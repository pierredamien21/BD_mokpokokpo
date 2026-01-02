-- =====================================================
-- VUES METIER - BASE MOKPOKPO
-- Schéma : public
-- =====================================================

SET search_path TO public;

-- =====================================================
-- VUE 1 : Stock actuel des produits
-- =====================================================
-- Objectif :
-- Afficher l’état du stock pour chaque produit
-- (quantité disponible + seuil minimal)
-- =====================================================

CREATE OR REPLACE VIEW vue_stock_actuel AS
SELECT
    p.id_produit,
    p.nom_produit,
    s.quantite_disponible,
    s.seuil_minimal,
    s.date_derniere_mise_a_jour
FROM produit p
JOIN stock s ON p.id_produit = s.id_produit;

-- =====================================================
-- VUE 2 : Commandes détaillées (ligne par produit)
-- =====================================================
-- Objectif :
-- Avoir le détail complet des commandes
-- (client + produit + quantités)
-- =====================================================

CREATE OR REPLACE VIEW vue_commandes_detaillees AS
SELECT
    c.id_commande,
    c.date_commande,
    c.statut,
    cl.id_client,
    u.nom || ' ' || u.prenom AS client,
    p.nom_produit,
    lc.quantite,
    lc.prix_unitaire,
    lc.montant_ligne
FROM commande c
JOIN client cl ON c.id_client = cl.id_client
JOIN utilisateur u ON cl.id_utilisateur = u.id_utilisateur
JOIN ligne_commande lc ON c.id_commande = lc.id_commande
JOIN produit p ON lc.id_produit = p.id_produit;

-- =====================================================
-- VUE 3 : Historique des ventes
-- =====================================================
-- Objectif :
-- Consulter les ventes validées avec leur chiffre d’affaires
-- =====================================================

CREATE OR REPLACE VIEW vue_ventes AS
SELECT
    v.id_vente,
    v.date_vente,
    v.chiffre_affaires,
    c.id_commande,
    u.nom || ' ' || u.prenom AS client
FROM vente v
JOIN commande c ON v.id_commande = c.id_commande
JOIN client cl ON c.id_client = cl.id_client
JOIN utilisateur u ON cl.id_utilisateur = u.id_utilisateur;

-- =====================================================
-- VUE 4 : Alertes de stock
-- =====================================================
-- Objectif :
-- Suivre les alertes de stock bas par produit
-- =====================================================

CREATE OR REPLACE VIEW vue_alertes_stock AS
SELECT
    a.id_alerte,
    a.date_alerte,
    p.nom_produit,
    a.message,
    a.statut,
    a.seuil_declencheur
FROM alerte_stock a
JOIN produit p ON a.id_produit = p.id_produit;

-- =====================================================
-- VUE 5 : Chiffre d’affaires par produit
-- =====================================================
-- Objectif :
-- Aider le gestionnaire commercial à analyser
-- la rentabilité des produits
-- =====================================================

CREATE OR REPLACE VIEW vue_chiffre_affaires_par_produit AS
SELECT
    p.id_produit,
    p.nom_produit,
    SUM(lc.montant_ligne) AS chiffre_affaires_total
FROM ligne_commande lc
JOIN commande c ON lc.id_commande = c.id_commande
JOIN produit p ON lc.id_produit = p.id_produit
WHERE c.statut = 'ACCEPTEE'
GROUP BY p.id_produit, p.nom_produit;

-- =====================================================
-- FIN DES VUES
-- =====================================================
