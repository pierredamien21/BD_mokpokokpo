-- =====================================================
-- VUES MÉTIER – FERME MOKPOKPO (CORRIGÉES)
-- =====================================================

SET search_path TO public;

-- =====================================================
-- VUE 1 : Produits + Stock
-- =====================================================
CREATE OR REPLACE VIEW vue_produits_stock AS
SELECT
    p.id_produit,
    p.nom_produit,
    p.type_produit,
    p.prix_unitaire,
    s.quantite_disponible,
    s.seuil_minimal,
    CASE
        WHEN s.quantite_disponible <= s.seuil_minimal
        THEN 'STOCK BAS'
        ELSE 'STOCK OK'
    END AS etat_stock
FROM produit p
JOIN stock s ON p.id_produit = s.id_produit;

-- =====================================================
-- VUE 2 : Commandes détaillées (CORRIGÉE)
-- =====================================================
CREATE OR REPLACE VIEW vue_commandes_detaillees AS
SELECT
    c.id_commande,
    c.date_commande,
    c.statut,
    u.id_utilisateur AS id_client,
    u.nom,
    u.prenom,
    p.nom_produit,
    lc.quantite,
    lc.prix_unitaire,
    lc.montant_ligne
FROM commande c
JOIN client cl ON c.id_client = cl.id_utilisateur
JOIN utilisateur u ON cl.id_utilisateur = u.id_utilisateur
JOIN ligne_commande lc ON c.id_commande = lc.id_commande
JOIN produit p ON lc.id_produit = p.id_produit;

-- =====================================================
-- VUE 3 : Historique des ventes
-- =====================================================
CREATE OR REPLACE VIEW vue_ventes AS
SELECT
    v.id_vente,
    v.date_vente,
    v.chiffre_affaires,
    c.id_commande,
    u.id_utilisateur AS id_client,
    u.nom,
    u.prenom
FROM vente v
JOIN commande c ON v.id_commande = c.id_commande
JOIN client cl ON c.id_client = cl.id_utilisateur
JOIN utilisateur u ON cl.id_utilisateur = u.id_utilisateur;

-- =====================================================
-- VUE 4 : Chiffre d’affaires par produit
-- =====================================================
CREATE OR REPLACE VIEW vue_ca_par_produit AS
SELECT
    p.id_produit,
    p.nom_produit,
    SUM(lc.quantite) AS total_vendu,
    SUM(lc.montant_ligne) AS chiffre_affaires
FROM ligne_commande lc
JOIN produit p ON lc.id_produit = p.id_produit
JOIN commande c ON lc.id_commande = c.id_commande
WHERE c.statut = 'ACCEPTEE'
GROUP BY p.id_produit, p.nom_produit;

-- =====================================================
-- VUE 5 : Alertes de stock
-- =====================================================
CREATE OR REPLACE VIEW vue_alertes_stock AS
SELECT
    a.id_alerte,
    a.date_alerte,
    a.message,
    a.statut,
    p.nom_produit
FROM alerte_stock a
JOIN produit p ON a.id_produit = p.id_produit;

-- =====================================================
-- VUE 6 : Clients + nombre de commandes
-- =====================================================
CREATE OR REPLACE VIEW vue_clients_commandes AS
SELECT
    u.id_utilisateur,
    u.nom,
    u.prenom,
    u.email,
    COUNT(c.id_commande) AS nombre_commandes
FROM utilisateur u
JOIN client cl ON u.id_utilisateur = cl.id_utilisateur
LEFT JOIN commande c ON cl.id_utilisateur = c.id_client
GROUP BY u.id_utilisateur, u.nom, u.prenom, u.email;

-- =====================================================
-- FIN DES VUES MÉTIER
-- =====================================================
