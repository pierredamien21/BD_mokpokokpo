import os
import joblib
import numpy as np
import pandas as pd
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.model import Vente, Commande, LigneCommande, Produit, Stock
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration de Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    logger.info("✅ API Gemini configurée")
else:
    logger.warning("⚠️ GOOGLE_API_KEY non trouvée dans l'environnement")

# Charger le modèle RandomForest
MODEL_PATH = Path(__file__).parent.parent / "AI" / "modele_ventes.pkl"
MODELE_ML = None
if MODEL_PATH.exists():
    try:
        MODELE_ML = joblib.load(str(MODEL_PATH))
        logger.info(f"✅ Modèle ML chargé depuis {MODEL_PATH}")
        logger.info(f"   Type: {type(MODELE_ML).__name__}")
    except Exception as e:
        logger.error(f"❌ Erreur chargement modèle ML: {e}")
else:
    logger.error(f"❌ Fichier modèle ML introuvable: {MODEL_PATH}")

class PredictionService:
    def __init__(self, db: Session):
        self.db = db
        self.model = MODELE_ML
        if self.model is None:
            logger.warning("⚠️ PredictionService initialisé SANS modèle ML")
        else:
            logger.debug("✅ PredictionService initialisé avec modèle ML")

    def get_historical_sales_data(self, days: int = 90):
        """
        Extrait les données de ventes agrégées par jour pour les 'days' derniers jours.
        """
        logger.debug(f"Récupération historique sur {days} jours")
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Agrégation des ventes par jour
            sales = self.db.query(
                func.date(Vente.date_vente).label("date"),
                func.sum(Vente.chiffre_affaires).label("total_ca")
            ).filter(Vente.date_vente >= start_date)\
             .group_by(func.date(Vente.date_vente))\
             .order_by(func.date(Vente.date_vente))\
             .all()
            
            result = [{"date": str(s.date), "ca": float(s.total_ca)} for s in sales]
            logger.info(f"📈 {len(result)} jours d'historique récupérés")
            return result
        except Exception as e:
            logger.error(f"❌ Erreur récupération historique: {e}")
            return []

    def get_top_products_data(self, limit: int = 5):
        """
        Extrait les produits les plus vendus.
        """
        logger.debug(f"Récupération top {limit} produits")
        try:
            top_products = self.db.query(
                Produit.nom_produit,
                func.sum(LigneCommande.quantite).label("quantite_totale")
            ).join(LigneCommande)\
             .group_by(Produit.id_produit)\
             .order_by(func.sum(LigneCommande.quantite).desc())\
             .limit(limit)\
             .all()
            
            result = [{"produit": p.nom_produit, "quantite": int(p.quantite_totale)} for p in top_products]
            logger.info(f"📊 Top {len(result)} produits récupérés")
            return result
        except Exception as e:
            logger.error(f"❌ Erreur récupération top produits: {e}")
            return []

    def prepare_features_for_product(self, product_id: int) -> dict:
        """
        Prépare les 15 features requises par le modèle RandomForest
        Features: product_id, product_type_enc, prix_unitaire, stock_initial, seuil_minimal,
                  commandes_acceptees, reservations, day_of_week, is_weekend, is_holiday,
                  lag_1_ventes, lag_2_ventes, lag_3_ventes, lag_7_ventes, rolling_mean_3
        """
        logger.debug(f"🔧 Préparation features pour produit {product_id}")
        try:
            produit = self.db.query(Produit).filter(Produit.id_produit == product_id).first()
            if not produit:
                logger.warning(f"⚠️ Produit {product_id} introuvable")
                return None
            
            stock = self.db.query(Stock).filter(Stock.id_produit == product_id).first()
            
            # Encodage type produit (simple hash)
            product_type_enc = hash(produit.type_produit or "unknown") % 100
            
            # Commandes acceptées pour ce produit
            commandes_prod = self.db.query(func.count(LigneCommande.id_ligne_commande)).join(
                Commande, Commande.id_commande == LigneCommande.id_commande
            ).filter(
                LigneCommande.id_produit == product_id,
                Commande.statut == "ACCEPTEE"
            ).scalar() or 0
            
            # Réservations
            reservations = self.db.query(func.count(LigneCommande.id_ligne_commande)).filter(
                LigneCommande.id_produit == product_id
            ).scalar() or 0
            
            # Données temporelles
            now = datetime.now()
            day_of_week = now.weekday()
            is_weekend = 1 if day_of_week >= 5 else 0
            is_holiday = 0  # À implémenter avec calendar si besoin
            
            # Lags de ventes (derniers 1, 2, 3, 7 jours)
            today = datetime.now().date()
            lag_1 = self.db.query(func.sum(Vente.quantite_vendue)).filter(
                Vente.id_produit == product_id,
                func.date(Vente.date_vente) == today - timedelta(days=1)
            ).scalar() or 0
            
            lag_2 = self.db.query(func.sum(Vente.quantite_vendue)).filter(
                Vente.id_produit == product_id,
                func.date(Vente.date_vente) == today - timedelta(days=2)
            ).scalar() or 0
            
            lag_3 = self.db.query(func.sum(Vente.quantite_vendue)).filter(
                Vente.id_produit == product_id,
                func.date(Vente.date_vente) == today - timedelta(days=3)
            ).scalar() or 0
            
            lag_7 = self.db.query(func.sum(Vente.quantite_vendue)).filter(
                Vente.id_produit == product_id,
                func.date(Vente.date_vente) == today - timedelta(days=7)
            ).scalar() or 0
            
            # Moyenne mobile 3 jours
            rolling_mean_3 = np.mean([lag_1, lag_2, lag_3]) if any([lag_1, lag_2, lag_3]) else 0
            
            features = {
                "product_id": float(product_id),
                "product_type_enc": float(product_type_enc),
                "prix_unitaire": float(produit.prix_unitaire or 0),
                "stock_initial": float(stock.quantite_disponible if stock else 0),
                "seuil_minimal": float(stock.seuil_minimal if stock else 0),
                "commandes_acceptees": float(commandes_prod),
                "reservations": float(reservations),
                "day_of_week": float(day_of_week),
                "is_weekend": float(is_weekend),
                "is_holiday": float(is_holiday),
                "lag_1_ventes": float(lag_1),
                "lag_2_ventes": float(lag_2),
                "lag_3_ventes": float(lag_3),
                "lag_7_ventes": float(lag_7),
                "rolling_mean_3": float(rolling_mean_3)
            }
            
            logger.debug(f"✅ Features OK pour produit {product_id} ({produit.nom_produit})")
            return features
        
        except Exception as e:
            logger.error(f"❌ Erreur préparation features pour produit {product_id}: {e}")
            return None

    def predict_sales_by_product(self):
        """
        Prédit les ventes pour tous les produits sur les 7 prochains jours
        Utilise le modèle RandomForest
        """
        logger.info("🔮 Démarrage prédictions ML pour tous les produits")
        
        if not self.model:
            error_msg = "Modèle ML non chargé"
            logger.error(f"❌ {error_msg}")
            return {"error": error_msg, "error_type": "ml_model_not_loaded"}
        
        try:
            produits = self.db.query(Produit).all()
            logger.info(f"📊 {len(produits)} produits à analyser")
            predictions = []
            
            for produit in produits:
                features_dict = self.prepare_features_for_product(produit.id_produit)
                if not features_dict:
                    logger.warning(f"⏭️ Skip produit {produit.id_produit} (features manquantes)")
                    continue
                
                # Construire le vecteur dans l'ordre des features du modèle
                features_order = [
                    'product_id', 'product_type_enc', 'prix_unitaire', 'stock_initial',
                    'seuil_minimal', 'commandes_acceptees', 'reservations', 'day_of_week',
                    'is_weekend', 'is_holiday', 'lag_1_ventes', 'lag_2_ventes', 'lag_3_ventes',
                    'lag_7_ventes', 'rolling_mean_3'
                ]
                
                X = np.array([[features_dict[f] for f in features_order]])
                
                try:
                    pred_7_days = self.model.predict(X)[0]
                    
                    predictions.append({
                        "product_id": produit.id_produit,
                        "nom_produit": produit.nom_produit,
                        "type_produit": produit.type_produit,
                        "prix_unitaire": float(produit.prix_unitaire),
                        "predicted_sales_7_days": round(float(pred_7_days), 2),
                        "confidence": "High"  # RandomForest a bonne confiance
                    })
                    
                    logger.debug(f"   ✓ {produit.nom_produit}: {pred_7_days:.2f} unités prévues")
                    
                except Exception as e:
                    logger.error(f"❌ Erreur prédiction produit {produit.id_produit}: {e}")
            
            result = sorted(predictions, key=lambda x: x['predicted_sales_7_days'], reverse=True)
            logger.info(f"✅ {len(result)} prédictions générées avec succès")
            return result
        
        except Exception as e:
            error_msg = f"Erreur globale prédiction: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {"error": error_msg, "error_type": "prediction_failed"}

    async def predict_sales(self):
        """
        Combine prédictions ML + recommandations Gemini
        1. RandomForest prédit les ventes par produit
        2. Gemini fournit des recommandations intelligentes
        """
        logger.info("🚀 Démarrage prédiction complète (ML + Gemini)")
        
        # Étape 1: Prédictions ML
        ml_predictions = self.predict_sales_by_product()
        
        if isinstance(ml_predictions, dict) and "error" in ml_predictions:
            logger.error(f"❌ Échec ML: {ml_predictions.get('error')}")
            return ml_predictions
        
        if not ml_predictions or isinstance(ml_predictions, dict):
            logger.warning("⚠️ Pas assez de données pour prédiction")
            return {"message": "Pas assez de données pour effectuer une prédiction"}
        
        # Étape 2: Calculs de synthèse
        total_predicted_sales = sum(p['predicted_sales_7_days'] for p in ml_predictions)
        top_3_products = ml_predictions[:3] if len(ml_predictions) >= 3 else ml_predictions
        
        logger.info(f"📊 Total prévu 7 jours: {total_predicted_sales:.2f} unités")
        
        # Étape 3: Données pour Gemini
        sales_data = self.get_historical_sales_data(days=30)
        
        if not GOOGLE_API_KEY:
            logger.warning("⚠️ API Gemini non configurée, retour ML seulement")
            return {
                "ml_predictions": ml_predictions,
                "summary": {
                    "total_predicted_sales_7_days": round(total_predicted_sales, 2),
                    "top_products": top_3_products,
                    "note": "Prédictions ML chargées (recommandations Gemini non disponibles)"
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Étape 4: Prompt pour Gemini avec données ML
        prompt = f"""
Tu es un expert en gestion agricole et en supply chain pour une ferme.

DONNÉES HISTORIQUES (30 derniers jours):
{json.dumps(sales_data)}

PRÉDICTIONS ML (RandomForest) - VENTES ATTENDUES 7 PROCHAINS JOURS:
{json.dumps(top_3_products)}

Total prévu 7 jours: {total_predicted_sales} unités

En te basant sur ces données RÉELLES de prédiction ML, fournis moi:

1. **Analyse des tendances**: Quels sont les patterns identifiés par le ML?
2. **Recommandations de stock**: Devrait-on augmenter/diminuer le stock pour ces produits?
3. **Stratégie de prix**: Y a-t-il des opportunités de prix dynamique?
4. **Risques identifiés**: Quels produits risquent une rupture de stock?
5. **Actions prioritaires**: 3 actions concrètes à prendre cette semaine

Réponds en format JSON avec ces clés:
{{
  "trends_analysis": "paragraph concis",
  "stock_recommendations": ["rec1", "rec2", "rec3"],
  "pricing_strategy": "string",
  "risk_assessment": ["risque1", "risque2"],
  "priority_actions": ["action1", "action2", "action3"]
}}
"""
        
        try:
            logger.info("🤖 Appel API Gemini pour recommandations...")
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(prompt)
            
            # Extraction du JSON
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            gemini_recommendations = json.loads(text)
            logger.info("✅ Recommandations Gemini reçues et parsées")
            
            return {
                "ml_predictions": ml_predictions,
                "summary": {
                    "total_predicted_sales_7_days": round(total_predicted_sales, 2),
                    "top_products": top_3_products
                },
                "gemini_recommendations": gemini_recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur parsing JSON Gemini: {e}")
            logger.debug(f"Raw response: {text[:200]}...")
            # Retourner les prédictions ML même si Gemini échoue
            return {
                "ml_predictions": ml_predictions,
                "summary": {
                    "total_predicted_sales_7_days": round(total_predicted_sales, 2),
                    "top_products": top_3_products
                },
                "gemini_error": f"JSON parsing failed: {str(e)}",
                "error_type": "gemini_json_parse_error",
                "note": "Prédictions ML disponibles, recommandations Gemini échouées",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur API Gemini: {e}")
            # Retourner les prédictions ML même si Gemini échoue
            return {
                "ml_predictions": ml_predictions,
                "summary": {
                    "total_predicted_sales_7_days": round(total_predicted_sales, 2),
                    "top_products": top_3_products
                },
                "gemini_error": str(e),
                "error_type": "gemini_api_error",
                "note": "Prédictions ML disponibles, recommandations Gemini échouées",
                "timestamp": datetime.now().isoformat()
            }
