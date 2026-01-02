from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal

class CommandeCreate(BaseModel):
    id_client: int
    statut: str

class CommandeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_commande: int
    date_commande: datetime
    montant_total: Decimal
    statut: str
    id_client: int