import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
from models.model import Utilisateur

def check_users():
    db = SessionLocal()
    users = db.query(Utilisateur).all()
    print(f"Nombre d'utilisateurs: {len(users)}")
    for u in users:
        print(f"ID: {u.id_utilisateur} | Email: {u.email} | Role: {u.role}")

if __name__ == "__main__":
    check_users()
