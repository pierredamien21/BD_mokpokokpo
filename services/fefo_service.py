"""
Logique FEFO (First Expired First Out) 
Gestion des lots et allocation intelligente des stocks
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from models.model import Lot, Stock, Produit, LigneCommande
from typing import Optional, Tuple


class FEFOService:
    """Service pour gérer la logique FEFO (First Expired First Out)"""

    @staticmethod
    def get_lots_fefo_order(db: Session, id_produit: int) -> list[Lot]:
        """
        Récupère tous les lots du produit triés par FEFO
        (premièrement expirant d'abord)
        
        Args:
            db: Session SQLAlchemy
            id_produit: ID du produit
            
        Returns:
            Liste des lots triés par date_expiration ASC (lots qui expirent bientôt d'abord)
        """
        now = datetime.now()
        
        lots = db.query(Lot).filter(
            and_(
                Lot.id_produit == id_produit,
                Lot.quantite_restante > 0,  # Seulement lots avec stock
                Lot.date_expiration > now   # Seulement lots non expirés
            )
        ).order_by(Lot.date_expiration.asc()).all()
        
        return lots

    @staticmethod
    def get_lots_expired(db: Session, id_produit: int) -> list[Lot]:
        """
        Récupère les lots expirés d'un produit
        
        Args:
            db: Session SQLAlchemy
            id_produit: ID du produit
            
        Returns:
            Liste des lots expirés
        """
        now = datetime.now()
        
        lots_expired = db.query(Lot).filter(
            and_(
                Lot.id_produit == id_produit,
                Lot.date_expiration <= now,
                Lot.quantite_restante > 0  # Seulement les lots avec stock restant
            )
        ).all()
        
        return lots_expired

    @staticmethod
    def allocate_fefo(
        db: Session,
        id_produit: int,
        quantite_demandee: int
    ) -> Tuple[list[dict], bool, Optional[str]]:
        """
        Alloue la quantité demandée en suivant la stratégie FEFO
        
        Stratégie:
        1. Vérifier si le produit a du stock expiré → BLOQUER (erreur sanitaire)
        2. Récupérer tous les lots actifs triés par expiration croissante
        3. Déduire du premier lot jusqu'à épuisement
        4. Passer au lot suivant s'il reste à déduire
        5. Retourner la liste d'allocations [{'id_lot': X, 'quantite': Y}, ...]
        
        Args:
            db: Session SQLAlchemy
            id_produit: ID du produit
            quantite_demandee: Quantité à allouer
            
        Returns:
            Tuple (allocations, success, error_message)
            - allocations: list des lots utilisés avec quantités
            - success: True si allocation réussie, False sinon
            - error_message: Message d'erreur si échec
        """
        now = datetime.now()
        
        # 1. Vérifier si stock expiré existe
        lots_expired = FEFOService.get_lots_expired(db, id_produit)
        if lots_expired:
            expired_count = sum(lot.quantite_restante for lot in lots_expired)
            return (
                [],
                False,
                f"⚠️ ERREUR SANITAIRE: {expired_count} unités expirées détectées! "
                f"Impossible de traiter commande. Contactez gestionnaire stock."
            )
        
        # 2. Récupérer stocks actifs triés par FEFO
        lots_actifs = FEFOService.get_lots_fefo_order(db, id_produit)
        
        # 3. Vérifier si quantité totale disponible suffit
        quantite_totale = sum(lot.quantite_restante for lot in lots_actifs)
        if quantite_totale < quantite_demandee:
            return (
                [],
                False,
                f"Stock insuffisant: {quantite_totale} disponible, {quantite_demandee} demandée"
            )
        
        # 4. Allouer en suivant FEFO
        allocations = []
        quantite_restante = quantite_demandee
        
        for lot in lots_actifs:
            if quantite_restante <= 0:
                break
            
            # Prendre ce qu'on peut du lot courant
            quantite_du_lot = min(lot.quantite_restante, quantite_restante)
            
            allocations.append({
                "id_lot": lot.id_lot,
                "numero_lot": lot.numero_lot,
                "quantite": quantite_du_lot,
                "date_expiration": lot.date_expiration.isoformat(),
                "fournisseur": lot.fournisseur
            })
            
            quantite_restante -= quantite_du_lot
        
        return (allocations, True, None)

    @staticmethod
    def deduct_lots(
        db: Session,
        allocations: list[dict]
    ) -> bool:
        """
        Applique les déductions aux lots après validation commande
        
        Args:
            db: Session SQLAlchemy
            allocations: Liste [{'id_lot': X, 'quantite': Y}, ...]
            
        Returns:
            True si succès, False si erreur
        """
        for alloc in allocations:
            lot = db.get(Lot, alloc["id_lot"])
            if not lot:
                return False
            
            # Déduire la quantité
            lot.quantite_restante -= alloc["quantite"]
            if lot.quantite_restante < 0:
                lot.quantite_restante = 0
        
        db.commit()
        return True

    @staticmethod
    def get_lot_alert_status(lot: Lot) -> str:
        """
        Calcule le statut d'alerte d'un lot basé sur l'expiration
        
        Seuils:
        - ✅ VERT: > 90 jours
        - 🟡 JAUNE: 60-90 jours
        - 🟠 ORANGE: 30-60 jours
        - 🔴 ROUGE: 0-30 jours
        - ❌ EXPIRÉ: < 0 jours
        
        Args:
            lot: Instance du Lot
            
        Returns:
            Code statut: "VERT", "JAUNE", "ORANGE", "ROUGE", "EXPIRÉ"
        """
        now = datetime.now()
        jours = (lot.date_expiration - now).days
        
        if jours < 0:
            return "EXPIRÉ"
        elif jours <= 30:
            return "ROUGE"
        elif jours <= 60:
            return "ORANGE"
        elif jours <= 90:
            return "JAUNE"
        else:
            return "VERT"

    @staticmethod
    def get_jours_avant_expiration(lot: Lot) -> int:
        """Retourne le nombre de jours avant expiration (négatif si expiré)"""
        jours = (lot.date_expiration - datetime.now()).days
        return jours

    @staticmethod
    def get_all_lots_with_status(db: Session) -> list[dict]:
        """
        Récupère tous les lots avec leur statut d'alerte
        Utile pour tableau de bord gestionnaire stock
        
        Returns:
            Liste des lots avec statut, alerte, jours restants
        """
        lots = db.query(Lot).all()
        
        result = []
        for lot in lots:
            jours = FEFOService.get_jours_avant_expiration(lot)
            status = FEFOService.get_lot_alert_status(lot)
            
            result.append({
                "id_lot": lot.id_lot,
                "numero_lot": lot.numero_lot,
                "produit": lot.produit.nom_produit if lot.produit else "N/A",
                "fournisseur": lot.fournisseur,
                "quantite_restante": lot.quantite_restante,
                "quantite_initiale": lot.quantite_initiale,
                "date_expiration": lot.date_expiration.isoformat(),
                "jours_avant_expiration": jours,
                "statut_alerte": status,
                "disponible": lot.quantite_restante > 0 and jours >= 0
            })
        
        return sorted(result, key=lambda x: x["date_expiration"])

    @staticmethod
    def get_lots_by_product_with_status(db: Session, id_produit: int) -> list[dict]:
        """
        Récupère tous les lots d'un produit spécifique avec statut
        
        Args:
            db: Session SQLAlchemy
            id_produit: ID du produit
            
        Returns:
            Liste triée par date expiration (FEFO)
        """
        lots = db.query(Lot).filter(
            Lot.id_produit == id_produit
        ).order_by(Lot.date_expiration.asc()).all()
        
        result = []
        for lot in lots:
            jours = FEFOService.get_jours_avant_expiration(lot)
            status = FEFOService.get_lot_alert_status(lot)
            
            result.append({
                "id_lot": lot.id_lot,
                "numero_lot": lot.numero_lot,
                "quantite_restante": lot.quantite_restante,
                "quantite_initiale": lot.quantite_initiale,
                "date_expiration": lot.date_expiration.isoformat(),
                "date_fabrication": lot.date_fabrication.isoformat(),
                "fournisseur": lot.fournisseur,
                "jours_avant_expiration": jours,
                "statut_alerte": status,
                "disponible": lot.quantite_restante > 0 and jours >= 0
            })
        
        return result
