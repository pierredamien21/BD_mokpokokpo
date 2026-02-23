from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    DateTime,
    Boolean,
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
    actif = Column(Boolean, default=True, nullable=False)

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

    id_client = Column(Integer, primary_key=True)
    id_utilisateur = Column(
        Integer,
        ForeignKey("utilisateur.id_utilisateur", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    telephone = Column(String(30))
    adresse = Column(Text)
    actif = Column(Boolean, default=True, nullable=False)

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
    url_image = Column(Text)  # URL de l'image du produit

    stock = relationship("Stock", back_populates="produit", uselist=False)
    lots = relationship("Lot", back_populates="produit", cascade="all, delete-orphan")
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
    lots = relationship("Lot", back_populates="stock", cascade="all, delete-orphan")


# =====================================================
# LOT (BATCH TRACKING - FEFO)
# =====================================================
class Lot(Base):
    __tablename__ = "lot"

    id_lot = Column(Integer, primary_key=True)
    numero_lot = Column(String(50), nullable=False)
    date_fabrication = Column(DateTime, nullable=False)
    date_expiration = Column(DateTime, nullable=False)
    quantite_initiale = Column(Integer, nullable=False)
    quantite_restante = Column(Integer, nullable=False)
    fournisseur = Column(String(150), nullable=True)
    date_creation = Column(DateTime, server_default=func.now())
    
    id_produit = Column(
        Integer,
        ForeignKey("produit.id_produit", ondelete="CASCADE"),
        nullable=False
    )
    id_stock = Column(
        Integer,
        ForeignKey("stock.id_stock", ondelete="CASCADE"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "numero_lot",
            "id_produit",
            name="uq_lot_numero_produit"
        ),
    )

    produit = relationship("Produit", back_populates="lots")
    stock = relationship("Stock", back_populates="lots")
    lignes_commande = relationship("LigneCommande", back_populates="lot", cascade="all, delete-orphan")


# =====================================================
# COMMANDE
# =====================================================
class Commande(Base):
    __tablename__ = "commande"

    id_commande = Column(Integer, primary_key=True)
    date_commande = Column(DateTime, server_default=func.now())
    montant_total = Column(Numeric(12, 2), default=0)
    statut = Column(String(20), nullable=False)

    id_client = Column(
        Integer,
        ForeignKey("client.id_client", ondelete="CASCADE"),
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
    livraison = relationship("Livraison", back_populates="commande", uselist=False)


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
    id_lot = Column(
        Integer,
        ForeignKey("lot.id_lot"),
        nullable=True
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
    lot = relationship("Lot", back_populates="lignes_commande")


# =====================================================
# RESERVATION
# =====================================================
class Reservation(Base):
    __tablename__ = "reservation"

    id_reservation = Column(Integer, primary_key=True)
    date_reservation = Column(DateTime, server_default=func.now())
    statut = Column(String(20), nullable=False)

    id_client = Column(
        Integer,
        ForeignKey("client.id_client", ondelete="CASCADE"),
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
    deleted_at = Column(DateTime, nullable=True)

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


# =====================================================
# LIVRAISON (PHASE 3 - DELIVERY MANAGEMENT)
# =====================================================
class Livraison(Base):
    __tablename__ = "livraison"

    id_livraison = Column(Integer, primary_key=True, index=True)
    numero_livraison = Column(String(50), unique=True, nullable=False)
    statut = Column(String(30), nullable=False, default="EN_PREPARATION")
    date_creation = Column(DateTime, server_default=func.now(), index=True)
    date_preparation = Column(DateTime, nullable=True)
    date_expedition = Column(DateTime, nullable=True)
    date_livraison = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    adresse_livraison = Column(Text, nullable=True)
    transporteur = Column(String(100), nullable=True)
    numero_suivi = Column(String(100), nullable=True, unique=True)

    # Clés étrangères
    id_commande = Column(
        Integer,
        ForeignKey("commande.id_commande", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    __table_args__ = (
        CheckConstraint(
            "statut IN ('EN_PREPARATION', 'PRETE', 'EN_LIVRAISON', 'LIVRÉE')",
            name="ck_livraison_statut"
        ),
        CheckConstraint(
            "date_preparation IS NULL OR date_preparation >= date_creation",
            name="ck_livraison_preparation_date"
        ),
        CheckConstraint(
            "date_expedition IS NULL OR date_expedition >= COALESCE(date_preparation, date_creation)",
            name="ck_livraison_expedition_date"
        ),
        CheckConstraint(
            "date_livraison IS NULL OR date_livraison >= COALESCE(date_expedition, date_creation)",
            name="ck_livraison_delivery_date"
        ),
    )

    # Relations
    commande = relationship("Commande", back_populates="livraison")
