import os
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.model import Vente, Commande, LigneCommande, Produit
from datetime import datetime, timedelta
import json

# Configuration de Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

class PredictionService:
    def __init__(self, db: Session):
        self.db = db

    def get_historical_sales_data(self, days: int = 90):
        """
        Extrait les données de ventes agrégées par jour pour les 'days' derniers jours.
        """
        start_date = datetime.now() - timedelta(days=days)
        
        # Agrégation des ventes par jour
        sales = self.db.query(
            func.date(Vente.date_vente).label("date"),
            func.sum(Vente.chiffre_affaires).label("total_ca")
        ).filter(Vente.date_vente >= start_date)\
         .group_by(func.date(Vente.date_vente))\
         .order_by(func.date(Vente.date_vente))\
         .all()
        
        return [{"date": str(s.date), "ca": float(s.total_ca)} for s in sales]

    def get_top_products_data(self, limit: int = 5):
        """
        Extrait les produits les plus vendus.
        """
        top_products = self.db.query(
            Produit.nom_produit,
            func.sum(LigneCommande.quantite).label("quantite_totale")
        ).join(LigneCommande)\
         .group_by(Produit.id_produit)\
         .order_by(func.sum(LigneCommande.quantite).desc())\
         .limit(limit)\
         .all()
        
        return [{"produit": p.nom_produit, "quantite": int(p.quantite_totale)} for p in top_products]

    async def predict_sales(self):
        """
        Génère une prédiction de ventes via Gemini.
        """
        if not GOOGLE_API_KEY:
            return {"error": "Clé API Google non configurée"}

        sales_data = self.get_historical_sales_data()
        top_products = self.get_top_products_data()

        if not sales_data:
            return {"message": "Pas assez de données pour effectuer une prédiction"}

        # Construction du prompt pour Gemini
        prompt = f"""
        Tu es un expert en analyse de données commerciales pour une ferme.
        Voici les données historiques de ventes des 90 derniers jours :
        {json.dumps(sales_data)}

        Voici les produits les plus vendus :
        {json.dumps(top_products)}

        En te basant sur ces données, fournis moi :
        1. Une prévision du chiffre d'affaires pour les 7 prochains jours.
        2. Une identification des tendances ou périodes de fortes ventes à venir.
        3. Des recommandations pour la gestion des stocks.

        Réponds en format JSON structuré avec les clés suivantes :
        - forecast_7_days: (nombre)
        - trends: (string)
        - recommendations: (list of strings)
        - analysis_text: (brief paragraph summary)
        """

        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(prompt)
            # On essaie d'extraire le JSON de la réponse
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                 text = text.split("```")[1].split("```")[0].strip()
            
            return json.loads(text)
        except Exception as e:
            return {"error": f"Erreur lors de la génération de la prédiction : {str(e)}"}
