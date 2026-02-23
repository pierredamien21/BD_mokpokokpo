"""
Script pour injecter les produits via l'API
Teste simultanément que les endpoints fonctionnent correctement
"""
import sys
import os
import json
import requests
from typing import Optional

# Ajout du dossier parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
# API_URL = "http://localhost:8000"  # Pour tests locaux
API_URL = "https://bd-mokpokokpo.onrender.com"  # Production Render
ADMIN_EMAIL = "slykokou@gmail.com"
ADMIN_PASSWORD = "admin123"
PRODUCTS_FILE = os.path.join(os.path.dirname(__file__), "..", "products_seed.json")

class APIPopulator:
    def __init__(self, base_url: str, admin_email: str, admin_password: str):
        self.base_url = base_url
        self.admin_email = admin_email
        self.admin_password = admin_password
        self.token = None
        self.session = requests.Session()
        
    def authenticate(self) -> bool:
        """Obtenir le token JWT admin"""
        print("🔐 Authentification en tant qu'admin...")
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                data={
                    "username": self.admin_email,
                    "password": self.admin_password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                print(f"✅ Authentification réussie!")
                return True
            else:
                print(f"❌ Erreur d'authentification: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Erreur lors de la connexion: {str(e)}")
            return False
    
    def load_products(self) -> Optional[list]:
        """Charger les produits du fichier JSON"""
        print(f"\n📖 Chargement des produits depuis {PRODUCTS_FILE}...")
        try:
            with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                products = data.get("produits", [])
                print(f"✅ {len(products)} produits chargés")
                return products
        except FileNotFoundError:
            print(f"❌ Fichier non trouvé: {PRODUCTS_FILE}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON: {str(e)}")
            return None
    
    def create_product(self, product_data: dict) -> Optional[int]:
        """Créer un produit via l'API"""
        try:
            payload = {
                "nom_produit": product_data["nom_produit"],
                "type_produit": product_data.get("type_produit"),
                "description": product_data.get("description"),
                "usages": product_data.get("usages"),
                "prix_unitaire": float(product_data["prix_unitaire"]),
                "url_image": product_data.get("url_image")  # Ajout de l'URL image
            }
            
            response = self.session.post(
                f"{self.base_url}/produits/",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                product_id = result.get("id_produit")
                print(f"  ✅ Produit créé: {product_data['nom_produit']} (ID: {product_id})")
                return product_id
            else:
                print(f"  ❌ Erreur création produit: {response.status_code}")
                print(f"     {response.text}")
                return None
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return None
    
    def create_stock(self, product_id: int, stock_data: dict) -> bool:
        """Créer un stock via l'API"""
        try:
            payload = {
                "id_produit": product_id,
                "quantite_disponible": stock_data["quantite_disponible"],
                "seuil_minimal": stock_data["seuil_minimal"]
            }
            
            response = self.session.post(
                f"{self.base_url}/stocks/",
                json=payload
            )
            
            if response.status_code == 200:
                print(f"     ✅ Stock créé: {stock_data['quantite_disponible']} unités (seuil: {stock_data['seuil_minimal']})")
                return True
            else:
                print(f"     ❌ Erreur création stock: {response.status_code}")
                print(f"        {response.text}")
                return False
        except Exception as e:
            print(f"     ❌ Exception: {str(e)}")
            return False
    
    def populate(self):
        """Processus complet de population"""
        print("\n" + "="*70)
        print("🌿 POPULATION DE LA BASE DONNÉES VIA API - FERME MOKPOKPO")
        print("="*70)
        
        # Étape 1: Authentification
        if not self.authenticate():
            return False
        
        # Étape 2: Chargement des produits
        products = self.load_products()
        if not products:
            return False
        
        # Étape 3: Création des produits et stocks
        print(f"\n📝 Création des {len(products)} produits et leurs stocks...")
        print("-" * 70)
        
        success_count = 0
        failed_count = 0
        
        for i, product in enumerate(products, 1):
            print(f"\n[{i}/{len(products)}] 🌱 {product['nom_produit']}")
            
            # Créer le produit
            product_id = self.create_product(product)
            
            if product_id:
                # Créer le stock associé
                if self.create_stock(product_id, product["stock"]):
                    success_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
        
        # Résumé
        print("\n" + "="*70)
        print("📊 RÉSUMÉ")
        print("="*70)
        print(f"✅ Réussis:     {success_count} produits")
        print(f"❌ Échoués:     {failed_count} produits")
        print(f"📈 Total:       {len(products)} produits")
        print("="*70)
        
        return success_count == len(products)

def main():
    """Fonction principale"""
    populator = APIPopulator(API_URL, ADMIN_EMAIL, ADMIN_PASSWORD)
    success = populator.populate()
    
    if success:
        print("\n✅ Population réussie! Tous les produits ont été ajoutés.")
        print(f"\n💡 Commandes à tester:")
        print(f"   1. GET /produits/          → Voir tous les produits")
        print(f"   2. GET /stocks/            → Voir tous les stocks")
        print(f"   3. GET /docs               → Voir la documentation Swagger")
    else:
        print("\n⚠️ La population s'est terminée avec des erreurs.")
        print("   Vérifiez que:")
        print("   - L'API est en cours d'exécution (http://localhost:8000)")
        print("   - Les identifiants admin sont corrects")
        print("   - Le fichier products_seed.json existe")

if __name__ == "__main__":
    main()
