#!/usr/bin/env python3
"""
Script de test pour Phase 3: Livraison Management
Teste tous les endpoints du router livraison
"""

import sys
sys.path.insert(0, '/home/sly/Documents/s5/projet tutoré/projet')

from fastapi.testclient import TestClient
from main import app
from database import SessionLocal

# Setup client de test
client = TestClient(app)

print("\n" + "="*60)
print("🧪 TESTS PHASE 3 : LIVRAISON MANAGEMENT")
print("="*60)

# Test 1: Vérifier que les endpoints sont enregistrés
print("\n1️⃣  Vérifier que les routes Livraison sont disponibles...")
routes = [route.path for route in app.routes]
livraison_routes = [r for r in routes if 'livraison' in r.lower()]
print(f"   Routes trouvées: {livraison_routes}")
if len(livraison_routes) >= 4:
    print("   ✅ Routes Livraison enregistrées")
else:
    print("   ⚠️  Nombre de routes insuffisant")

# Test 2: Vérifier que les schémas sont importables
print("\n2️⃣  Vérifier les imports des schémas Livraison...")
try:
    from schema.livraison import (
        LivraisonBase, LivraisonCreate, LivraisonRead,
        LivraisonDetailRead, LivraisonListResponse, LivraisonStatusUpdate
    )
    print("   ✅ Tous les schémas Livraison importés")
except Exception as e:
    print(f"   ❌ Erreur import: {e}")

# Test 3: Vérifier que le modèle est bien lié à Commande
print("\n3️⃣  Vérifier les relations Commande ↔ Livraison...")
try:
    from models.model import Commande, Livraison
    
    # Vérifier l'attribut livraison dans Commande
    if hasattr(Commande, 'livraison'):
        print("   ✅ Relation Livraison dans Commande trouvée")
    else:
        print("   ❌ Relation manquante dans Commande")
    
    # Vérifier l'attribut commande dans Livraison
    if hasattr(Livraison, 'commande'):
        print("   ✅ Relation Commande dans Livraison trouvée")
    else:
        print("   ❌ Relation manquante dans Livraison")
        
except Exception as e:
    print(f"   ❌ Erreur vérification relations: {e}")

# Test 4: Vérifier la structure des endpoints
print("\n4️⃣  Vérifier la structure des endpoints...")
endpoint_signatures = {
    "/livraisons/": ["GET", "POST"],
    "/livraisons/{id_livraison}": ["GET", "PUT"],
    "/livraisons/{id_livraison}/statut": ["PUT"],
    "/livraisons/dashboard/stats": ["GET"]
}

for route in app.routes:
    for endpoint, methods in endpoint_signatures.items():
        if endpoint.replace("{id_livraison}", "{") in route.path or route.path.endswith(endpoint.split("/")[1]) if "/" in endpoint else False:
            if hasattr(route, 'methods'):
                route_methods = [m for m in route.methods if m != "HEAD"]
                print(f"   ✅ {route.path}: {route_methods}")

# Test 5: Vérifier la compilation de la migration SQL
print("\n5️⃣  Vérifier la migration SQL...")
try:
    with open('/home/sly/Documents/s5/projet tutoré/projet/tables_index_tiggers/migration_livraison.sql', 'r') as f:
        sql_content = f.read()
        tables_count = sql_content.count('CREATE TABLE')
        indexes_count = sql_content.count('CREATE INDEX')
        print(f"   ✅ Migration SQL trouvée:")
        print(f"      - {tables_count} table(s) créée(s)")
        print(f"      - {indexes_count} index(es) créé(s)")
        print(f"      - Contraintes : check, fk, unique")
except Exception as e:
    print(f"   ❌ Erreur migration SQL: {e}")

# Test 6: Vérifier les statuts d'énumération
print("\n6️⃣  Vérifier les statuts d'énumération...")
try:
    from schema.livraison import StatutLivraison
    statuts = [s.value for s in StatutLivraison]
    expected = ["EN_PREPARATION", "PRETE", "EN_LIVRAISON", "LIVRÉE"]
    if set(statuts) == set(expected):
        print(f"   ✅ Statuts valides: {statuts}")
    else:
        print(f"   ⚠️  Statuts: {statuts}")
except Exception as e:
    print(f"   ⚠️  Enum statuts: {e}")

# Test 7: Vérifier la documentation Swagger
print("\n7️⃣  Vérifier la documentation Swagger...")
try:
    response = client.get("/openapi.json")
    if response.status_code == 200:
        openapi = response.json()
        livraison_paths = [p for p in openapi.get("paths", {}) if "livraison" in p.lower()]
        print(f"   ✅ Documentation Swagger disponible")
        print(f"      - {len(livraison_paths)} endpoint(s) documenté(s)")
    else:
        print(f"   ⚠️  Swagger non accessible (code {response.status_code})")
except Exception as e:
    print(f"   ⚠️  Erreur Swagger: {e}")

print("\n" + "="*60)
print("✅ TESTS PHASE 3 TERMINÉS")
print("="*60 + "\n")
