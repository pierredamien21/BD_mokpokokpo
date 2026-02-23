"""
Service pour gestion des alertes d'expiration des lots
Scan les lots et génère des alertes selon les seuils de proximité d'expiration
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.model import Lot, AlerteStock, Produit
from typing import List, Dict, Optional


class AlerteExpirationService:
    """Service pour gérer les alertes d'expiration intelligentes"""

    # Seuils d'alerte (en jours)
    SEUIL_JAUNE = 90      # J-90: Alerte jaune
    SEUIL_ORANGE = 60     # J-60: Alerte orange
    SEUIL_ROUGE = 30      # J-30: Alerte rouge
    SEUIL_EXPIRE = 0      # J≤0: Alerte expiré (CRITIQUE)

    @staticmethod
    def scanner_lots_expiration(db: Session) -> Dict[str, int]:
        """
        Scan tous les lots et génère les alertes d'expiration
        
        Stratégie:
        1. Récupérer tous les lots avec quantité restante > 0
        2. Pour chaque lot, calculer jours avant expiration
        3. Créer/mettre à jour alerte selon seuil
        4. Supprimer anciennes alertes si lot revient au vert
        
        Args:
            db: Session SQLAlchemy
            
        Returns:
            Dictionnaire avec compte d'alertes par type
        """
        now = datetime.now()
        stats = {
            "jaune": 0,
            "orange": 0,
            "rouge": 0,
            "expire": 0,
            "updated": 0,
            "deleted": 0
        }
        
        # Récupérer tous les lots avec stock
        lots = db.query(Lot).filter(Lot.quantite_restante > 0).all()
        
        for lot in lots:
            jours = (lot.date_expiration - now).days
            
            # Déterminer le type d'alerte
            type_alerte = None
            if jours < 0:
                type_alerte = "EXPIRÉ"
                stats["expire"] += 1
            elif jours <= AlerteExpirationService.SEUIL_ROUGE:
                type_alerte = "ROUGE"
                stats["rouge"] += 1
            elif jours <= AlerteExpirationService.SEUIL_ORANGE:
                type_alerte = "ORANGE"
                stats["orange"] += 1
            elif jours <= AlerteExpirationService.SEUIL_JAUNE:
                type_alerte = "JAUNE"
                stats["jaune"] += 1
            
            # Créer/mettre à jour l'alerte
            if type_alerte:
                # Vérifier si alerte existe déjà
                alerte_existante = db.query(AlerteStock).filter(
                    AlerteStock.id_lot == lot.id_lot,
                    AlerteStock.type_alerte == type_alerte
                ).first()
                
                if not alerte_existante:
                    # Supprimer les anciennes alertes pour ce lot
                    db.query(AlerteStock).filter(
                        AlerteStock.id_lot == lot.id_lot,
                        AlerteStock.type_alerte.in_(["JAUNE", "ORANGE", "ROUGE", "EXPIRÉ"])
                    ).delete()
                    stats["deleted"] += db.query(AlerteStock).filter(
                        AlerteStock.id_lot == lot.id_lot
                    ).count()
                    
                    # Créer nouvelle alerte
                    nouvelle_alerte = AlerteStock(
                        id_produit=lot.id_produit,
                        id_lot=lot.id_lot,
                        type_alerte=type_alerte,
                        date_creation=now
                    )
                    db.add(nouvelle_alerte)
                    stats["updated"] += 1
        
        # Commit
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"Erreur lors du scan d'alerte: {str(e)}")
        
        return stats

    @staticmethod
    def get_alertes_expirations(
        db: Session,
        type_alerte: Optional[str] = None,
        id_produit: Optional[int] = None
    ) -> List[Dict]:
        """
        Récupère les alertes d'expiration
        
        Args:
            db: Session SQLAlchemy
            type_alerte: Filtrer par type (JAUNE, ORANGE, ROUGE, EXPIRÉ)
            id_produit: Filtrer par produit
            
        Returns:
            Liste des alertes avec détails lot + produit
        """
        query = db.query(AlerteStock).filter(
            AlerteStock.type_alerte.in_(["JAUNE", "ORANGE", "ROUGE", "EXPIRÉ"])
        )
        
        if type_alerte:
            query = query.filter(AlerteStock.type_alerte == type_alerte)
        
        if id_produit:
            query = query.filter(AlerteStock.id_produit == id_produit)
        
        alertes = query.all()
        
        # Enrichir avec infos lot + produit
        result = []
        for alerte in alertes:
            lot = db.get(Lot, alerte.id_lot) if alerte.id_lot else None
            produit = db.get(Produit, alerte.id_produit)
            
            if lot:
                jours = (lot.date_expiration - datetime.now()).days
                result.append({
                    "id_alerte": alerte.id_alerte,
                    "type_alerte": alerte.type_alerte,
                    "id_lot": lot.id_lot,
                    "numero_lot": lot.numero_lot,
                    "id_produit": produit.id_produit,
                    "nom_produit": produit.nom_produit,
                    "fournisseur": lot.fournisseur,
                    "quantite_restante": lot.quantite_restante,
                    "date_expiration": lot.date_expiration.isoformat(),
                    "jours_avant_expiration": jours,
                    "date_alerte": alerte.date_creation.isoformat() if alerte.date_creation else None,
                    "criticite": AlerteExpirationService._get_criticite(jours)
                })
        
        # Trier par criticité (expiré d'abord)
        ordre = {"EXPIRÉ": 0, "ROUGE": 1, "ORANGE": 2, "JAUNE": 3}
        result.sort(key=lambda x: ordre.get(x["type_alerte"], 4))
        
        return result

    @staticmethod
    def get_alertes_dashboard(db: Session) -> Dict:
        """
        Récupère les statistiques des alertes pour le dashboard
        
        Returns:
            Dictionnaire avec résumé des alertes par type + sévérité
        """
        now = datetime.now()
        
        # Compter les alertes par type
        stats = {
            "total_alertes": 0,
            "par_type": {
                "expiré": 0,
                "rouge": 0,
                "orange": 0,
                "jaune": 0
            },
            "par_produit": {},
            "quantite_en_risque": 0,
            "quantite_expirée": 0,
            "produits_critiques": []
        }
        
        alertes = db.query(AlerteStock).filter(
            AlerteStock.type_alerte.in_(["JAUNE", "ORANGE", "ROUGE", "EXPIRÉ"])
        ).all()
        
        stats["total_alertes"] = len(alertes)
        
        for alerte in alertes:
            lot = db.get(Lot, alerte.id_lot) if alerte.id_lot else None
            produit = db.get(Produit, alerte.id_produit)
            
            if not lot:
                continue
            
            # Compter par type
            type_lower = alerte.type_alerte.lower()
            if type_lower == "expiré":
                stats["par_type"]["expiré"] += lot.quantite_restante
                stats["quantite_expirée"] += lot.quantite_restante
            else:
                stats["par_type"][type_lower] += lot.quantite_restante
                stats["quantite_en_risque"] += lot.quantite_restante
            
            # Compter par produit
            produit_nom = produit.nom_produit
            if produit_nom not in stats["par_produit"]:
                stats["par_produit"][produit_nom] = {
                    "id_produit": produit.id_produit,
                    "count": 0,
                    "quantite": 0,
                    "types": set()
                }
            
            stats["par_produit"][produit_nom]["count"] += 1
            stats["par_produit"][produit_nom]["quantite"] += lot.quantite_restante
            stats["par_produit"][produit_nom]["types"].add(alerte.type_alerte)
        
        # Identifier produits critiques (EXPIRÉ ou ROUGE)
        stats["produits_critiques"] = [
            {
                "nom_produit": nom,
                "id_produit": info["id_produit"],
                "alertes_count": info["count"],
                "quantite": info["quantite"],
                "types": sorted(info["types"])
            }
            for nom, info in stats["par_produit"].items()
            if "EXPIRÉ" in info["types"] or "ROUGE" in info["types"]
        ]
        
        # Convertir les sets en lists pour JSON
        stats["par_produit"] = {
            nom: {**info, "types": list(info["types"])}
            for nom, info in stats["par_produit"].items()
        }
        
        return stats

    @staticmethod
    def _get_criticite(jours: int) -> str:
        """
        Détermine le niveau de criticité basé sur les jours avant expiration
        """
        if jours < 0:
            return "🔴 CRITIQUE - EXPIRÉ"
        elif jours <= 30:
            return "🔴 CRITIQUE - Expire bientôt"
        elif jours <= 60:
            return "🟠 ÉLEVÉE - Attention"
        elif jours <= 90:
            return "🟡 MODÉRÉE - À surveiller"
        else:
            return "✅ NORMAL"

    @staticmethod
    def nettoyer_alertes_obsolètes(db: Session) -> int:
        """
        Supprime les alertes pour les lots qui ne sont plus en alerte
        (expiration > J+90)
        
        Returns:
            Nombre d'alertes supprimées
        """
        now = datetime.now()
        seuil = now + timedelta(days=AlerteExpirationService.SEUIL_JAUNE)
        
        # Récupérer les alertes pour les lots qui ne sont plus en danger
        alertes_a_supprimer = db.query(AlerteStock).join(
            Lot, AlerteStock.id_lot == Lot.id_lot
        ).filter(
            AlerteStock.type_alerte.in_(["JAUNE", "ORANGE", "ROUGE", "EXPIRÉ"]),
            Lot.date_expiration > seuil
        ).all()
        
        count = len(alertes_a_supprimer)
        for alerte in alertes_a_supprimer:
            db.delete(alerte)
        
        db.commit()
        return count
