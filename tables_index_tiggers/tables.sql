-- =========================
-- Base : Ferme Mokpokpo
-- SGBD : PostgreSQL
-- =========================

--  UTILISATEUR
CREATE TABLE utilisateur (
    id_utilisateur SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    mot_de_passe TEXT NOT NULL,
    role VARCHAR(30) NOT NULL CHECK (role IN (
        'CLIENT',
        'GEST_COMMERCIAL',
        'GEST_STOCK',
        'ADMIN'
    )),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--  CLIENT
CREATE TABLE client (
    id_client SERIAL PRIMARY KEY,
    telephone VARCHAR(30),
    adresse TEXT,
    id_utilisateur INT UNIQUE NOT NULL,
    CONSTRAINT fk_client_utilisateur
        FOREIGN KEY (id_utilisateur)
        REFERENCES utilisateur(id_utilisateur)
        ON DELETE CASCADE
);

-- PRODUIT
CREATE TABLE produit (
    id_produit SERIAL PRIMARY KEY,
    nom_produit VARCHAR(150) NOT NULL,
    type_produit VARCHAR(50),
    description TEXT,
    usages TEXT,
    prix_unitaire NUMERIC(10,2) NOT NULL CHECK (prix_unitaire >= 0)
);

--  STOCK
CREATE TABLE stock (
    id_stock SERIAL PRIMARY KEY,
    quantite_disponible INT NOT NULL CHECK (quantite_disponible >= 0),
    seuil_minimal INT NOT NULL CHECK (seuil_minimal >= 0),
    date_derniere_mise_a_jour TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_produit INT UNIQUE NOT NULL,
    CONSTRAINT fk_stock_produit
        FOREIGN KEY (id_produit)
        REFERENCES produit(id_produit)
        ON DELETE CASCADE
);

--  COMMANDE
CREATE TABLE commande (
    id_commande SERIAL PRIMARY KEY,
    date_commande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    montant_total NUMERIC(12,2) DEFAULT 0,
    statut VARCHAR(20) NOT NULL CHECK (statut IN (
        'EN_ATTENTE',
        'ACCEPTEE',
        'REFUSEE'
    )),
    id_client INT NOT NULL,
    CONSTRAINT fk_commande_client
        FOREIGN KEY (id_client)
        REFERENCES client(id_client)
        ON DELETE CASCADE
);

--  LIGNE_COMMANDE
CREATE TABLE ligne_commande (
    id_ligne_commande SERIAL PRIMARY KEY,
    quantite INT NOT NULL CHECK (quantite > 0),
    prix_unitaire NUMERIC(10,2) NOT NULL CHECK (prix_unitaire >= 0),
    montant_ligne NUMERIC(12,2) NOT NULL,
    id_commande INT NOT NULL,
    id_produit INT NOT NULL,
    CONSTRAINT fk_ligne_commande_commande
        FOREIGN KEY (id_commande)
        REFERENCES commande(id_commande)
        ON DELETE CASCADE,
    CONSTRAINT fk_ligne_commande_produit
        FOREIGN KEY (id_produit)
        REFERENCES produit(id_produit)
);

--  RESERVATION
CREATE TABLE reservation (
    id_reservation SERIAL PRIMARY KEY,
    date_reservation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut VARCHAR(20) NOT NULL CHECK (statut IN (
        'EN_ATTENTE',
        'ACCEPTEE',
        'REFUSEE'
    )),
    id_client INT NOT NULL,
    CONSTRAINT fk_reservation_client
        FOREIGN KEY (id_client)
        REFERENCES client(id_client)
        ON DELETE CASCADE
);

--  LIGNE_RESERVATION
CREATE TABLE ligne_reservation (
    id_ligne_reservation SERIAL PRIMARY KEY,
    quantite_reservee INT NOT NULL CHECK (quantite_reservee > 0),
    id_reservation INT NOT NULL,
    id_produit INT NOT NULL,
    CONSTRAINT fk_ligne_reservation_reservation
        FOREIGN KEY (id_reservation)
        REFERENCES reservation(id_reservation)
        ON DELETE CASCADE,
    CONSTRAINT fk_ligne_reservation_produit
        FOREIGN KEY (id_produit)
        REFERENCES produit(id_produit)
);

--  VENTE
CREATE TABLE vente (
    id_vente SERIAL PRIMARY KEY,
    date_vente TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    chiffre_affaires NUMERIC(12,2) NOT NULL,
    id_commande INT UNIQUE NOT NULL,
    CONSTRAINT fk_vente_commande
        FOREIGN KEY (id_commande)
        REFERENCES commande(id_commande)
);

--  ALERTE_STOCK
CREATE TABLE alerte_stock (
    id_alerte SERIAL PRIMARY KEY,
    date_alerte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message TEXT NOT NULL,
    statut VARCHAR(20) NOT NULL CHECK (statut IN (
        'ENVOYEE',
        'TRAITEE'
    )),
    seuil_declencheur INT NOT NULL,
    id_produit INT NOT NULL,
    CONSTRAINT fk_alerte_produit
        FOREIGN KEY (id_produit)
        REFERENCES produit(id_produit)
);
