-- =========================================
-- INDEX - Optimisation Base Mokpokpo
-- Schéma : public
-- =========================================

SET search_path TO public;

-- 🔹 Index sur clés étrangères (JOIN & performance)

CREATE INDEX idx_client_utilisateur
    ON client(id_utilisateur);

CREATE INDEX idx_commande_client
    ON commande(id_client);

CREATE INDEX idx_ligne_commande_commande
    ON ligne_commande(id_commande);

CREATE INDEX idx_ligne_commande_produit
    ON ligne_commande(id_produit);

CREATE INDEX idx_stock_produit
    ON stock(id_produit);

CREATE INDEX idx_reservation_client
    ON reservation(id_client);

CREATE INDEX idx_ligne_reservation_reservation
    ON ligne_reservation(id_reservation);

CREATE INDEX idx_ligne_reservation_produit
    ON ligne_reservation(id_produit);

CREATE INDEX idx_vente_commande
    ON vente(id_commande);

CREATE INDEX idx_alerte_produit
    ON alerte_stock(id_produit);

-- 🔹 Index métier (recherches fréquentes)

CREATE INDEX idx_produit_nom
    ON produit(nom_produit);

CREATE INDEX idx_commande_statut
    ON commande(statut);

CREATE INDEX idx_commande_date
    ON commande(date_commande);

-- =========================================
-- FIN DES INDEX
-- =========================================
