-- ============================================
-- MIGRATION : PHASE 3 - GESTION DES LIVRAISONS
-- Table: livraison
-- Description: Gestion complète de la lifecycle des livraisons
-- ============================================

-- ============================================
-- TABLE LIVRAISON
-- ============================================

CREATE TABLE livraison (
    id_livraison SERIAL PRIMARY KEY,
    numero_livraison VARCHAR(100) UNIQUE NOT NULL,
    statut VARCHAR(50) NOT NULL DEFAULT 'EN_PREPARATION' 
        CHECK (statut IN ('EN_PREPARATION', 'PRETE', 'EN_LIVRAISON', 'LIVRÉE')),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_preparation TIMESTAMP,
    date_expedition TIMESTAMP,
    date_livraison TIMESTAMP,
    adresse_livraison TEXT NOT NULL,
    transporteur VARCHAR(150),
    numero_suivi VARCHAR(100),
    notes TEXT,
    id_commande INT UNIQUE NOT NULL,
    
    -- Contrainte de clé étrangère vers commande
    CONSTRAINT fk_livraison_commande
        FOREIGN KEY (id_commande)
        REFERENCES commande(id_commande)
        ON DELETE CASCADE,
    
    -- Contrainte : date_preparation >= date_creation
    CONSTRAINT check_date_preparation
        CHECK (date_preparation IS NULL OR date_preparation >= date_creation),
    
    -- Contrainte : date_expedition >= date_preparation
    CONSTRAINT check_date_expedition
        CHECK (date_expedition IS NULL OR date_preparation IS NOT NULL 
               OR date_expedition >= date_creation),
    
    -- Contrainte : date_livraison >= date_expedition
    CONSTRAINT check_date_livraison
        CHECK (date_livraison IS NULL OR date_expedition IS NOT NULL 
               OR date_livraison >= date_expedition),
    
    -- Contrainte : transitions de statut valides
    CONSTRAINT check_statut_transitions
        CHECK (
            (statut = 'EN_PREPARATION' AND date_preparation IS NULL) OR
            (statut = 'PRETE' AND date_preparation IS NOT NULL) OR
            (statut = 'EN_LIVRAISON' AND date_expedition IS NOT NULL) OR
            (statut = 'LIVRÉE' AND date_livraison IS NOT NULL)
        )
);

-- ============================================
-- INDEXES POUR OPTIMISER LES REQUÊTES
-- ============================================

-- Index sur id_commande (recherches fréquentes)
CREATE INDEX idx_livraison_id_commande ON livraison(id_commande);

-- Index sur statut (filtrage par statut)
CREATE INDEX idx_livraison_statut ON livraison(statut);

-- Index sur date_creation (tri chronologique)
CREATE INDEX idx_livraison_date_creation ON livraison(date_creation DESC);

-- Index composé pour dashboard stats
CREATE INDEX idx_livraison_statut_date ON livraison(statut, date_creation DESC);

-- ============================================
-- COMMENTAIRES POUR DOCUMENTATION
-- ============================================

COMMENT ON TABLE livraison IS 'Gestion des livraisons des commandes acceptées avec suivi des étapes';

COMMENT ON COLUMN livraison.numero_livraison IS 'Identifiant commercial de la livraison (unique, ex: LIV-2024-001)';
COMMENT ON COLUMN livraison.statut IS 'État de la livraison (progression: EN_PREPARATION → PRETE → EN_LIVRAISON → LIVRÉE)';
COMMENT ON COLUMN livraison.date_preparation IS 'Date à laquelle la livraison a été préparée (transition vers PRETE)';
COMMENT ON COLUMN livraison.date_expedition IS 'Date d''expédition au transporteur (transition vers EN_LIVRAISON)';
COMMENT ON COLUMN livraison.date_livraison IS 'Date de livraison confirmée (transition vers LIVRÉE)';
COMMENT ON COLUMN livraison.adresse_livraison IS 'Adresse de livraison (peut différer du client)';
COMMENT ON COLUMN livraison.transporteur IS 'Nom du prestataire de transport';
COMMENT ON COLUMN livraison.numero_suivi IS 'Numéro de suivi fourni par le transporteur';
COMMENT ON COLUMN livraison.notes IS 'Informations complémentaires accumulées (timestamps ajoutés)';
COMMENT ON COLUMN livraison.id_commande IS 'Référence à la commande (1:1, commande acceptée uniquement)';
