from pydantic import BaseModel, ConfigDict
from datetime import datetime

from schema.enums import StatutReservationEnum

class ReservationBase(BaseModel):
    statut: StatutReservationEnum = StatutReservationEnum.EN_ATTENTE

class ReservationCreate(ReservationBase):
    id_client: int

class ReservationRead(ReservationBase):
    id_reservation: int
    date_reservation: datetime
    model_config = ConfigDict(from_attributes=True)
