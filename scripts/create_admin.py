import sys
import os

# Ajout du dossier parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.model import Utilisateur
from security.hashing import hash_password
from schema.enums import RoleEnum

def create_user(nom=None, prenom=None, email=None, password=None, role=None):
    db = SessionLocal()
    
    if not role:
        role = "ADMIN"
    
    print(f"--- Création d'un utilisateur ({role}) ---")
    
    if not nom:
        nom = input("Nom: ")
    if not prenom:
        prenom = input("Prénom: ")
    if not email:
        email = input("Email: ")
    if not password:
        password = input("Mot de passe: ")
    
    # Vérification existence
    existing = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if existing:
        print(" Erreur: Cet email existe déjà.")
        return False

    user = Utilisateur(
        nom=nom,
        prenom=prenom,
        email=email,
        mot_de_passe=hash_password(password),
        role=role
    )
    
    db.add(user)
    db.commit()
    print(f" Utilisateur {email} ({role}) créé avec succès !")
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 4:
        role = sys.argv[5] if len(sys.argv) > 5 else "ADMIN"
        create_user(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], role)
    else:
        create_user()
