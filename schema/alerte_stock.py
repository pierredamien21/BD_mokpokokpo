from pydantic import BaseModel
from datetime import datetime

class AlerteStockCreate(BaseModel):
    message: str
    statut: str
    seuil_declencheur: int
    id_produit: int

class AlerteStockRead(AlerteStockCreate):
    id_alerte: int
    date_alerte: datetime

    class Config:
        from_attributes = True
