from pydantic import BaseModel, ConfigDict
from datetime import datetime

from schema.enums import StatutAlerteEnum

class AlerteStockCreate(BaseModel):
    message: str
    statut: StatutAlerteEnum = StatutAlerteEnum.NON_TRAITEE
    seuil_declencheur: int
    id_produit: int

class AlerteStockRead(AlerteStockCreate):
    id_alerte: int
    date_alerte: datetime
    model_config = ConfigDict(from_attributes=True)
