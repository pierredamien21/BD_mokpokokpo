import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

#  1. Charge le fichier .env
load_dotenv()

#  2. Récupère SANS valeur par défaut contenant le mot de passe
DATABASE_URL = os.getenv("DATABASE_URL")

#  3. Si .env n'existe pas ou DATABASE_URL manquant : ERREUR
if not DATABASE_URL:
    print(" ERREUR: Fichier .env manquant ou DATABASE_URL non défini")
    print("Créez un fichier .env avec:")
    print("   DATABASE_URL=postgresql://user:password@localhost:5433/dbname")
    print(" Ou copiez: cp .env.example .env")
    raise ValueError("Configuration base de données manquante")

#  4. Masquage pour l'affichage
def mask_password(url):
    """Masque le mot de passe dans l'URL"""
    try:
        if "://" in url and "@" in url:
            protocol = url.split("://")[0]
            rest = url.split("://")[1]
            if "@" in rest:
                before_at = rest.split("@")[0]
                after_at = rest.split("@")[1]
                if ":" in before_at:
                    user = before_at.split(":")[0]
                    return f"{protocol}://{user}:****@{after_at}"
    except:
        pass
    return "postgresql://****@****"

print(f"🔗 {mask_password(DATABASE_URL)}")

#  5. Configuration SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test
try:
    with engine.connect():
        print("Connexion PostgreSQL réussie")
except Exception as e:
    print(f"Erreur: {str(e)[:100]}...")
    raise