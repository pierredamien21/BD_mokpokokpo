import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine

def fix_sequence():
    print("🔧 Correction de la séquence d'IDs...")
    with engine.connect() as conn:
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
        try:
            # Récupère max ID
            result = conn.execute(text("SELECT MAX(id_utilisateur) FROM utilisateur"))
            max_id = result.scalar() or 0
            print(f"Max ID actuel : {max_id}")
            
            # Reset sequence
            # Le nom de la séquence est généralement table_colonne_seq
            seq_name = "utilisateur_id_utilisateur_seq"
            # setval(seq, max_id) fait que le prochain sera max_id + 1
            query = text(f"SELECT setval('{seq_name}', {max_id});")
            conn.execute(query)
            print(f"✅ Séquence '{seq_name}' réinitialisée à {max_id}")
        except Exception as e:
            print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    fix_sequence()
