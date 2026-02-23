"""
Schémas Pydantic pour Livraison (Delivery Management)
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class LivraisonBase(BaseModel):
    numero_livraison: str = Field(..., min_length=1, max_length=50, description="Numéro unique de livraison")
    adresse_livraison: Optional[str] = Field(None, max_length=500, description="Adresse complète de livraison")
    transporteur: Optional[str] = Field(None, max_length=100, description="Nom du transporteur")
    numero_suivi: Optional[str] = Field(None, max_length=100, description="Numéro de suivi colis")
    notes: Optional[str] = Field(None, description="Notes ou instructions spéciales")


class LivraisonCreate(BaseModel):
    id_commande: int = Field(..., description="ID de la commande associée")


class LivraisonUpdate(BaseModel):
    statut: Optional[str] = Field(None, description="PREPARATION, PRETE, EN_LIVRAISON, LIVRÉE")
    adresse_livraison: Optional[str] = Field(None)
    transporteur: Optional[str] = Field(None)
    numero_suivi: Optional[str] = Field(None)
    notes: Optional[str] = Field(None)
    date_preparation: Optional[datetime] = Field(None, description="Quand le colis a été préparé")
    date_expedition: Optional[datetime] = Field(None, description="Quand le colis a été expédié")
    date_livraison: Optional[datetime] = Field(None, description="Quand le colis a été livré")


class LivraisonRead(LivraisonBase):
    id_livraison: int
    id_commande: int
    statut: str
    date_creation: datetime
    date_preparation: Optional[datetime]
    date_expedition: Optional[datetime]
    date_livraison: Optional[datetime]

    class Config:
        from_attributes = True


class LivraisonDetailRead(LivraisonRead):
    """Livraison détaillée avec infos commande"""
    jours_preparation: Optional[int] = Field(None, description="Jours pour préparer")
    jours_expedition: Optional[int] = Field(None, description="Jours en transit")
    jours_total: Optional[int] = Field(None, description="Jours totaux")
    statut_visuel: str = Field(..., description="🟡 EN_PREPARATION, 🟠 PRETE, 🟢 EN_LIVRAISON, ✅ LIVRÉE")

    class Config:
        from_attributes = True


class LivraisonListResponse(BaseModel):
    total: int
    livraisons: list[LivraisonRead]
    filtre_statut: Optional[str] = None
    filtre_commande_id: Optional[int] = None


class LivraisonStatusUpdate(BaseModel):
    """Mise à jour simple du statut"""
    nouveau_statut: str = Field(..., description="EN_PREPARATION, PRETE, EN_LIVRAISON, ou LIVRÉE")
    notes: Optional[str] = Field(None, description="Notes additionnelles")
