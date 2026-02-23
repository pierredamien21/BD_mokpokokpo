-- =====================================================
-- MIGRATION: Soft Delete + URL Images
-- Date: 2026-02-23
-- Description: Ajout des colonnes pour soft delete et images produits
-- =====================================================

-- 1. Ajouter colonne 'actif' à la table 'utilisateur'
ALTER TABLE utilisateur 
ADD COLUMN IF NOT EXISTS actif BOOLEAN NOT NULL DEFAULT TRUE;

-- Créer un index pour filtrer rapidement les utilisateurs actifs
CREATE INDEX IF NOT EXISTS idx_utilisateur_actif ON utilisateur(actif);

-- 2. Ajouter colonne 'actif' à la table 'client'
ALTER TABLE client 
ADD COLUMN IF NOT EXISTS actif BOOLEAN NOT NULL DEFAULT TRUE;

-- Créer un index pour filtrer rapidement les clients actifs
CREATE INDEX IF NOT EXISTS idx_client_actif ON client(actif);

-- 3. Ajouter colonne 'deleted_at' à la table 'vente'
ALTER TABLE vente 
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;

-- Créer un index pour filtrer rapidement les ventes non supprimées
CREATE INDEX IF NOT EXISTS idx_vente_deleted_at ON vente(deleted_at);

-- 4. Ajouter colonne 'url_image' à la table 'produit'
ALTER TABLE produit 
ADD COLUMN IF NOT EXISTS url_image TEXT;

-- =====================================================
-- Vérification des colonnes ajoutées
-- =====================================================

-- Vérifier la structure de 'utilisateur'
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'utilisateur' AND column_name = 'actif';

-- Vérifier la structure de 'client'
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'client' AND column_name = 'actif';

-- Vérifier la structure de 'vente'
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'vente' AND column_name = 'deleted_at';

-- Vérifier la structure de 'produit'
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'produit' AND column_name = 'url_image';

-- =====================================================
-- Notes importantes
-- =====================================================
-- 
-- SOFT DELETE:
-- - utilisateur.actif = TRUE par défaut (utilisateurs existants restent actifs)
-- - client.actif = TRUE par défaut (clients existants restent actifs)
-- - vente.deleted_at = NULL par défaut (ventes existantes non archivées)
--
-- IMAGES:
-- - produit.url_image = NULL par défaut (produits existants sans images)
--
-- ROLLBACK (si nécessaire):
-- ALTER TABLE utilisateur DROP COLUMN IF EXISTS actif;
-- ALTER TABLE client DROP COLUMN IF EXISTS actif;
-- ALTER TABLE vente DROP COLUMN IF EXISTS deleted_at;
-- ALTER TABLE produit DROP COLUMN IF EXISTS url_image;
-- DROP INDEX IF EXISTS idx_utilisateur_actif;
-- DROP INDEX IF EXISTS idx_client_actif;
-- DROP INDEX IF EXISTS idx_vente_deleted_at;
