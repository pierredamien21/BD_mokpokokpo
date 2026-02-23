"""
Router pour gestion des livraisons (Delivery Management)
Endpoints pour créer, consulter, et tracker les livraisons
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import desc

from database import get_db
from models.model import Livraison, Commande, Utilisateur
from schema.livraison import (
    LivraisonCreate, LivraisonRead, LivraisonUpdate, 
    LivraisonDetailRead, LivraisonStatusUpdate
)
from schema.enums import RoleEnum, StatutCommandeEnum
from security.dependencies import get_current_user
from services.pdf_service import PDFService

router = APIRouter(
    prefix="/livraisons",
    tags=["Livraisons (Delivery Management)"]
)


# =====================================================
# 📝 CREATE - Créer une livraison
# =====================================================
@router.post("/", response_model=LivraisonRead, status_code=201)
def create_livraison(
    data: LivraisonCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    📦 Créer une nouvelle livraison
    
    **Permissions**: GEST_COMMERCIAL, ADMIN
    
    **Processus**:
    1. Vérifier que commande existe et est ACCEPTEE
    2. Vérifier qu'aucune livraison n'existe pour cette commande
    3. Créer la livraison avec statut EN_PREPARATION
    
    **Retourne**: Livraison créée
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    # Vérifier commande existe et est acceptée
    commande = db.get(Commande, data.id_commande)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    if commande.statut != StatutCommandeEnum.ACCEPTEE:
        raise HTTPException(
            status_code=400,
            detail=f"Commande doit être ACCEPTEE pour créer une livraison (statut actuel: {commande.statut})"
        )
    
    # Vérifier qu'une livraison n'existe pas déjà
    livraison_existante = db.query(Livraison).filter(
        Livraison.id_commande == data.id_commande
    ).first()
    
    if livraison_existante:
        raise HTTPException(
            status_code=400,
            detail=f"Une livraison existe déjà pour cette commande (ID: {livraison_existante.id_livraison})"
        )
    
    # Générer numéro de livraison
    numero = f"LIV-{datetime.now().strftime('%Y%m%d')}-{commande.id_commande}"
    
    # Créer livraison
    livraison = Livraison(
        numero_livraison=numero,
        id_commande=data.id_commande,
        statut="EN_PREPARATION",
        adresse_livraison=None,
        transporteur=None,
        numero_suivi=None
    )
    
    try:
        db.add(livraison)
        db.commit()
        db.refresh(livraison)
        return livraison
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur création livraison: {str(e)}")


# =====================================================
# 📖 READ - Consulter les livraisons
# =====================================================
@router.get("/", response_model=list[LivraisonRead])
def get_livraisons(
    statut: str = None,
    id_commande: int = None,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    📋 Lister les livraisons
    
    **Permissions**: ADMIN, GEST_COMMERCIAL
    
    **Filtres optionnels**:
    - statut: EN_PREPARATION, PRETE, EN_LIVRAISON, LIVRÉE
    - id_commande: Limiter à une commande spécifique
    
    **Retourne**: Liste des livraisons triée par date (plus récentes d'abord)
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    query = db.query(Livraison)
    
    if statut:
        query = query.filter(Livraison.statut == statut)
    
    if id_commande:
        query = query.filter(Livraison.id_commande == id_commande)
    
    livraisons = query.order_by(desc(Livraison.date_creation)).all()
    return livraisons


@router.get("/{id_livraison}", response_model=LivraisonDetailRead)
def get_livraison(
    id_livraison: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    📄 Consulter une livraison spécifique avec détails
    
    **Permissions**: ADMIN, GEST_COMMERCIAL
    
    **Retourne**: Livraison avec calculs de durées (jours)
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    livraison = db.get(Livraison, id_livraison)
    if not livraison:
        raise HTTPException(status_code=404, detail="Livraison non trouvée")
    
    # Calculer les durées
    now = datetime.now()
    jours_preparation = None
    jours_expedition = None
    jours_total = None
    
    if livraison.date_preparation:
        jours_preparation = (livraison.date_preparation - livraison.date_creation).days
    
    if livraison.date_expedition and livraison.date_preparation:
        jours_expedition = (livraison.date_expedition - livraison.date_preparation).days
    
    if livraison.date_livraison:
        jours_total = (livraison.date_livraison - livraison.date_creation).days
    
    # Déterminer le statut visuel
    statut_visuel_map = {
        "EN_PREPARATION": "🟡 EN_PREPARATION",
        "PRETE": "🟠 PRETE",
        "EN_LIVRAISON": "🟢 EN_LIVRAISON",
        "LIVRÉE": "✅ LIVRÉE"
    }
    
    return LivraisonDetailRead(
        **livraison.__dict__,
        jours_preparation=jours_preparation,
        jours_expedition=jours_expedition,
        jours_total=jours_total,
        statut_visuel=statut_visuel_map.get(livraison.statut, "❓ INCONNU")
    )


# =====================================================
# ✏️ UPDATE - Mettre à jour le statut
# =====================================================
@router.put("/{id_livraison}/statut", response_model=LivraisonRead)
def update_livraison_statut(
    id_livraison: int,
    data: LivraisonStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    ✏️ Mettre à jour le statut d'une livraison
    
    **Permissions**: ADMIN, GEST_COMMERCIAL
    
    **Statuts valides**: EN_PREPARATION → PRETE → EN_LIVRAISON → LIVRÉE
    
    **Processus**:
    1. Vérifier transition de statut valide
    2. Enregistrer les timestamps appropriés
    3. Mettre à jour la livraison
    
    **Retourne**: Livraison mise à jour
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    livraison = db.get(Livraison, id_livraison)
    if not livraison:
        raise HTTPException(status_code=404, detail="Livraison non trouvée")
    
    # Vérifier transition valide
    transitions_valides = {
        "EN_PREPARATION": ["PRETE", "EN_LIVRAISON"],
        "PRETE": ["EN_LIVRAISON"],
        "EN_LIVRAISON": ["LIVRÉE"],
        "LIVRÉE": []  # Pas de transition depuis LIVRÉE
    }
    
    nouveau_statut = data.nouveau_statut.upper()
    
    if nouveau_statut not in transitions_valides.get(livraison.statut, []):
        raise HTTPException(
            status_code=400,
            detail=f"Transition invalide: {livraison.statut} → {nouveau_statut}. "
                   f"Transitions valides: {transitions_valides.get(livraison.statut, [])}"
        )
    
    # Enregistrer les timestamps selon le statut
    now = datetime.now()
    
    if nouveau_statut == "PRETE":
        livraison.date_preparation = now
    elif nouveau_statut == "EN_LIVRAISON":
        livraison.date_expedition = now
    elif nouveau_statut == "LIVRÉE":
        livraison.date_livraison = now
    
    livraison.statut = nouveau_statut
    
    if data.notes:
        livraison.notes = (livraison.notes or "") + f"\n[{now.strftime('%Y-%m-%d %H:%M')}] {data.notes}"
    
    try:
        db.add(livraison)
        db.commit()
        db.refresh(livraison)
        return livraison
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur mise à jour: {str(e)}")


@router.put("/{id_livraison}", response_model=LivraisonRead)
def update_livraison(
    id_livraison: int,
    data: LivraisonUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    ✏️ Mettre à jour les détails d'une livraison
    
    **Permissions**: ADMIN, GEST_COMMERCIAL
    
    **Modifiable**: Adresse, transporteur, numéro de suivi, notes
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    livraison = db.get(Livraison, id_livraison)
    if not livraison:
        raise HTTPException(status_code=404, detail="Livraison non trouvée")
    
    # Mise à jour des champs optionnels
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(livraison, field, value)
    
    try:
        db.add(livraison)
        db.commit()
        db.refresh(livraison)
        return livraison
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur mise à jour: {str(e)}")


# =====================================================
# 📊 DASHBOARD - Vue d'ensemble
# =====================================================
@router.get("/dashboard/stats")
def get_livraisons_dashboard(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    📊 Tableau de bord des livraisons
    
    **Permissions**: ADMIN, GEST_COMMERCIAL
    
    **Affiche**:
    - Nombre de livraisons par statut
    - Temps moyen par étape
    - Livraisons critiques (retardées)
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    now = datetime.now()
    
    # Compter par statut
    total_en_prep = db.query(Livraison).filter(Livraison.statut == "EN_PREPARATION").count()
    total_prete = db.query(Livraison).filter(Livraison.statut == "PRETE").count()
    total_en_livraison = db.query(Livraison).filter(Livraison.statut == "EN_LIVRAISON").count()
    total_livree = db.query(Livraison).filter(Livraison.statut == "LIVRÉE").count()
    
    # Livraisons trop longues
    livraisons_longues = db.query(Livraison).filter(
        Livraison.statut.in_(["EN_PREPARATION", "PRETE", "EN_LIVRAISON"]),
        (now - Livraison.date_creation).between(3 * 86400, 999999999)  # > 3 jours
    ).all()
    
    return {
        "timestamp": now.isoformat(),
        "par_statut": {
            "en_preparation": total_en_prep,
            "prete": total_prete,
            "en_livraison": total_en_livraison,
            "livree": total_livree
        },
        "total_en_cours": total_en_prep + total_prete + total_en_livraison,
        "total_livrees": total_livree,
        "livraisons_potentiellement_retardees": len(livraisons_longues),
        "alerte_critique": len(livraisons_longues) > 0
    }


@router.get("/{id_livraison}/bon-livraison-pdf")
def download_bon_livraison(
    id_livraison: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Télécharger le bon de livraison en PDF
    
    **Permissions**: ADMIN, GEST_COMMERCIAL (et CLIENT sa propre livraison)
    
    Génère un PDF professionnel avec:
    - Informations de livraison et commande
    - Adresse et transporteur
    - Liste des produits
    - État et dates d'avancement
    """
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL, RoleEnum.CLIENT]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    livraison = db.query(Livraison).filter(Livraison.id_livraison == id_livraison).first()
    if not livraison:
        raise HTTPException(status_code=404, detail="Livraison introuvable")
    
    # Vérification: CLIENT ne peut accéder qu'à ses propres livraisons
    if current_user.role == RoleEnum.CLIENT:
        commande = livraison.commande
        if commande.id_client != current_user.id_utilisateur:
            raise HTTPException(status_code=403, detail="Vous n'avez pas accès à cette livraison")
    
    try:
        pdf_buffer = PDFService.generate_bon_livraison(id_livraison)
        filename = f"bon-livraison-{livraison.numero_livraison}.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération PDF: {str(e)}")
