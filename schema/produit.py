from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional

class ProduitBase(BaseModel):
    nom_produit: str
    type_produit: Optional[str] = None
    description: Optional[str] = None
    usages: Optional[str] = None
    prix_unitaire: Decimal
    url_image: Optional[str] = None  # URL de l'image du produit

class ProduitCreate(ProduitBase):
    pass

class ProduitRead(ProduitBase):
    id_produit: int
    model_config = ConfigDict(from_attributes=True)
