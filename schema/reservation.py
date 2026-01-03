from pydantic import BaseModel
from datetime import datetime

from schema.enums import StatutReservationEnum

class ReservationBase(BaseModel):
    statut: StatutReservationEnum = StatutReservationEnum.EN_ATTENTE

class ReservationCreate(ReservationBase):
    id_utilisateur: int

class ReservationRead(ReservationBase):
    id_reservation: int
    date_reservation: datetime

    class Config:
        from_attributes = True
