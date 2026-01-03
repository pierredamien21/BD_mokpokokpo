import sys
import os

# Ajout du dossier parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.model import Utilisateur
from security.hashing import hash_password
from schema.enums import RoleEnum

def create_admin():
    db = SessionLocal()
    
    print("--- Création d'un Administrateur ---")
    nom = input("Nom: ")
    prenom = input("Prénom: ")
    email = input("Email: ")
    password = input("Mot de passe: ")
    
    # Vérification existence
    existing = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if existing:
        print("❌ Erreur: Cet email existe déjà.")
        return

    admin = Utilisateur(
        nom=nom,
        prenom=prenom,
        email=email,
        mot_de_passe=hash_password(password),
        role=RoleEnum.ADMIN
    )
    
    db.add(admin)
    db.commit()
    print(f"Administrateur {email} créé avec succès !")

if __name__ == "__main__":
    create_admin()
