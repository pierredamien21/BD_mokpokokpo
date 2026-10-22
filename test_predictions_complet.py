#!/usr/bin/env python3
import os
"""
Script de test complet pour valider les corrections IA
Tests:
1. Endpoint /health (nouveau)
2. Authentification
3. Prédictions ML (/predictions/sales)
4. Format de réponse
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://bd-mokpokokpo.onrender.com"
# BASE_URL = "http://localhost:8000"  # Pour test local

def print_section(title):
    """Affiche une section formatée"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health_endpoint():
    """Test 1: Endpoint /health"""
    print_section("TEST 1: Endpoint /health")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Status général: {data.get('status')}")
            print(f"🕒 Timestamp: {data.get('timestamp')}")
            
            services = data.get('services', {})
            print("\n🔧 Services:")
            for service, status in services.items():
                icon = "✅" if "connected" in status or "loaded" in status or "configured" in status else "⚠️"
                print(f"   {icon} {service}: {status}")
            
            return True
        else:
            print(f"❌ Erreur: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print("⏱️ TIMEOUT: Le backend met du temps à répondre (cold start Render?)")
        print("💡 Conseil: Attendre 30 secondes et réessayer")
        return False
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def get_auth_token():
    """Obtenir un token JWT"""
    print_section("AUTHENTIFICATION")
    
    # Essayer avec admin par défaut
    credentials = {
        "username": os.environ.get("ADMIN_USERNAME", "admin"),
        "password": os.environ["ADMIN_PASSWORD"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=credentials,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Token obtenu: {token[:20]}...")
            print(f"🔐 Type: {data.get('token_type')}")
            return token
        else:
            print(f"❌ Erreur login: {response.status_code}")
            print(f"   {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_predictions_endpoint(token):
    """Test 3: Endpoint /predictions/sales"""
    print_section("TEST 3: Prédictions ML + Gemini")
    
    if not token:
        print("❌ Pas de token disponible, skip test")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        print("📡 Appel de /predictions/sales...")
        print("⏳ Patience, le ML + Gemini peuvent prendre 10-30 secondes...")
        
        response = requests.get(
            f"{BASE_URL}/predictions/sales",
            headers=headers,
            timeout=60  # Timeout généreux pour ML + Gemini
        )
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Vérifier la structure
            print("\n📦 Structure de réponse:")
            print(f"   ✓ ml_predictions: {len(data.get('ml_predictions', []))} produits")
            print(f"   ✓ summary: {bool(data.get('summary'))}")
            print(f"   ✓ gemini_recommendations: {bool(data.get('gemini_recommendations'))}")
            print(f"   ✓ timestamp: {data.get('timestamp')}")
            
            # Afficher le top 3
            ml_preds = data.get('ml_predictions', [])
            if ml_preds and isinstance(ml_preds, list):
                print("\n🏆 Top 3 produits (prédiction 7 jours):")
                for i, prod in enumerate(ml_preds[:3], 1):
                    print(f"   {i}. {prod.get('nom_produit')}: {prod.get('predicted_sales_7_days')} unités")
            
            # Afficher les recommandations Gemini
            gemini = data.get('gemini_recommendations', {})
            if gemini and isinstance(gemini, dict):
                print("\n🤖 Recommandations Gemini:")
                if 'trends_analysis' in gemini:
                    print(f"   📈 Tendances: {gemini['trends_analysis'][:100]}...")
                if 'priority_actions' in gemini:
                    print(f"   ⚡ Actions prioritaires: {len(gemini.get('priority_actions', []))} actions")
            elif 'gemini_error' in data:
                print(f"\n⚠️ Gemini échoué (mais ML OK): {data['gemini_error'][:100]}")
            
            # Sauvegarder la réponse complète
            with open('prediction_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("\n💾 Réponse complète sauvegardée dans 'prediction_response.json'")
            
            return True
        
        elif response.status_code == 401:
            print("❌ 401 Unauthorized: Token invalide ou expiré")
            return False
        
        elif response.status_code == 403:
            print("❌ 403 Forbidden: Rôle insuffisant (ADMIN ou GEST_COMMERCIAL requis)")
            return False
        
        elif response.status_code == 500:
            print("❌ 500 Internal Server Error")
            try:
                error_data = response.json()
                print(f"   Détails: {error_data}")
            except:
                print(f"   Raw: {response.text[:200]}")
            return False
        
        else:
            print(f"❌ Code inattendu: {response.status_code}")
            print(f"   {response.text[:200]}")
            return False
    
    except requests.exceptions.Timeout:
        print("⏱️ TIMEOUT après 60s: Le ML/Gemini prend trop de temps")
        print("💡 Causes possibles:")
        print("   - Cold start Render (attendre 1-2 minutes)")
        print("   - Gemini API lent (peut prendre 30-45 secondes)")
        print("   - Beaucoup de produits à analyser")
        return False
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_ml_only_endpoint(token):
    """Test 4: Endpoint /predictions/sales/ml-only (sans Gemini)"""
    print_section("TEST 4: Prédictions ML seulement (sans Gemini)")
    
    if not token:
        print("❌ Pas de token disponible, skip test")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        print("📡 Appel de /predictions/sales/ml-only...")
        
        response = requests.get(
            f"{BASE_URL}/predictions/sales/ml-only",
            headers=headers,
            timeout=30
        )
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            predictions = data.get('predictions', [])
            print(f"📊 {data.get('total_products', 0)} produits analysés")
            print(f"🤖 Modèle: {data.get('model', 'unknown')}")
            
            if predictions:
                print("\n🏆 Top 3 (ML seulement):")
                for i, prod in enumerate(predictions[:3], 1):
                    print(f"   {i}. {prod.get('nom_produit')}: {prod.get('predicted_sales_7_days')} unités")
            
            return True
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text[:200]}")
            return False
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale"""
    print("\n" + "🚀"*30)
    print("   TESTS BACKEND API MOKPOKPO - PRÉDICTIONS IA")
    print("🚀"*30)
    print(f"\n🌐 URL de base: {BASE_URL}")
    print(f"⏰ Début: {datetime.now().strftime('%H:%M:%S')}")
    
    results = {}
    
    # Test 1: Health
    results['health'] = test_health_endpoint()
    
    # Test 2: Auth
    token = get_auth_token()
    results['auth'] = bool(token)
    
    if token:
        # Test 3: Prédictions complètes (ML + Gemini)
        results['predictions_full'] = test_predictions_endpoint(token)
        
        # Test 4: ML seulement
        results['predictions_ml_only'] = test_ml_only_endpoint(token)
    else:
        results['predictions_full'] = False
        results['predictions_ml_only'] = False
    
    # Résumé
    print_section("RÉSUMÉ DES TESTS")
    
    for test_name, success in results.items():
        icon = "✅" if success else "❌"
        print(f"   {icon} {test_name.upper()}: {'PASS' if success else 'FAIL'}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n📊 Score: {passed}/{total} tests réussis ({passed*100//total}%)")
    print(f"⏰ Fin: {datetime.now().strftime('%H:%M:%S')}")
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
    elif passed >= total * 0.75:
        print("\n✅ Majorité des tests réussis")
    else:
        print("\n⚠️ Plusieurs tests ont échoué")
    
    print("\n💡 CONSEILS:")
    print("   - Si timeout sur Render: attendre 1-2 minutes (cold start)")
    print("   - Si 401/403: vérifier les credentials et le rôle utilisateur")
    print("   - Si 500: check les logs backend avec 'heroku logs' ou Render logs")
    print("   - Logs détaillés maintenant disponibles côté backend!")

if __name__ == "__main__":
    main()
