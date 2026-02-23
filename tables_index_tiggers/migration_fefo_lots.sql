-- ======================================================================
-- 🚀 MIGRATION FEFO (First Expired First Out) - Gestion des Lots
-- ======================================================================
-- Date: 2026-02-23
-- Objectif: Ajouter support des lots avec dates expiration pour FEFO
-- ======================================================================

-- ======================================================================
-- 1️⃣ CRÉER TABLE LOT
-- ======================================================================
CREATE TABLE IF NOT EXISTS lot (
    id_lot SERIAL PRIMARY KEY,
    numero_lot VARCHAR(50) NOT NULL,
    date_fabrication TIMESTAMP NOT NULL,
    date_expiration TIMESTAMP NOT NULL,
    quantite_initiale INTEGER NOT NULL CHECK (quantite_initiale > 0),
    quantite_restante INTEGER NOT NULL CHECK (quantite_restante >= 0),
    fournisseur VARCHAR(150),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    id_produit INTEGER NOT NULL REFERENCES produit(id_produit) ON DELETE CASCADE,
    id_stock INTEGER NOT NULL REFERENCES stock(id_stock) ON DELETE CASCADE,
    
    CONSTRAINT uq_lot_numero_produit UNIQUE (numero_lot, id_produit),
    CONSTRAINT ck_lot_quantite CHECK (quantite_restante <= quantite_initiale)
);

-- Index pour recherche rapide par date expiration (FEFO)
CREATE INDEX IF NOT EXISTS idx_lot_date_expiration 
    ON lot(id_produit, date_expiration ASC) 
    WHERE quantite_restante > 0;

-- Index pour recherche par date expiration (alertes)
CREATE INDEX IF NOT EXISTS idx_lot_date_fabrication 
    ON lot(date_fabrication DESC);

-- Index pour recherche par stock
CREATE INDEX IF NOT EXISTS idx_lot_id_stock 
    ON lot(id_stock);

-- ======================================================================
-- 2️⃣ MODIFIER TABLE LIGNE_COMMANDE
-- ======================================================================
ALTER TABLE ligne_commande 
ADD COLUMN IF NOT EXISTS id_lot INTEGER REFERENCES lot(id_lot) ON DELETE SET NULL;

-- Index pour tracer les lignes par lot
CREATE INDEX IF NOT EXISTS idx_ligne_commande_id_lot 
    ON ligne_commande(id_lot) 
    WHERE id_lot IS NOT NULL;

-- ======================================================================
-- 3️⃣ AJOUTER COLONNES POUR ALERTES INTELLIGENTES (Phase 2)
-- ======================================================================
-- Ces colonnes seront utilisées par le système d'alerte expiration (J-90, J-60, J-30)
ALTER TABLE alerte_stock 
ADD COLUMN IF NOT EXISTS type_alerte VARCHAR(20) DEFAULT 'QUANTITE';
    -- Type: 'QUANTITE', 'JAUNE' (J-90), 'ORANGE' (J-60), 'ROUGE' (J-30), 'EXPIRÉ'

ALTER TABLE alerte_stock 
ADD COLUMN IF NOT EXISTS id_lot INTEGER REFERENCES lot(id_lot) ON DELETE CASCADE;

-- ======================================================================
-- 4️⃣ VÉRIFICATION & INDEXES SUPPLÉMENTAIRES
-- ======================================================================
-- Index pour optimiser les requêtes de vente (validations)
CREATE INDEX IF NOT EXISTS idx_lot_actif 
    ON lot(id_produit, quantite_restante) 
    WHERE quantite_restante > 0 AND date_expiration > CURRENT_TIMESTAMP;

-- ======================================================================
-- RÉSUMÉ DES CHANGEMENTS
-- ======================================================================
-- ✅ Table LOT créée avec:
--    - Numéro de lot (unique par produit)
--    - Dates fabrication/expiration
--    - Tracking quantité initiale vs restante
--    - Fournisseur et date création
--
-- ✅ INDEX créés pour:
--    - Recherche rapide FEFO (par expiration croissante)
--    - Alertes intelligentes
--    - Traçabilité stock
--
-- ✅ LIGNE_COMMANDE modifiée:
--    - Ajout colonne id_lot (nullable, optionnel)
--    - Permet tracer quel lot a alimenté chaque ligne
--
-- ✅ ALERTE_STOCK améliorée:
--    - Ajout type_alerte (QUANTITE, JAUNE, ORANGE, ROUGE, EXPIRÉ)
--    - Lien vers lot pour alertes expiration
--
-- ======================================================================
-- ROLLBACK (En cas d'erreur)
-- ======================================================================
/*
DROP TABLE IF EXISTS lot CASCADE;
ALTER TABLE ligne_commande DROP COLUMN IF EXISTS id_lot;
ALTER TABLE alerte_stock DROP COLUMN IF EXISTS type_alerte;
ALTER TABLE alerte_stock DROP COLUMN IF EXISTS id_lot;
*/
-- ======================================================================
