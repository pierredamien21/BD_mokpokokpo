from pydantic import BaseModel, ConfigDict
from datetime import datetime

class StockCreate(BaseModel):
    quantite_disponible: int
    seuil_minimal: int
    id_produit: int

class StockOut(StockCreate):
    model_config = ConfigDict(from_attributes=True)
    
    id_stock: int
    date_derniere_mise_a_jour: datetime