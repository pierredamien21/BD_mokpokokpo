#!/usr/bin/env python3
"""
Script pour appliquer la migration FEFO sur Render PostgreSQL
Crée la table LOT et met à jour LIGNE_COMMANDE pour FEFO
"""

import os
import psycopg2
from psycopg2 import sql, Error
from dotenv import load_dotenv
from pathlib import Path

# Charger .env
env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ ERREUR: DATABASE_URL non trouvée dans .env")
    exit(1)

# Parser la URL (format: postgresql://user:password@host:port/db)
try:
    # Remplacer postgresql:// par postgresql+psycopg2:// pour SQLAlchemy
    db_url = DATABASE_URL.replace("postgresql://", "")
    parts = db_url.split("@")
    credentials = parts[0].split(":")
    host_db = parts[1].split("/")
    
    db_user = credentials[0]
    db_password = credentials[1]
    db_host = host_db[0]
    db_name = host_db[1]
    
    print(f"🔐 Connexion à PostgreSQL...")
    print(f"   Host: {db_host}")
    print(f"   DB: {db_name}")
    print(f"   User: {db_user}")
    
except Exception as e:
    print(f"❌ Erreur parsing DATABASE_URL: {e}")
    exit(1)

# Migration SQL
MIGRATION_SQL = """
-- ======================================================================
-- 🚀 MIGRATION FEFO (First Expired First Out)
-- ======================================================================

-- 1. Créer table LOT
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

-- 2. Index FEFO (tri par date expiration)
CREATE INDEX IF NOT EXISTS idx_lot_date_expiration 
    ON lot(id_produit, date_expiration ASC) 
    WHERE quantite_restante > 0;

-- 3. Index pour alertes
CREATE INDEX IF NOT EXISTS idx_lot_date_fabrication 
    ON lot(date_fabrication DESC);

-- 4. Index stock
CREATE INDEX IF NOT EXISTS idx_lot_id_stock 
    ON lot(id_stock);

-- 5. Index lot actif
CREATE INDEX IF NOT EXISTS idx_lot_actif 
    ON lot(id_produit, quantite_restante) 
    WHERE quantite_restante > 0 AND date_expiration > CURRENT_TIMESTAMP;

-- 6. Ajouter colonne id_lot à LIGNE_COMMANDE
ALTER TABLE ligne_commande 
ADD COLUMN IF NOT EXISTS id_lot INTEGER REFERENCES lot(id_lot) ON DELETE SET NULL;

-- 7. Index ligne_commande par lot
CREATE INDEX IF NOT EXISTS idx_ligne_commande_id_lot 
    ON ligne_commande(id_lot) 
    WHERE id_lot IS NOT NULL;

-- 8. Améliorer ALERTE_STOCK pour alertes expiration
ALTER TABLE alerte_stock 
ADD COLUMN IF NOT EXISTS type_alerte VARCHAR(20) DEFAULT 'QUANTITE';
-- Types: 'QUANTITE', 'JAUNE' (J-90), 'ORANGE' (J-60), 'ROUGE' (J-30), 'EXPIRÉ'

ALTER TABLE alerte_stock 
ADD COLUMN IF NOT EXISTS id_lot INTEGER REFERENCES lot(id_lot) ON DELETE CASCADE;

-- Index pour alertes pas lot
CREATE INDEX IF NOT EXISTS idx_alerte_stock_id_lot 
    ON alerte_stock(id_lot) 
    WHERE id_lot IS NOT NULL;

"""

try:
    # Connexion
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    
    cursor = conn.cursor()
    print("✅ Connexion établie!\n")
    
    # Exécuter migration
    print("🚀 Exécution de la migration...")
    cursor.execute(MIGRATION_SQL)
    
    print("✅ Migration appliquée!\n")
    
    # Vérifications
    print("📊 Vérification des changements...\n")
    
    # Vérifier table lot
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'lot'
        );
    """)
    if cursor.fetchone()[0]:
        print("✅ Table LOT créée")
    
    # Vérifier colonne id_lot in ligne_commande
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'ligne_commande' AND column_name = 'id_lot'
        );
    """)
    if cursor.fetchone()[0]:
        print("✅ Colonne LINE_COMMANDE.id_lot créée")
    
    # Vérifier colonne type_alerte in alerte_stock
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'alerte_stock' AND column_name = 'type_alerte'
        );
    """)
    if cursor.fetchone()[0]:
        print("✅ Colonne ALERTE_STOCK.type_alerte créée")
    
    # Compter les index
    cursor.execute("""
        SELECT COUNT(*) FROM pg_indexes 
        WHERE tablename = 'lot';
    """)
    lot_indexes = cursor.fetchone()[0]
    print(f"✅ {lot_indexes} index créés sur table LOT")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("🎉 MIGRATION FEFO RÉUSSIE!")
    print("=" * 70)
    print("\n📌 Prochaines étapes:")
    print("   1. Créer des lots: POST /lots")
    print("   2. Valider commande avec FEFO: POST /commandes/{id}/valider")
    print("   3. Consulter lots: GET /lots")
    print("   4. Dashboard: GET /lots/dashboard/resumé")
    
except Error as e:
    print(f"❌ Erreur PostgreSQL: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Erreur: {type(e).__name__}: {e}")
    exit(1)
