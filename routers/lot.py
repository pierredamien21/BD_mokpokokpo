"""
Router pour gestion des LOTS (Batch Tracking - FEFO)
Endpoints pour créer, consulter, mettre à jour les lots
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.model import Lot, Produit, Stock, Utilisateur
from schema.lot import LotCreate, LotRead, LotUpdate, LotDetailRead, LotFEFOInfo
from security.dependencies import get_current_user
from services.fefo_service import FEFOService
from schema.enums import RoleEnum
from datetime import datetime

router = APIRouter(
    prefix="/lots",
    tags=["Lots (Batch Tracking)"]
)


# =====================================================
# 📝 CREATE - Créer un nouveau lot
# =====================================================
@router.post("/", response_model=LotRead, status_code=201)
def create_lot(
    data: LotCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    ✅ Créer un nouveau lot
    
    **Permissions**: ADMIN, GEST_STOCK
    
    **Données requises**:
    - numero_lot: Numéro unique du lot (ex: LOT-2026-001)
    - date_fabrication: Date de production
    - date_expiration: Date d'expiration
    - quantite_initiale: Quantité totale du lot
    - id_produit: ID du produit
    - id_stock: ID du stock
    - fournisseur (optionnel): Nom du fournisseur
    """
    
    # Vérification permissions
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    # Vérifier que produit existe
    produit = db.get(Produit, data.id_produit)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Vérifier que stock existe et appartient au produit
    stock = db.get(Stock, data.id_stock)
    if not stock or stock.id_produit != data.id_produit:
        raise HTTPException(status_code=404, detail="Stock non trouvé pour ce produit")
    
    # Validation dates
    if data.date_fabrication > data.date_expiration:
        raise HTTPException(
            status_code=400,
            detail="Date fabrication ne peut pas être après date expiration"
        )
    
    # Créer le lot
    lot = Lot(
        **data.model_dump()
    )
    
    try:
        db.add(lot)
        db.commit()
        db.refresh(lot)
        return lot
    except IntegrityError as e:
        db.rollback()
        if "uq_lot_numero_produit" in str(e):
            raise HTTPException(
                status_code=400,
                detail=f"Lot avec numéro '{data.numero_lot}' existe déjà pour ce produit"
            )
        raise HTTPException(status_code=400, detail="Erreur création lot")


