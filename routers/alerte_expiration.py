"""
Router pour gestion des alertes d'expiration des lots
Endpoints pour scanner, consulter et gérer les alertes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models.model import Utilisateur
from services.alerte_expiration_service import AlerteExpirationService
from schema.enums import RoleEnum
from security.dependencies import get_current_user

router = APIRouter(
    prefix="/alertes",
    tags=["Alertes Expiration"]
)


# =====================================================
# 📊 SCANNER - Déclencher scan manuel
# =====================================================
@router.post("/scanner")
def scanner_alertes_manuel(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    🔍 Scanner manuel les lots et générer les alertes d'expiration
    
    **Permissions**: ADMIN, GEST_STOCK
    
    **Processus**:
    1. Récupère tous les lots avec quantité restante > 0
    2. Calcule jours avant expiration
    3. Crée/met à jour alertes selon seuils (J-90, J-60, J-30, J≤0)
    4. Supprime les anciennes alertes si lot revient au vert
    
    **Retourne**: Stats sur les alertes créées par type
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    try:
        stats = AlerteExpirationService.scanner_lots_expiration(db)
        
        return {
            "message": "✅ Scan des alertes d'expiration complété",
            "timestamp": datetime.now().isoformat(),
            "resultats": {
                "alertes_jaune_creees": stats["jaune"],
                "alertes_orange_creees": stats["orange"],
                "alertes_rouge_creees": stats["rouge"],
                "alertes_expirees_creees": stats["expire"],
                "total_mises_a_jour": stats["updated"],
                "anciennes_alertes_supprimees": stats["deleted"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur scan: {str(e)}")


# =====================================================
# 📖 LIRE - Consulter les alertes
# =====================================================
@router.get("/expirations")
def get_alertes_expirations(
    type_alerte: str = None,  # JAUNE, ORANGE, ROUGE, EXPIRÉ
    id_produit: int = None,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    📋 Lister les alertes d'expiration des lots
    
    **Permissions**: ADMIN, GEST_STOCK, GEST_COMMERCIAL
    
    **Filtres optionnels**:
    - type_alerte: JAUNE (J-90), ORANGE (J-60), ROUGE (J-30), EXPIRÉ (J≤0)
    - id_produit: Limiter à un produit spécifique
    
    **Retourne**: Liste des alertes triée par criticité (expiré → jaune)
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    alertes = AlerteExpirationService.get_alertes_expirations(
        db,
        type_alerte=type_alerte,
        id_produit=id_produit
    )
    
    return {
        "total": len(alertes),
        "filtres": {
            "type_alerte": type_alerte,
            "id_produit": id_produit
        },
        "alertes": alertes
    }


# =====================================================
# 📊 DASHBOARD - Vue d'ensemble
# =====================================================
@router.get("/dashboard")
def get_alertes_dashboard(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    📊 Tableau de bord des alertes d'expiration
    
    **Permissions**: ADMIN, GEST_STOCK
    
    **Affiche**:
    - Nombre total d'alertes par type
    - Quantité en risque / expirée
    - Produits critiques (avec alertes ROUGE ou EXPIRÉ)
    - Recommandations d'action
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    stats = AlerteExpirationService.get_alertes_dashboard(db)
    
    # Ajouter recommandations
    recommandations = []
    
    if stats["quantite_expirée"] > 0:
        recommandations.append({
            "severity": "🔴 CRITIQUE",
            "action": "Déchets à traiter",
            "details": f"{stats['quantite_expirée']} unités expirées à éliminer immédiatement"
        })
    
    if stats["par_type"]["rouge"] > 0:
        recommandations.append({
            "severity": "🔴 URGENT",
            "action": "Prioriser les ventes",
            "details": f"{stats['par_type']['rouge']} unités expirent dans ≤ 30 jours"
        })
    
    if stats["par_type"]["orange"] > 0:
        recommandations.append({
            "severity": "🟠 IMPORTANT",
            "action": "Planifier les ventes",
            "details": f"{stats['par_type']['orange']} unités expirent dans 30-60 jours"
        })
    
    if stats["par_type"]["jaune"] > 0:
        recommandations.append({
            "severity": "🟡 ATTENTION",
            "action": "Surveiller",
            "details": f"{stats['par_type']['jaune']} unités expirent dans 60-90 jours"
        })
    
    if len(recommandations) == 0:
        recommandations.append({
            "severity": "✅ NORMAL",
            "action": "Aucune action requise",
            "details": "Tous les lots sont en bon état"
        })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "resume": {
            "total_alertes": stats["total_alertes"],
            "quantite_en_risque": stats["quantite_en_risque"],
            "quantite_expirée": stats["quantite_expirée"]
        },
        "par_type": {
            "expiré": stats["par_type"]["expiré"],
            "rouge": stats["par_type"]["rouge"],
            "orange": stats["par_type"]["orange"],
            "jaune": stats["par_type"]["jaune"]
        },
        "produits_critiques": stats["produits_critiques"],
        "recommandations": recommandations
    }


# =====================================================
# 🧹 NETTOYAGE - Supprimer alertes obsolètes
# =====================================================
@router.post("/nettoyer")
def nettoyer_alertes_obsoletes(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    🧹 Nettoyer les alertes pour les lots qui ne sont plus en danger
    
    **Permissions**: ADMIN, GEST_STOCK
    
    **Supprime**: Alertes pour les lots expirant à > J+90
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    try:
        count = AlerteExpirationService.nettoyer_alertes_obsolètes(db)
        
        return {
            "message": "✅ Nettoyage complété",
            "alertes_supprimees": count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur nettoyage: {str(e)}")
