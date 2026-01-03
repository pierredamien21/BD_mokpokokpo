from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

from schema.enums import StatutCommandeEnum

class CommandeBase(BaseModel):
    statut: StatutCommandeEnum = StatutCommandeEnum.EN_ATTENTE

class CommandeCreate(CommandeBase):
    id_utilisateur: int

class CommandeRead(CommandeBase):
    id_commande: int
    date_commande: datetime
    montant_total: Decimal

    class Config:
        from_attributes = True
