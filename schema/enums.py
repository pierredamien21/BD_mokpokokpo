from enum import Enum

class RoleEnum(str, Enum):
    CLIENT = "CLIENT"
    GEST_STOCK = "GEST_STOCK"
    GEST_COMMERCIAL = "GEST_COMMERCIAL"
    ADMIN = "ADMIN"

class StatutCommandeEnum(str, Enum):
    EN_ATTENTE = "EN_ATTENTE"
    ACCEPTEE = "ACCEPTEE"
    REFUSEE = "REFUSEE"

class StatutReservationEnum(str, Enum):
    EN_ATTENTE = "EN_ATTENTE"
    ACCEPTEE = "ACCEPTEE"
    REFUSEE = "REFUSEE"

class StatutAlerteEnum(str, Enum):
    TRAITEE = "TRAITEE"
    NON_TRAITEE = "NON_TRAITEE"
