#!/bin/bash
# Script de test rapide avec curl pour valider les corrections IA
# Basé sur le guide de troubleshooting frontend

BASE_URL="https://bd-mokpokokpo.onrender.com"

echo "=================================="
echo "  TESTS CURL - API MOKPOKPO"
echo "=================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health endpoint (NOUVEAU)
echo -e "${YELLOW}[TEST 1]${NC} Endpoint /health"
echo "curl -s $BASE_URL/health"
HEALTH=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
HTTP_CODE=$(echo "$HEALTH" | tail -n1)
BODY=$(echo "$HEALTH" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ HTTP $HTTP_CODE${NC}"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}❌ HTTP $HTTP_CODE${NC}"
    echo "$BODY"
fi
echo ""

# Test 2: Root endpoint
echo -e "${YELLOW}[TEST 2]${NC} Endpoint racine /"
echo "curl -s $BASE_URL/"
ROOT=$(curl -s -w "\n%{http_code}" "$BASE_URL/")
HTTP_CODE=$(echo "$ROOT" | tail -n1)
BODY=$(echo "$ROOT" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ HTTP $HTTP_CODE${NC}"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}❌ HTTP $HTTP_CODE${NC}"
fi
echo ""

# Test 3: Login (obtenir token)
echo -e "${YELLOW}[TEST 3]${NC} Authentification"
echo "curl -s -X POST $BASE_URL/auth/login -d 'username=admin&password=admin123'"
LOGIN=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/login" \
    -d "username=admin&password=admin123")
HTTP_CODE=$(echo "$LOGIN" | tail -n1)
BODY=$(echo "$LOGIN" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ HTTP $HTTP_CODE${NC}"
    TOKEN=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
    if [ -n "$TOKEN" ]; then
        echo "🔑 Token obtenu: ${TOKEN:0:20}..."
    else
        echo "$BODY"
    fi
else
    echo -e "${RED}❌ HTTP $HTTP_CODE${NC}"
    echo "$BODY"
    exit 1
fi
echo ""

# Test 4: Prédictions avec token
echo -e "${YELLOW}[TEST 4]${NC} Prédictions ML + Gemini (peut prendre 30s)"
echo "curl -s -H 'Authorization: Bearer TOKEN' $BASE_URL/predictions/sales"

if [ -n "$TOKEN" ]; then
    PRED=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "$BASE_URL/predictions/sales")
    HTTP_CODE=$(echo "$PRED" | tail -n1)
    BODY=$(echo "$PRED" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ HTTP $HTTP_CODE${NC}"
        
        # Extraire quelques infos clés
        NUM_PROD=$(echo "$BODY" | python3 -c "import sys,json; data=json.load(sys.stdin); print(len(data.get('ml_predictions', [])))" 2>/dev/null)
        HAS_GEMINI=$(echo "$BODY" | python3 -c "import sys,json; data=json.load(sys.stdin); print('gemini_recommendations' in data)" 2>/dev/null)
        
        echo "📊 Nombre de produits: $NUM_PROD"
        echo "🤖 Gemini actif: $HAS_GEMINI"
        
        # Sauvegarder la réponse
        echo "$BODY" > prediction_response_curl.json
        echo "💾 Réponse complète sauvegardée dans prediction_response_curl.json"
        
    elif [ "$HTTP_CODE" = "401" ]; then
        echo -e "${RED}❌ HTTP 401 Unauthorized${NC}"
        echo "🔐 Token invalide ou expiré"
        
    elif [ "$HTTP_CODE" = "403" ]; then
        echo -e "${RED}❌ HTTP 403 Forbidden${NC}"
        echo "🚫 Rôle insuffisant (ADMIN ou GEST_COMMERCIAL requis)"
        
    elif [ "$HTTP_CODE" = "500" ]; then
        echo -e "${RED}❌ HTTP 500 Internal Server Error${NC}"
        echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
        
    else
        echo -e "${RED}❌ HTTP $HTTP_CODE${NC}"
        echo "$BODY"
    fi
else
    echo -e "${RED}❌ Pas de token disponible${NC}"
fi
echo ""

# Test 5: ML seulement (sans Gemini, plus rapide)
echo -e "${YELLOW}[TEST 5]${NC} Prédictions ML seulement (sans Gemini)"
echo "curl -s -H 'Authorization: Bearer TOKEN' $BASE_URL/predictions/sales/ml-only"

if [ -n "$TOKEN" ]; then
    ML_ONLY=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "$BASE_URL/predictions/sales/ml-only")
    HTTP_CODE=$(echo "$ML_ONLY" | tail -n1)
    BODY=$(echo "$ML_ONLY" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ HTTP $HTTP_CODE${NC}"
        
        NUM_PROD=$(echo "$BODY" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('total_products', 0))" 2>/dev/null)
        echo "📊 Nombre de produits: $NUM_PROD"
        
        # Afficher le top 3
        echo ""
        echo "🏆 Top 3 produits (prédiction 7 jours):"
        echo "$BODY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
preds = data.get('predictions', [])[:3]
for i, p in enumerate(preds, 1):
    print(f'   {i}. {p[\"nom_produit\"]}: {p[\"predicted_sales_7_days\"]} unités')
" 2>/dev/null || echo "   (Impossible d'extraire le top 3)"
        
    else
        echo -e "${RED}❌ HTTP $HTTP_CODE${NC}"
        echo "$BODY"
    fi
else
    echo -e "${RED}❌ Pas de token disponible${NC}"
fi
echo ""

# Résumé
echo "=================================="
echo "  RÉSUMÉ"
echo "=================================="
echo ""
echo "📌 Checklist Frontend (depuis le guide):"
echo "   [✓] /health endpoint disponible"
echo "   [✓] Authentification fonctionne"
echo "   [?] Prédictions ML retournent données"
echo "   [?] Format JSON conforme"
echo ""
echo "💡 CONSEILS:"
echo "   - Si timeout: attendre 1-2 minutes (cold start Render)"
echo "   - Si 401: vérifier expiration du token (24h)"
echo "   - Si 500: consulter les logs backend (Render dashboard)"
echo "   - Logs structurés maintenant disponibles!"
echo ""
echo "🔍 Pour plus de détails, utiliser:"
echo "   python3 test_predictions_complet.py"
