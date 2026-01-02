from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class LigneCommandeCreate(BaseModel):
    id_commande: int
    id_produit: int
    quantite: int
    prix_unitaire: Decimal
    montant_ligne: Decimal

class LigneCommandeOut(LigneCommandeCreate):
    model_config = ConfigDict(from_attributes=True)
    
    id_ligne_commande: int