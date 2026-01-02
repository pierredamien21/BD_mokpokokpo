from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ReservationCreate(BaseModel):
    id_client: int
    statut: str

class ReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_reservation: int
    date_reservation: datetime
    statut: str
    id_client: int