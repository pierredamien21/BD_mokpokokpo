from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional

class VenteCreate(BaseModel):
    id_commande: int
    chiffre_affaires: Decimal

class VenteRead(VenteCreate):
    id_vente: int
    date_vente: datetime
    deleted_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
