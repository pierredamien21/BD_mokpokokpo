-- =====================================================
-- INDEX COMPLETS - Projet Mokpokpo
-- Méthode : Table mère + tables par rôle
-- Schéma : public
-- =====================================================

SET search_path TO public;

-- =====================================================
-- 🔹 UTILISATEUR (classe mère)
-- =====================================================

-- Recherche par email (login)
CREATE UNIQUE INDEX idx_utilisateur_email
ON utilisateur(email);

-- =====================================================
-- 🔹 CLIENT (rôle : client)
-- =====================================================

CREATE UNIQUE INDEX idx_client_utilisateur
ON client(id_utilisateur);

CREATE INDEX idx_client_telephone
ON client(telephone);

-- =====================================================
-- 🔹 GESTIONNAIRE STOCK
-- =====================================================

CREATE UNIQUE INDEX idx_gestionnaire_stock_utilisateur
ON gestionnaire_stock(id_utilisateur);

-- =====================================================
-- 🔹 GESTIONNAIRE COMMERCIAL
-- =====================================================

CREATE UNIQUE INDEX idx_gestionnaire_commercial_utilisateur
ON gestionnaire_commercial(id_utilisateur);

-- =====================================================
-- 🔹 ADMINISTRATEUR
-- =====================================================

CREATE UNIQUE INDEX idx_administrateur_utilisateur
ON administrateur(id_utilisateur);

-- =====================================================
-- 🔹 PRODUIT
-- =====================================================

CREATE INDEX idx_produit_nom
ON produit(nom_produit);

CREATE INDEX idx_produit_type
ON produit(type_produit);

-- =====================================================
-- 🔹 STOCK
-- =====================================================

CREATE UNIQUE INDEX idx_stock_produit
ON stock(id_produit);

CREATE INDEX idx_stock_quantite
ON stock(quantite_disponible);

-- =====================================================
-- 🔹 COMMANDE
-- =====================================================

CREATE INDEX idx_commande_client
ON commande(id_client);

CREATE INDEX idx_commande_statut
ON commande(statut);

CREATE INDEX idx_commande_date
ON commande(date_commande);

-- =====================================================
-- 🔹 LIGNE_COMMANDE
-- =====================================================

CREATE INDEX idx_ligne_commande_commande
ON ligne_commande(id_commande);

CREATE INDEX idx_ligne_commande_produit
ON ligne_commande(id_produit);

-- =====================================================
-- 🔹 RESERVATION
-- =====================================================

CREATE INDEX idx_reservation_client
ON reservation(id_client);

CREATE INDEX idx_reservation_statut
ON reservation(statut);

-- =====================================================
-- 🔹 VENTE
-- =====================================================

CREATE UNIQUE INDEX idx_vente_commande
ON vente(id_commande);

CREATE INDEX idx_vente_date
ON vente(date_vente);

-- =====================================================
-- 🔹 ALERTE_STOCK
-- =====================================================

CREATE INDEX idx_alerte_produit
ON alerte_stock(id_produit);

CREATE INDEX idx_alerte_statut
ON alerte_stock(statut);

-- =====================================================
-- FIN DES INDEX
-- =====================================================
