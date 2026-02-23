"""
Script pour supprimer tous les produits existants avant re-population
"""
import sys
import os
import requests

# Ajout du dossier parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
API_URL = "https://bd-mokpokokpo.onrender.com"
ADMIN_EMAIL = "slykokou@gmail.com"
ADMIN_PASSWORD = "admin123"

def authenticate():
    """Obtenir le token JWT admin"""
    print("🔐 Authentification en tant qu'admin...")
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            data={
                "username": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Authentification réussie!")
            return token
        else:
            print(f"❌ Erreur d'authentification: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return None

def get_all_products(token):
    """Récupérer tous les produits"""
    print("\n📖 Récupération de tous les produits...")
    try:
        response = requests.get(
            f"{API_URL}/produits/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            products = response.json()
            print(f"✅ {len(products)} produits trouvés")
            return products
        else:
            print(f"❌ Erreur: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return []

def delete_product(token, product_id):
    """Supprimer un produit via l'API"""
    try:
        response = requests.delete(
            f"{API_URL}/produits/{product_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code in [200, 204]:
            return True
        else:
            print(f"     ❌ Erreur suppression produit {product_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"     ❌ Exception: {str(e)}")
        return False

def clean_all_products():
    """Nettoyer tous les produits"""
    print("\n" + "="*70)
    print("🧹 NETTOYAGE DE TOUS LES PRODUITS - FERME MOKPOKPO")
    print("="*70)
    
    # Authentification
    token = authenticate()
    if not token:
        return False
    
    # Récupération des produits
    products = get_all_products(token)
    if not products:
        print("\n✅ Aucun produit à supprimer!")
        return True
    
    # Suppression
    print(f"\n🗑️  Suppression de {len(products)} produits...")
    print("-" * 70)
    
    success_count = 0
    failed_count = 0
    
    for i, product in enumerate(products, 1):
        product_id = product.get("id_produit")
        product_name = product.get("nom_produit")
        
        print(f"[{i}/{len(products)}] Suppression: {product_name} (ID: {product_id})")
        
        if delete_product(token, product_id):
            success_count += 1
        else:
            failed_count += 1
    
    # Résumé
    print("\n" + "="*70)
    print("📊 RÉSUMÉ")
    print("="*70)
    print(f"✅ Supprimés:   {success_count} produits")
    print(f"❌ Échoués:     {failed_count} produits")
    print(f"📈 Total:       {len(products)} produits")
    print("="*70)
    
    return failed_count == 0

if __name__ == "__main__":
    print("\n⚠️  ATTENTION: Ce script va supprimer TOUS les produits!")
    confirm = input("Taper 'OUI' pour confirmer: ")
    
    if confirm.strip().upper() == "OUI":
        success = clean_all_products()
        if success:
            print("\n✅ Nettoyage terminé! Vous pouvez maintenant exécuter populate_api.py")
        else:
            print("\n⚠️  Certains produits n'ont pas pu être supprimés.")
    else:
        print("\n❌ Opération annulée.")
