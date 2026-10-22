"""
Script pour appliquer la migration SQL à la base de données Render
Ajoute les colonnes: actif (utilisateur, client), deleted_at (vente), url_image (produit)
"""
import sys
import os
import psycopg2
from psycopg2 import sql

# URL de la base : variable d'environnement DATABASE_URL (voir .env.example)
DATABASE_URL = os.environ["DATABASE_URL"]

def run_migration():
    """Exécuter la migration SQL"""
    print("=" * 70)
    print("🔄 MIGRATION: Soft Delete + URL Images")
    print("=" * 70)
    
    # Lire le fichier SQL
    migration_file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "tables_index_tiggers",
        "migration_soft_delete_and_images.sql"
    )
    
    try:
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
    except FileNotFoundError:
        print(f"❌ Fichier de migration introuvable: {migration_file}")
        return False
    
    # Connexion à la base de données
    print("\n🔐 Connexion à la base de données Render...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False  # Transaction manuelle
        cursor = conn.cursor()
        print("✅ Connexion établie!")
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        return False
    
    # Exécution de la migration
    print("\n🚀 Exécution de la migration...")
    try:
        # Séparer les commandes SQL
        commands = [cmd.strip() for cmd in migration_sql.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
        
        total_commands = len(commands)
        executed = 0
        
        for i, command in enumerate(commands, 1):
            # Ignorer les commentaires et les SELECT de vérification
            if command.strip().upper().startswith('SELECT'):
                print(f"[{i}/{total_commands}] ⏭️  Vérification ignorée (exécutez manuellement si nécessaire)")
                continue
            
            print(f"[{i}/{total_commands}] Exécution...")
            try:
                cursor.execute(command)
                executed += 1
                print(f"   ✅ OK")
            except Exception as e:
                error_msg = str(e)
                # Ignorer les erreurs "column already exists"
                if "already exists" in error_msg:
                    print(f"   ⚠️  Colonne déjà existante (ignoré)")
                else:
                    print(f"   ❌ Erreur: {error_msg}")
                    raise
        
        # Commit de la transaction
        conn.commit()
        print(f"\n✅ Migration appliquée avec succès! ({executed} commandes exécutées)")
        
        # Vérification finale
        print("\n📊 Vérification des colonnes ajoutées...")
        
        verification_queries = [
            ("utilisateur.actif", "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='utilisateur' AND column_name='actif'"),
            ("client.actif", "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='client' AND column_name='actif'"),
            ("vente.deleted_at", "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='vente' AND column_name='deleted_at'"),
            ("produit.url_image", "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='produit' AND column_name='url_image'"),
        ]
        
        all_ok = True
        for col_name, query in verification_queries:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            if count == 1:
                print(f"   ✅ {col_name}")
            else:
                print(f"   ❌ {col_name} - NON CRÉÉE!")
                all_ok = False
        
        cursor.close()
        conn.close()
        
        if all_ok:
            print("\n" + "=" * 70)
            print("🎉 MIGRATION TERMINÉE AVEC SUCCÈS!")
            print("=" * 70)
            print("\n💡 Prochaines étapes:")
            print("   1. Tester les endpoints DELETE sur Render")
            print("   2. Re-peupler les produits avec url_image:")
            print("      python scripts/clean_products.py")
            print("      python scripts/populate_api.py")
            return True
        else:
            print("\n⚠️  Certaines colonnes n'ont pas été créées correctement!")
            return False
            
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur lors de la migration: {str(e)}")
        print("🔄 Rollback effectué - aucune modification appliquée")
        cursor.close()
        conn.close()
        return False

if __name__ == "__main__":
    print("\n⚠️  ATTENTION: Cette migration va modifier la structure de la base de données!")
    print("📋 Modifications prévues:")
    print("   - utilisateur: ajout colonne 'actif' (BOOLEAN)")
    print("   - client: ajout colonne 'actif' (BOOLEAN)")
    print("   - vente: ajout colonne 'deleted_at' (TIMESTAMP)")
    print("   - produit: ajout colonne 'url_image' (TEXT)")
    print()
    
    confirm = input("Taper 'OUI' pour confirmer: ")
    
    if confirm.strip().upper() == "OUI":
        success = run_migration()
        sys.exit(0 if success else 1)
    else:
        print("\n❌ Migration annulée.")
        sys.exit(1)
