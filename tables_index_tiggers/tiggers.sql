-- =====================================================
-- TRIGGERS AUTOMATIQUES - GESTION STOCK & ALERTES
-- Base : Mokpokpo
-- Schéma : public
-- =====================================================

SET search_path TO public;

-- =====================================================
-- TRIGGER 1 : Mise à jour automatique du stock
-- =====================================================
-- Objectif :
-- Lorsqu'une commande passe au statut 'ACCEPTEE',
-- le stock des produits concernés est décrémenté
-- selon les quantités commandées.
--
-- Pourquoi :
-- - Éviter les mises à jour manuelles
-- - Garantir la cohérence entre commandes et stock
-- =====================================================

CREATE OR REPLACE FUNCTION maj_stock_apres_commande()
RETURNS TRIGGER AS $$
BEGIN
    -- Décrémenter le stock pour chaque produit de la commande
    UPDATE stock s
    SET quantite_disponible = s.quantite_disponible - lc.quantite
    FROM ligne_commande lc
    WHERE lc.id_commande = NEW.id_commande
      AND s.id_produit = lc.id_produit;

    -- Mettre à jour la date de dernière modification du stock
    UPDATE stock
    SET date_derniere_mise_a_jour = CURRENT_TIMESTAMP
    WHERE id_produit IN (
        SELECT id_produit
        FROM ligne_commande
        WHERE id_commande = NEW.id_commande
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Déclenchement :
-- Le trigger s'exécute UNIQUEMENT lorsque le statut
-- d'une commande devient 'ACCEPTEE'
CREATE TRIGGER trg_maj_stock_apres_commande
AFTER UPDATE OF statut
ON commande
FOR EACH ROW
WHEN (NEW.statut = 'ACCEPTEE' AND OLD.statut <> 'ACCEPTEE')
EXECUTE FUNCTION maj_stock_apres_commande();

-- =====================================================
-- TRIGGER 2 : Alerte automatique de stock bas
-- =====================================================
-- Objectif :
-- Générer automatiquement une alerte lorsque
-- le stock devient inférieur ou égal au seuil minimal.
--
-- Pourquoi :
-- - Anticiper les ruptures de stock
-- - Alerter le gestionnaire de stock
-- =====================================================

CREATE OR REPLACE FUNCTION alerte_stock_bas()
RETURNS TRIGGER AS $$
BEGIN
    -- Vérifier si le stock est inférieur ou égal au seuil
    IF NEW.quantite_disponible <= NEW.seuil_minimal THEN
        INSERT INTO alerte_stock (
            date_alerte,
            message,
            statut,
            seuil_declencheur,
            id_produit
        )
        VALUES (
            CURRENT_TIMESTAMP,
            'Alerte : stock inférieur ou égal au seuil minimal',
            'ENVOYEE',
            NEW.seuil_minimal,
            NEW.id_produit
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Déclenchement :
-- Le trigger s'exécute après chaque modification
-- de la quantité disponible en stock
CREATE TRIGGER trg_alerte_stock_bas
AFTER UPDATE OF quantite_disponible
ON stock
FOR EACH ROW
EXECUTE FUNCTION alerte_stock_bas();


-- =====================================================
-- TRIGGER : Blocage du stock négatif
-- =====================================================
-- Objectif :
-- Empêcher toute mise à jour du stock qui entraînerait
-- une quantité disponible négative.
--
-- Pourquoi :
-- - Éviter les incohérences métier
-- - Garantir l'intégrité des données
-- - Forcer la logique "stock suffisant avant vente"
--
-- Ce trigger est exécuté AVANT toute mise à jour du stock
-- =====================================================

-- =====================================================
-- Fonction de contrôle du stock
-- =====================================================
CREATE OR REPLACE FUNCTION verifier_stock_non_negatif()
RETURNS TRIGGER AS $$
BEGIN
    -- Vérifier si la nouvelle quantité devient négative
    IF NEW.quantite_disponible < 0 THEN
        RAISE EXCEPTION
            'Opération refusée : stock négatif interdit (produit ID = %, stock demandé = %)',
            NEW.id_produit,
            NEW.quantite_disponible;
    END IF;

    -- Si tout est correct, autoriser l'opération
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Déclenchement du trigger
-- =====================================================
-- Le trigger s'exécute AVANT toute mise à jour
-- de la quantité disponible en stock
CREATE TRIGGER trg_blocage_stock_negatif
BEFORE UPDATE OF quantite_disponible
ON stock
FOR EACH ROW
EXECUTE FUNCTION verifier_stock_non_negatif();

-- =====================================================
-- FIN DU TRIGGER
-- =====================================================

-- =====================================================
-- FIN DES TRIGGERS
-- =====================================================
