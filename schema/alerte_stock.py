from pydantic import BaseModel, ConfigDict
from datetime import datetime

class AlerteStockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_alerte: int
    date_alerte: datetime
    message: str
    statut: str
    seuil_declencheur: int
    id_produit: int