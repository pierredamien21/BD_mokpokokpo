"""
Script complet: clean + repeupler avec images
Étapes:
1. Supprimer tous les produits existants
2. Re-créer les 15 produits avec url_image
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

# Configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

API_URL = "https://bd-mokpokokpo.onrender.com"
ADMIN_EMAIL = os.environ["ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
PRODUCTS_FILE = os.path.join(os.path.dirname(__file__), "..", "products_seed.json")

print("=" * 70)
print("🔄 NETTOYAGE + REPOPULATION DES PRODUITS AVEC IMAGES")
print("=" * 70)

# Authentification
print("\n🔐 Authentification...")
try:
    response = requests.post(
        f"{API_URL}/auth/login",
        data={
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Impossible de s'authentifier: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    token = response.json().get("access_token")
    print(f"✅ Authentification réussie!")
except Exception as e:
    print(f"❌ Erreur: {str(e)}")
    sys.exit(1)

headers = {"Authorization": f"Bearer {token}"}

# ÉTAPE 1: Récupérer et supprimer les produits
print("\n" + "=" * 70)
print("📛 ÉTAPE 1: SUPPRESSION DES ANCIENS PRODUITS")
print("=" * 70)

try:
    response = requests.get(f"{API_URL}/produits/", headers=headers)
    if response.status_code != 200:
        print(f"❌ Impossible de récupérer les produits: {response.status_code}")
        sys.exit(1)
    
    products = response.json()
    print(f"\n📊 {len(products)} produits trouvés")
    
    if len(products) > 0:
        print("\n🗑️  Suppression...")
        deleted = 0
        for i, product in enumerate(products, 1):
            pid = product.get("id_produit")
            pname = product.get("nom_produit")
            print(f"[{i}/{len(products)}] Suppression: {pname} (ID: {pid})")
            
            del_response = requests.delete(
                f"{API_URL}/produits/{pid}",
                headers=headers
            )
            
            if del_response.status_code in [200, 204]:
                deleted += 1
                print(f"     ✅ OK")
            else:
                print(f"     ❌ Erreur: {del_response.status_code}")
        
        print(f"\n✅ {deleted}/{len(products)} produits supprimés")
    else:
        print("✅ Aucun produit à supprimer")
        
except Exception as e:
    print(f"❌ Erreur lors de la suppression: {str(e)}")
    sys.exit(1)

# ÉTAPE 2: Lire les produits de seed.json
print("\n" + "=" * 70)
print("📖 ÉTAPE 2: CHARGEMENT DES PRODUITS AVEC IMAGES")
print("=" * 70)

try:
    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
        products_data = json.load(f)
    
    print(f"\n✅ {len(products_data)} produits chargés de {os.path.basename(PRODUCTS_FILE)}")
    
    # Afficher les produits avec images
    print("\n📦 Produits avec images:")
    for p in products_data[:3]:
        print(f"   - {p.get('nom_produit')}: {p.get('url_image', 'NO IMAGE')[:50]}")
    print(f"   ... ({len(products_data) - 3} autres)")
    
except FileNotFoundError:
    print(f"❌ Fichier non trouvé: {PRODUCTS_FILE}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur lors du chargement: {str(e)}")
    sys.exit(1)

# ÉTAPE 3: Re-créer les produits
print("\n" + "=" * 70)
print("✨ ÉTAPE 3: CRÉATION DES PRODUITS AVEC IMAGES")
print("=" * 70)

created = 0
failed = 0

for i, product_data in enumerate(products_data, 1):
    pname = product_data.get("nom_produit")
    print(f"\n[{i}/{len(products_data)}] {pname}")
    
    # Préparer le payload
    payload = {
        "nom_produit": product_data.get("nom_produit"),
        "type_produit": product_data.get("type_produit"),
        "description": product_data.get("description"),
        "usages": product_data.get("usages"),
        "prix_unitaire": float(product_data.get("prix_unitaire", 0)),
        "url_image": product_data.get("url_image")  # IMPORTANT: URL de l'image
    }
    
    try:
        response = requests.post(
            f"{API_URL}/produits/",
            json=payload,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            pid = result.get("id_produit")
            print(f"   ✅ Créé (ID: {pid})")
            created += 1
            
            # Créer le stock pour ce produit
            stock_payload = {
                "id_produit": pid,
                "quantite_disponible": product_data.get("quantite_disponible", 100),
                "seuil_minimal": product_data.get("seuil_minimal", 10)
            }
            
            stock_response = requests.post(
                f"{API_URL}/stocks/",
                json=stock_payload,
                headers=headers
            )
            
            if stock_response.status_code in [200, 201]:
                print(f"   ✅ Stock créé")
            else:
                print(f"   ⚠️  Stock non créé: {stock_response.status_code}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            print(f"   Message: {response.text[:100]}")
            failed += 1
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        failed += 1

# Résumé
print("\n" + "=" * 70)
print("📊 RÉSUMÉ")
print("=" * 70)
print(f"✅ Créés:      {created} produits")
print(f"❌ Échoués:    {failed} produits")
print(f"📈 Total:      {len(products_data)} produits")
print("=" * 70)

if failed == 0:
    print("\n🎉 RE-POPULATION RÉUSSIE!")
    print("\nProchaines étapes:")
    print("1. Vérifier les images avec: GET /produits/")
    print("2. Faire un git push pour déployer le code")
    sys.exit(0)
else:
    print(f"\n⚠️  {failed} produits n'ont pas pu être créés")
    sys.exit(1)
