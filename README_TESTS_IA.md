# 🚀 Guide Rapide - Tests IA Backend

## Pour tester rapidement les corrections :

### 1️⃣ Test Health Check (le plus rapide)
```bash
curl https://bd-mokpokokpo.onrender.com/health
```

**Résultat attendu :**
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "ml_model": "loaded",
    "gemini_api": "configured"
  }
}
```

---

### 2️⃣ Test complet avec script bash (recommandé)
```bash
./test_predictions.sh
```

**Ce que ça teste :**
- ✅ Endpoint `/health`
- ✅ Authentification
- ✅ Prédictions ML + Gemini
- ✅ Prédictions ML seulement

**Durée:** 1-2 minutes (selon cold start)

---

### 3️⃣ Test détaillé avec Python (le plus complet)
```bash
python3 test_predictions_complet.py
```

**Ce que ça teste :**
- Tout ce que fait le script bash
- Affiche le top 3 des produits
- Affiche les recommandations Gemini
- Sauvegarde la réponse complète en JSON
- Score final avec statistiques

**Durée:** 2-3 minutes

---

## 📊 Interprétation des résultats

### Status "healthy" ✅
Tout fonctionne : DB connectée, ML chargé, Gemini configuré

### Status "degraded" ⚠️
Fonctionne partiellement : ML OK mais Gemini non configuré

### Status "unhealthy" ❌
Problème critique : DB non connectée ou ML non chargé

---

## 🔍 Voir les logs en production

### Sur Render :
1. Aller sur https://dashboard.render.com
2. Sélectionner le service `bd-mokpokokpo`
3. Cliquer sur l'onglet **Logs**

### Logs à chercher :
```
✅ Modèle ML chargé depuis AI/modele_ventes.pkl
🔮 Démarrage prédictions ML pour tous les produits
📊 34 produits à analyser
✅ 34 prédictions générées avec succès
🤖 Appel API Gemini pour recommandations...
✅ Recommandations Gemini reçues et parsées
```

**En cas d'erreur :**
```
❌ Erreur chargement modèle ML: ...
❌ GOOGLE_API_KEY non trouvée dans l'environnement
❌ Erreur API Gemini: ...
```

---

## 🐛 Troubleshooting

### "Connection timeout"
**Cause:** Cold start Render (15-30 secondes première requête)  
**Solution:** Attendre 1-2 minutes et réessayer

### "HTTP 401 Unauthorized"
**Cause:** Token expiré (durée de vie: 24h)  
**Solution:** Relancer le script qui re-login automatiquement

### "HTTP 500 - ml_model_not_loaded"
**Cause:** Fichier `AI/modele_ventes.pkl` absent sur Render  
**Solution:** Vérifier que le fichier est dans le repo Git

### "HTTP 500 - gemini_api_error"
**Cause:** Clé API Gemini invalide ou quota dépassé  
**Solution:** Les prédictions ML sont quand même retournées (fallback)

### "HTTP 403 Forbidden"
**Cause:** Utilisateur sans rôle ADMIN ou GEST_COMMERCIAL  
**Solution:** Vérifier le rôle dans la base de données

---

## 📂 Fichiers importants

| Fichier | Rôle |
|---------|------|
| [main.py](main.py) | Endpoint `/health` ajouté |
| [services/prediction_service.py](services/prediction_service.py) | Logging + gestion d'erreurs |
| [test_predictions.sh](test_predictions.sh) | Tests bash rapides |
| [test_predictions_complet.py](test_predictions_complet.py) | Tests Python détaillés |
| [ANALYSE_FAISABILITE_IA.md](ANALYSE_FAISABILITE_IA.md) | Analyse des gaps frontend/backend |
| [CORRECTIONS_IA_PHASE6.md](CORRECTIONS_IA_PHASE6.md) | Documentation complète Phase 6 |

---

## ✅ Checklist avant de partager au frontend

- [ ] Tests locaux réussis (`./test_predictions.sh`)
- [ ] Déployé sur Render
- [ ] `/health` retourne `"status": "healthy"`
- [ ] Logs visibles dans Render Dashboard
- [ ] Prédictions ML fonctionnent
- [ ] Gemini retourne des recommandations (ou fallback ML si échoue)
- [ ] Documentation partagée avec l'équipe frontend

---

## 🎯 Ce qui a changé (pour le frontend)

### Nouveau endpoint disponible
```bash
GET /health
# Pas d'authentification requise
# Permet de vérifier si le backend est prêt
```

### Nouveaux champs dans les réponses d'erreur
```json
{
  "error": "Description de l'erreur",
  "error_type": "ml_model_not_loaded",  // NOUVEAU
  "timestamp": "2025-02-27T..."          // NOUVEAU
}
```

### Gestion du fallback Gemini
```json
{
  "ml_predictions": [...],              // ✅ Toujours présent
  "summary": {...},                     // ✅ Toujours présent
  "gemini_recommendations": {...},      // ✅ Si Gemini OK
  "gemini_error": "...",                // ⚠️ Si Gemini échoue
  "note": "Prédictions ML disponibles..." // ℹ️ Message d'info
}
```

**Frontend doit gérer :**
- Cas 1 : `ml_predictions` + `gemini_recommendations` → Afficher tout ✅
- Cas 2 : `ml_predictions` + `gemini_error` → Afficher ML seulement ⚠️
- Cas 3 : `error` + `error_type` → Afficher message d'erreur ❌

---

## 📞 Support

**Backend prêt à 100%** ✅

- Endpoint `/health` opérationnel
- Logging structuré activé
- Gestion d'erreurs avec `error_type`
- Fallback ML si Gemini échoue
- Scripts de test fournis

**Prochaine étape :** Déployer sur Render et tester en production

---

*Généré le 27 Février 2025 - Phase 6*
