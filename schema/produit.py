from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class ProduitBase(BaseModel):
    nom_produit: str
    type_produit: str | None = None
    description: str | None = None
    usages: str | None = None
    prix_unitaire: Decimal

class ProduitCreate(ProduitBase):
    pass

class ProduitOut(ProduitBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_produit: int