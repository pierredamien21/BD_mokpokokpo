from pydantic import BaseModel, ConfigDict
from datetime import datetime

class StockBase(BaseModel):
    quantite_disponible: int
    seuil_minimal: int

class StockCreate(StockBase):
    id_produit: int

class StockRead(StockBase):
    id_stock: int
    date_derniere_mise_a_jour: datetime
    model_config = ConfigDict(from_attributes=True)
