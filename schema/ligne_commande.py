from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class LigneCommandeBase(BaseModel):
    quantite: int
    prix_unitaire: Decimal
    montant_ligne: Decimal

class LigneCommandeCreate(LigneCommandeBase):
    id_commande: int
    id_produit: int

class LigneCommandeRead(LigneCommandeBase):
    id_ligne_commande: int
    model_config = ConfigDict(from_attributes=True)
