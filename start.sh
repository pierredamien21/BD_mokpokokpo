#!/bin/bash
# Script de lancement du serveur API
# Utilise automatiquement l'environnement virtuel "nouveau_env"

# Se placer dans le dossier du script
cd "$(dirname "$0")"

# Vérifier si l'environnement existe
if [ ! -d "nouveau_env" ]; then
    echo "⚠️  L'environnement virtuel 'nouveau_env' est introuvable."
    echo "Installation des dépendances..."
    python3 -m venv nouveau_env
    ./nouveau_env/bin/pip install -r requirements.txt
fi

echo "🚀 Démarrage du serveur Mokpokpo..."
echo "👉 Documentation : http://127.0.0.1:8000/docs"
echo "-----------------------------------------------"

# Lancer Uvicorn via le python de l'environnement virtuel
./nouveau_env/bin/python -m uvicorn main:app --reload