# =====================================================
# 📖 READ - Consulter les lots
# =====================================================
@router.get("/", response_model=list[LotDetailRead])
def get_lots(
    id_produit: int = Query(None, description="Filtrer par ID produit"),
    actifs_seulement: bool = Query(True, description="Seulement lots actifs (non expirés)"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    📊 Lister les lots
    
    **Permissions**: ADMIN, GEST_STOCK, GEST_COMMERCIAL
    
    **Filtres optionnels**:
    - id_produit: Limiter à un produit spécifique
    - actifs_seulement: true = seulement lots non expirés (défaut: true)
    
    **Retourne**: Liste des lots triée par date expiration (FEFO)
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    query = db.query(Lot)
    
    if id_produit:
        query = query.filter(Lot.id_produit == id_produit)
    
    if actifs_seulement:
        now = datetime.now()
        query = query.filter(
            (Lot.date_expiration > now) &
            (Lot.quantite_restante > 0)
        )
    
    lots = query.order_by(Lot.date_expiration.asc()).all()
    
    # Enrichir avec info d'alerte
    result = []
    for lot in lots:
        jours = FEFOService.get_jours_avant_expiration(lot)
        status = FEFOService.get_lot_alert_status(lot)
        
        result.append(LotDetailRead(
            **{**lot.__dict__, 
               "jours_avant_expiration": jours,
               "statut_alerte": status,
               "disponible": lot.quantite_restante > 0 and jours >= 0
            }
        ))
    
    return result


@router.get("/{id_lot}", response_model=LotDetailRead)
def get_lot(
    id_lot: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    📄 Consulter un lot spécifique
    
    **Permissions**: ADMIN, GEST_STOCK, GEST_COMMERCIAL
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    lot = db.get(Lot, id_lot)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot non trouvé")
    
    jours = FEFOService.get_jours_avant_expiration(lot)
    status = FEFOService.get_lot_alert_status(lot)
    
    return LotDetailRead(
        **{**lot.__dict__,
           "jours_avant_expiration": jours,
           "statut_alerte": status,
           "disponible": lot.quantite_restante > 0 and jours >= 0
        }
    )


# =====================================================
# 📊 DASHBOARD - Alertes et statut
# =====================================================
@router.get("/dashboard/resumé", response_model=dict, tags=["Dashboard"])
def get_lots_resume(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    📊 Résumé des lots pour tableau de bord gestionnaire stock
    
    **Permissions**: ADMIN, GEST_STOCK
    
    **Retourne**: Statistiques globales sur les lots
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    now = datetime.now()
    
    # Récupérer tous les lots
    all_lots = db.query(Lot).all()
    
    # Statistiques
    total_lots = len(all_lots)
    lots_expirés = [l for l in all_lots if l.date_expiration <= now]
    lots_rouges = [l for l in all_lots if 0 <= (l.date_expiration - now).days <= 30]
    lots_oranges = [l for l in all_lots if 30 < (l.date_expiration - now).days <= 60]
    lots_jaunes = [l for l in all_lots if 60 < (l.date_expiration - now).days <= 90]
    
    quantite_totale_stock = sum(l.quantite_restante for l in all_lots if l.date_expiration > now)
    quantite_expirée = sum(l.quantite_restante for l in lots_expirés)
    quantite_risque = sum(l.quantite_restante for l in lots_rouges + lots_oranges)
    
    return {
        "total_lots": total_lots,
        "statistiques": {
            "vert": len([l for l in all_lots if FEFOService.get_lot_alert_status(l) == "VERT"]),
            "jaune": len(lots_jaunes),
            "orange": len(lots_oranges),
            "rouge": len(lots_rouges),
            "expiré": len(lots_expirés)
        },
        "quantites": {
            "stock_sain": quantite_totale_stock,
            "stock_risque": quantite_risque,  # Orange + Rouge
            "stock_expiré": quantite_expirée
        },
        "alertes": {
            "critique": quantite_expirée > 0,  # ⚠️ Stock expiré = CRITIQUE
            "attention": quantite_risque > 0   # ⚠️ Stock expire bientôt
        }
    }


# =====================================================
# ✏️ UPDATE - Mettre à jour un lot
# =====================================================
@router.put("/{id_lot}", response_model=LotRead)
def update_lot(
    id_lot: int,
    data: LotUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    ✏️ Mettre à jour un lot
    
    **Permissions**: ADMIN, GEST_STOCK
    
    **Champs modifiables**:
    - quantite_restante: Ajuster stock (ex: correction inventory)
    - fournisseur: Modifier fournisseur
    - numero_lot: Corriger numéro
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    lot = db.get(Lot, id_lot)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot non trouvé")
    
    # Validation: quantite_restante ne peut pas dépasser quantite_initiale
    if data.quantite_restante is not None and data.quantite_restante > lot.quantite_initiale:
        raise HTTPException(
            status_code=400,
            detail=f"Quantité restante ({data.quantite_restante}) ne peut pas dépasser quantité initiale ({lot.quantite_initiale})"
        )
    
    # Mise à jour
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lot, field, value)
    
    try:
        db.add(lot)
        db.commit()
        db.refresh(lot)
        return lot
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erreur mise à jour lot")


# =====================================================
# 🗑️ DELETE - Supprimer un lot
# =====================================================
@router.delete("/{id_lot}", status_code=204)
def delete_lot(
    id_lot: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    🗑️ Supprimer un lot
    
    **Permissions**: ADMIN, GEST_STOCK
    
    **Garde-fou**: Impossible de supprimer un lot avec:
    - Quantité restante = 0 (lot épuisé) - DÉJÀ TERMINÉ
    - Lignes de commande associées (lot utilisé par commande)
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    lot = db.get(Lot, id_lot)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot non trouvé")
    
    # Garde-fou: Vérifier s'il y a des lignes de commande associées
    if lot.lignes_commande:
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer: Ce lot a des lignes de commande associées"
        )
    
    try:
        db.delete(lot)
        db.commit()
        return {"message": "Lot supprimé avec succès"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erreur suppression lot")


# =====================================================
# 🎯 FEFO LOGIC - Allocation intelligente
# =====================================================
@router.get("/fefo/{id_produit}/allocate", response_model=list[LotFEFOInfo])
def get_fefo_allocation(
    id_produit: int,
    quantite_demandee: int = Query(..., gt=0, description="Quantité à allouer"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    🎯 Simule allocation FEFO sans la valider
    
    **Permissions**: ADMIN, GEST_STOCK, GEST_COMMERCIAL
    
    **Utile pour**: Prévisualiser quel lot serait utilisé
    
    **Retourne**: Liste des lots qui seraient utilisés, dans l'ordre
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    # Vérifier produit existe
    produit = db.get(Produit, id_produit)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Allocation FEFO
    allocations, success, error = FEFOService.allocate_fefo(db, id_produit, quantite_demandee)
    
    if not success:
        raise HTTPException(status_code=400, detail=error)
    
    # Convertir allocations en LotFEFOInfo
    result = []
    for alloc in allocations:
        lot = db.get(Lot, alloc["id_lot"])
        result.append(LotFEFOInfo(
            id_lot=lot.id_lot,
            numero_lot=lot.numero_lot,
            quantite_disponible=alloc["quantite"],
            date_expiration=lot.date_expiration,
            jours_avant_expiration=FEFOService.get_jours_avant_expiration(lot),
            sera_utilise=True
        ))
    
    return result
