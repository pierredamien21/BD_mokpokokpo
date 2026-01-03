-- =====================================================
-- ROLES & PERMISSIONS - Projet Mokpokpo
-- SGBD : PostgreSQL
-- Schéma : public
-- =====================================================

SET search_path TO public;

-- =====================================================
-- 1 CRÉATION DES RÔLES (SI NON EXISTANTS)
-- =====================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'role_admin') THEN
        CREATE ROLE role_admin;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'role_gestionnaire_commercial') THEN
        CREATE ROLE role_gestionnaire_commercial;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'role_gestionnaire_stock') THEN
        CREATE ROLE role_gestionnaire_stock;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'role_client') THEN
        CREATE ROLE role_client;
    END IF;
END $$;

-- =====================================================
-- 2 NETTOYAGE : RÉINITIALISER LES DROITS EXISTANTS
-- =====================================================

REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM role_admin;
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM role_gestionnaire_commercial;
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM role_gestionnaire_stock;
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM role_client;

REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM role_admin;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM role_gestionnaire_commercial;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM role_gestionnaire_stock;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM role_client;

-- =====================================================
-- 3 PERMISSIONS : ADMINISTRATEUR
-- =====================================================
-- Accès total au système

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO role_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO role_admin;

-- =====================================================
-- 4 PERMISSIONS : GESTIONNAIRE COMMERCIAL
-- =====================================================
-- Gère produits, commandes, ventes, réservations

GRANT SELECT, INSERT, UPDATE
ON produit, commande, ligne_commande, reservation, ligne_reservation, vente
TO role_gestionnaire_commercial;

GRANT SELECT
ON utilisateur, client
TO role_gestionnaire_commercial;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA public
TO role_gestionnaire_commercial;

-- =====================================================
-- 5 PERMISSIONS : GESTIONNAIRE DE STOCK
-- =====================================================
-- Gère stock et alertes

GRANT SELECT, INSERT, UPDATE
ON stock, alerte_stock
TO role_gestionnaire_stock;

GRANT SELECT
ON produit
TO role_gestionnaire_stock;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA public
TO role_gestionnaire_stock;

-- =====================================================
-- 6️⃣ PERMISSIONS : CLIENT
-- =====================================================
-- Consultation + commandes / réservations

GRANT SELECT
ON produit
TO role_client;

GRANT SELECT, INSERT
ON commande, ligne_commande, reservation, ligne_reservation
TO role_client;

GRANT SELECT
ON vente
TO role_client;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA public
TO role_client;

-- =====================================================
-- FIN DU SCRIPT
-- =====================================================
