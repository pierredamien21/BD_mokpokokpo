from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class ProduitBase(BaseModel):
    nom_produit: str
    type_produit: Optional[str] = None
    description: Optional[str] = None
    usages: Optional[str] = None
    prix_unitaire: Decimal

class ProduitCreate(ProduitBase):
    pass

class ProduitRead(ProduitBase):
    id_produit: int

    class Config:
        from_attributes = True
