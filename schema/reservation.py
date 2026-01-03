from pydantic import BaseModel
from datetime import datetime

class ReservationBase(BaseModel):
    statut: str

class ReservationCreate(ReservationBase):
    id_client: int

class ReservationRead(ReservationBase):
    id_reservation: int
    date_reservation: datetime

    class Config:
        from_attributes = True
