SET search_path TO public;

-- ============================================
-- TRIGGER : Interdire le stock négatif
-- ============================================

CREATE OR REPLACE FUNCTION verifier_stock_non_negatif()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.quantite_disponible < 0 THEN
        RAISE EXCEPTION
            'Stock insuffisant : opération refusée (produit_id = %, stock = %)',
            NEW.id_produit,
            NEW.quantite_disponible;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_blocage_stock_negatif
BEFORE UPDATE OF quantite_disponible
ON stock
FOR EACH ROW
EXECUTE FUNCTION verifier_stock_non_negatif();

-- ============================================
-- TRIGGER : Décrémenter le stock après commande
-- ============================================

CREATE OR REPLACE FUNCTION maj_stock_apres_commande()
RETURNS TRIGGER AS $$
BEGIN
    -- Décrémenter le stock pour chaque ligne de commande
    UPDATE stock s
    SET quantite_disponible = s.quantite_disponible - lc.quantite,
        date_derniere_mise_a_jour = CURRENT_TIMESTAMP
    FROM ligne_commande lc
    WHERE lc.id_commande = NEW.id_commande
      AND s.id_produit = lc.id_produit;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_maj_stock_commande_acceptee
AFTER UPDATE OF statut
ON commande
FOR EACH ROW
WHEN (NEW.statut = 'ACCEPTEE' AND OLD.statut <> 'ACCEPTEE')
EXECUTE FUNCTION maj_stock_apres_commande();

-- ============================================
-- TRIGGER : Alerte stock bas
-- ============================================

CREATE OR REPLACE FUNCTION alerte_stock_bas()
RETURNS TRIGGER AS $$
BEGIN
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
            'Alerte automatique : stock bas',
            'ENVOYEE',
            NEW.seuil_minimal,
            NEW.id_produit
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_alerte_stock_bas
AFTER UPDATE OF quantite_disponible
ON stock
FOR EACH ROW
EXECUTE FUNCTION alerte_stock_bas();
