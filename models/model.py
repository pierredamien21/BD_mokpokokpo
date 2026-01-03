from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

# =====================================================
# UTILISATEUR (TABLE MÈRE LOGIQUE)
# =====================================================
class Utilisateur(Base):
    __tablename__ = "utilisateur"

    id_utilisateur = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    mot_de_passe = Column(Text, nullable=False)
    role = Column(String(30), nullable=False)
    date_creation = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "role IN ('CLIENT', 'GEST_STOCK', 'GEST_COMMERCIAL', 'ADMIN')",
            name="ck_utilisateur_role"
        ),
    )

    # Relations
    client = relationship(
        "Client",
        back_populates="utilisateur",
        uselist=False,
        cascade="all, delete"
    )


# =====================================================
# CLIENT (SPÉCIALISATION LOGIQUE DE UTILISATEUR)
# =====================================================
class Client(Base):
    __tablename__ = "client"

    id_utilisateur = Column(
        Integer,
        ForeignKey("utilisateur.id_utilisateur", ondelete="CASCADE"),
        primary_key=True
    )
    telephone = Column(String(30))
    adresse = Column(Text)

    utilisateur = relationship("Utilisateur", back_populates="client")

    commandes = relationship("Commande", back_populates="client")
    reservations = relationship("Reservation", back_populates="client")


# =====================================================
# PRODUIT
# =====================================================
class Produit(Base):
    __tablename__ = "produit"

    id_produit = Column(Integer, primary_key=True)
    nom_produit = Column(String(150), nullable=False)
    type_produit = Column(String(50))
    description = Column(Text)
    usages = Column(Text)
    prix_unitaire = Column(Numeric(10, 2), nullable=False)

    stock = relationship("Stock", back_populates="produit", uselist=False)
    lignes_commande = relationship("LigneCommande", back_populates="produit")
    lignes_reservation = relationship("LigneReservation", back_populates="produit")
    alertes = relationship("AlerteStock", back_populates="produit")


# =====================================================
# STOCK
# =====================================================
class Stock(Base):
    __tablename__ = "stock"

    id_stock = Column(Integer, primary_key=True)
    quantite_disponible = Column(Integer, nullable=False)
    seuil_minimal = Column(Integer, nullable=False)
    date_derniere_mise_a_jour = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
    id_produit = Column(
        Integer,
        ForeignKey("produit.id_produit", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    produit = relationship("Produit", back_populates="stock")


# =====================================================
# COMMANDE
# =====================================================
class Commande(Base):
    __tablename__ = "commande"

    id_commande = Column(Integer, primary_key=True)
    date_commande = Column(DateTime, server_default=func.now())
    montant_total = Column(Numeric(12, 2), default=0)
    statut = Column(String(20), nullable=False)

    id_utilisateur = Column(
        Integer,
        ForeignKey("client.id_utilisateur", ondelete="CASCADE"),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "statut IN ('EN_ATTENTE', 'ACCEPTEE', 'REFUSEE')",
            name="ck_commande_statut"
        ),
    )

    client = relationship("Client", back_populates="commandes")
    lignes = relationship(
        "LigneCommande",
        back_populates="commande",
        cascade="all, delete-orphan"
    )
    vente = relationship("Vente", back_populates="commande", uselist=False)


# =====================================================
# LIGNE COMMANDE
# =====================================================
class LigneCommande(Base):
    __tablename__ = "ligne_commande"

    id_ligne_commande = Column(Integer, primary_key=True)
    quantite = Column(Integer, nullable=False)
    prix_unitaire = Column(Numeric(10, 2), nullable=False)
    montant_ligne = Column(Numeric(12, 2), nullable=False)

    id_commande = Column(
        Integer,
        ForeignKey("commande.id_commande", ondelete="CASCADE"),
        nullable=False
    )
    id_produit = Column(
        Integer,
        ForeignKey("produit.id_produit"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "id_commande",
            "id_produit",
            name="uq_commande_produit"
        ),
    )

    commande = relationship("Commande", back_populates="lignes")
    produit = relationship("Produit", back_populates="lignes_commande")


# =====================================================
# RESERVATION
# =====================================================
class Reservation(Base):
    __tablename__ = "reservation"

    id_reservation = Column(Integer, primary_key=True)
    date_reservation = Column(DateTime, server_default=func.now())
    statut = Column(String(20), nullable=False)

    id_utilisateur = Column(
        Integer,
        ForeignKey("client.id_utilisateur", ondelete="CASCADE"),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "statut IN ('EN_ATTENTE', 'ACCEPTEE', 'REFUSEE')",
            name="ck_reservation_statut"
        ),
    )

    client = relationship("Client", back_populates="reservations")
    lignes = relationship(
        "LigneReservation",
        back_populates="reservation",
        cascade="all, delete-orphan"
    )


# =====================================================
# LIGNE RESERVATION
# =====================================================
class LigneReservation(Base):
    __tablename__ = "ligne_reservation"

    id_ligne_reservation = Column(Integer, primary_key=True)
    quantite_reservee = Column(Integer, nullable=False)

    id_reservation = Column(
        Integer,
        ForeignKey("reservation.id_reservation", ondelete="CASCADE"),
        nullable=False
    )
    id_produit = Column(
        Integer,
        ForeignKey("produit.id_produit"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "id_reservation",
            "id_produit",
            name="uq_reservation_produit"
        ),
    )

    reservation = relationship("Reservation", back_populates="lignes")
    produit = relationship("Produit", back_populates="lignes_reservation")


# =====================================================
# VENTE
# =====================================================
class Vente(Base):
    __tablename__ = "vente"

    id_vente = Column(Integer, primary_key=True)
    date_vente = Column(DateTime, server_default=func.now())
    chiffre_affaires = Column(Numeric(12, 2), nullable=False)

    id_commande = Column(
        Integer,
        ForeignKey("commande.id_commande"),
        unique=True,
        nullable=False
    )

    commande = relationship("Commande", back_populates="vente")


# =====================================================
# ALERTE STOCK
# =====================================================
class AlerteStock(Base):
    __tablename__ = "alerte_stock"

    id_alerte = Column(Integer, primary_key=True)
    date_alerte = Column(DateTime, server_default=func.now())
    message = Column(Text, nullable=False)
    statut = Column(String(20), nullable=False)
    seuil_declencheur = Column(Integer, nullable=False)

    id_produit = Column(
        Integer,
        ForeignKey("produit.id_produit"),
        nullable=False
    )

    produit = relationship("Produit", back_populates="alertes")
