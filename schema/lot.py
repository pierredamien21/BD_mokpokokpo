from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal

# =====================================================
# LOT / BATCH TRACKING (FEFO)
# =====================================================

class LotBase(BaseModel):
    numero_lot: str = Field(..., min_length=1, max_length=50, description="Numéro unique du lot")
    date_fabrication: datetime = Field(..., description="Date de fabrication du lot")
    date_expiration: datetime = Field(..., description="Date d'expiration du lot")
    quantite_initiale: int = Field(..., gt=0, description="Quantité initiale du lot")
    quantite_restante: int = Field(..., ge=0, description="Quantité restante disponible")
    fournisseur: Optional[str] = Field(None, max_length=150, description="Nom du fournisseur")
    id_produit: int = Field(..., description="ID du produit")
    id_stock: int = Field(..., description="ID du stock")


class LotCreate(LotBase):
    """Schéma pour créer un nouveau lot"""
    pass


class LotUpdate(BaseModel):
    """Schéma pour mettre à jour un lot"""
    quantite_restante: Optional[int] = Field(None, ge=0, description="Nouvelle quantité restante")
    fournisseur: Optional[str] = Field(None, max_length=150)
    numero_lot: Optional[str] = Field(None, min_length=1, max_length=50)
    date_fabrication: Optional[datetime] = None
    date_expiration: Optional[datetime] = None


class LotRead(LotBase):
    """Schéma pour afficher un lot"""
    id_lot: int
    date_creation: datetime
    
    class Config:
        from_attributes = True


class LotDetailRead(LotRead):
    """Schéma détaillé avec infos de stock et produit"""
    jours_avant_expiration: Optional[int] = Field(None, description="Jours avant expiration (peut être négatif si expiré)")
    statut_alerte: Optional[str] = Field(None, description="VERT ✅, JAUNE ⚠️, ORANGE 🟠, ROUGE 🔴, EXPIRÉ ❌")
    disponible: bool = Field(True, description="True si quantité_restante > 0 et non expiré")

    class Config:
        from_attributes = True


class LotListResponse(BaseModel):
    """Réponse paginated pour liste des lots"""
    total: int
    lots: list[LotRead]
    filtre_produit_id: Optional[int] = None
    filtre_actif_seulement: bool = True


class LotFEFOInfo(BaseModel):
    """Info pour sélection FEFO (First Expired First Out)"""
    id_lot: int
    numero_lot: str
    quantite_disponible: int
    date_expiration: datetime
    jours_avant_expiration: int
    sera_utilise: bool = False  # True si ce lot sera utilisé pour la commande

    class Config:
        from_attributes = True
