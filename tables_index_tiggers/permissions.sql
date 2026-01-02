-- =====================================================
-- GESTION DES RÔLES ET PERMISSIONS
-- Base : Mokpokpo
-- =====================================================
-- Objectif :
-- Définir des rôles PostgreSQL correspondant
-- aux acteurs métier de l'application.
--
-- Principe :
-- - Chaque rôle a des droits limités
-- - Sécurité appliquée au niveau BD
-- - Respect du principe du moindre privilège
-- =====================================================

-- =====================================================
-- 1 CRÉATION DES RÔLES
-- =====================================================

-- Rôle CLIENT :
-- Peut consulter les produits
-- Peut créer des commandes et réservations
CREATE ROLE role_client NOINHERIT;

-- Rôle GESTIONNAIRE COMMERCIAL :
-- Peut gérer commandes, ventes et produits
CREATE ROLE role_gest_commercial NOINHERIT;

-- Rôle GESTIONNAIRE DE STOCK :
-- Peut gérer le stock et consulter les alertes
CREATE ROLE role_gest_stock NOINHERIT;

-- Rôle ADMINISTRATEUR :
-- Accès complet à la base
CREATE ROLE role_admin NOINHERIT;

-- =====================================================
-- 2 RÉVOCATION PAR SÉCURITÉ (bonne pratique)
-- =====================================================
-- On retire tous les droits par défaut sur le schéma
REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM PUBLIC;

-- =====================================================
-- 3 PERMISSIONS POUR LE RÔLE CLIENT
-- =====================================================
-- Consultation des produits
GRANT SELECT ON produit TO role_client;

-- Création et consultation de ses commandes / réservations
GRANT SELECT, INSERT ON commande, reservation TO role_client;
GRANT SELECT, INSERT ON ligne_commande, ligne_reservation TO role_client;

-- =====================================================
-- 4PERMISSIONS POUR LE GESTIONNAIRE COMMERCIAL
-- =====================================================
-- Gestion des produits (prix, description)
GRANT SELECT, INSERT, UPDATE ON produit TO role_gest_commercial;

-- Consultation et validation des commandes / réservations
GRANT SELECT, UPDATE ON commande, reservation TO role_gest_commercial;

-- Accès aux ventes
GRANT SELECT, INSERT ON vente TO role_gest_commercial;

-- =====================================================
-- 5 PERMISSIONS POUR LE GESTIONNAIRE DE STOCK
-- =====================================================
-- Gestion du stock
GRANT SELECT, UPDATE ON stock TO role_gest_stock;

-- Consultation des produits
GRANT SELECT ON produit TO role_gest_stock;

-- Consultation des alertes de stock
GRANT SELECT, UPDATE ON alerte_stock TO role_gest_stock;

-- =====================================================
-- 6 PERMISSIONS POUR L’ADMINISTRATEUR
-- =====================================================
-- Accès total à toutes les tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO role_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO role_admin;
GRANT ALL PRIVILEGES ON SCHEMA public TO role_admin;

-- =====================================================
-- 7 EXEMPLE : ASSIGNATION D’UN RÔLE À UN UTILISATEUR
-- =====================================================
-- Exemple (à adapter selon tes users PostgreSQL)
-- GRANT role_client TO nom_utilisateur_pg;

-- =====================================================
-- FIN DU SCRIPT RÔLES & PERMISSIONS
-- =====================================================
