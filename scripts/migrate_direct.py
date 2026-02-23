#!/usr/bin/env python3
"""
Script direct pour appliquer la migration sans input utilisateur
"""
import psycopg2
from datetime import datetime

DATABASE_URL = "postgresql://postgres:BKqzqRgVhpCESb8zXbmvdJRWJBfbS2Md@dpg-d6bcpsbuibrs73ekh320-a.frankfurt-postgres.render.com/mokpokpo_bd"

print("=" * 70)
print("🔄 MIGRATION: Soft Delete + URL Images (AUTO)")
print("=" * 70)

print("\n🔐 Connexion à Render PostgreSQL...")
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print("✅ Connexion établie!")
except Exception as e:
    print(f"❌ Erreur: {e}")
    exit(1)

# Commandes de migration
migrations = [
    ("Utilisateur.actif", "ALTER TABLE utilisateur ADD COLUMN IF NOT EXISTS actif BOOLEAN NOT NULL DEFAULT TRUE;"),
    ("Index utilisateur.actif", "CREATE INDEX IF NOT EXISTS idx_utilisateur_actif ON utilisateur(actif);"),
    ("Client.actif", "ALTER TABLE client ADD COLUMN IF NOT EXISTS actif BOOLEAN NOT NULL DEFAULT TRUE;"),
    ("Index client.actif", "CREATE INDEX IF NOT EXISTS idx_client_actif ON client(actif);"),
    ("Vente.deleted_at", "ALTER TABLE vente ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;"),
    ("Index vente.deleted_at", "CREATE INDEX IF NOT EXISTS idx_vente_deleted_at ON vente(deleted_at);"),
    ("Produit.url_image", "ALTER TABLE produit ADD COLUMN IF NOT EXISTS url_image TEXT;"),
]

print("\n🚀 Exécution de la migration...")
executed = 0

for name, sql in migrations:
    try:
        cursor.execute(sql)
        print(f"✅ {name}")
        executed += 1
    except psycopg2.errors.DuplicateColumn:
        print(f"⚠️  {name} → Colonne déjà existante (ignoré)")
    except Exception as e:
        if "already exists" in str(e):
            print(f"⚠️  {name} → {e}")
        else:
            print(f"❌ {name} → {e}")

# Commit
try:
    conn.commit()
    print(f"\n✅ Migration appliquée! ({executed} commandes exécutées)")
except Exception as e:
    conn.rollback()
    print(f"❌ Commit échoué: {e}")
    exit(1)

# Vérification
print("\n📊 Vérification...")
verifications = [
    ("utilisateur.actif", "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='utilisateur' AND column_name='actif'"),
    ("client.actif", "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='client' AND column_name='actif'"),
    ("vente.deleted_at", "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='vente' AND column_name='deleted_at'"),
    ("produit.url_image", "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='produit' AND column_name='url_image'"),
]

all_ok = True
for name, query in verifications:
    cursor.execute(query)
    count = cursor.fetchone()[0]
    if count == 1:
        print(f"✅ {name}")
    else:
        print(f"❌ {name}")
        all_ok = False

cursor.close()
conn.close()

if all_ok:
    print("\n" + "=" * 70)
    print("🎉 MIGRATION RÉUSSIE!")
    print("=" * 70)
else:
    print("\n⚠️  Certaines colonnes manquent!")
    exit(1)
