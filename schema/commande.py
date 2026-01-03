from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class CommandeBase(BaseModel):
    statut: str

class CommandeCreate(CommandeBase):
    id_client: int

class CommandeRead(CommandeBase):
    id_commande: int
    date_commande: datetime
    montant_total: Decimal

    class Config:
        from_attributes = True
