import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine

def fix_database():
    print("🔧 Réparation de la base de données (Mode séquentiel)...")
    
    # Liste des commandes à exécuter séquentiellement
    # On isole chaque commande pour éviter qu'une erreur bloque tout
    commands = [
        "ALTER TABLE utilisateur ADD COLUMN IF NOT EXISTS role VARCHAR(30);",
        "UPDATE utilisateur SET role='CLIENT' WHERE role IS NULL;",
        "ALTER TABLE utilisateur ALTER COLUMN role SET NOT NULL;",
        # On tente de dropper la contrainte si elle existe (peut échouer si inexistante, pas grave)
        "ALTER TABLE utilisateur DROP CONSTRAINT IF EXISTS ck_utilisateur_role;",
        "ALTER TABLE utilisateur ADD CONSTRAINT ck_utilisateur_role CHECK (role IN ('CLIENT', 'GEST_STOCK', 'GEST_COMMERCIAL', 'ADMIN'));"
    ]
    
    with engine.connect() as conn:
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
        for cmd in commands:
            try:
                print(f"Exécution : {cmd[:50]}...")
                conn.execute(text(cmd))
            except Exception as e:
                print(f"⚠️ Note : {e}")
                
    print("✅ Tentative de réparation terminée.")

if __name__ == "__main__":
    fix_database()
