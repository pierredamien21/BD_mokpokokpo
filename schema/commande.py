from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal

from schema.enums import StatutCommandeEnum

class CommandeBase(BaseModel):
    statut: StatutCommandeEnum = StatutCommandeEnum.EN_ATTENTE

class CommandeCreate(CommandeBase):
    id_client: int

class CommandeRead(CommandeBase):
    id_commande: int
    date_commande: datetime
    montant_total: Decimal
    model_config = ConfigDict(from_attributes=True)
