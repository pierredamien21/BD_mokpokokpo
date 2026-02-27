from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
from datetime import datetime
from database import engine
from models.model import Base
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from security.limiter import limiter
from scheduler import start_scheduler, stop_scheduler

# Routers
from routers import (
    utilisateur, client, produit, stock,
    commande, ligne_commande, reservation,
    vente, alerte_stock, auth, prediction, lot, alerte_expiration, livraison
)
from services.prediction_service import MODELE_ML
from database import engine
import sqlalchemy
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

# Variables globales pour le scheduler
scheduler_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du cycle de vie de l'application
    - Démarrage: Initialiser le scheduler
    - Arrêt: Arrêter le scheduler
    """
    # Startup
    global scheduler_instance
    scheduler_instance = start_scheduler()
    yield
    # Shutdown
    if scheduler_instance:
        stop_scheduler(scheduler_instance)


app = FastAPI(
    title="API Ferme Mokpokpo",
    lifespan=lifespan
)

# Configuration CORS pour permettre au frontend de communiquer avec l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Inclusion des routes
app.include_router(utilisateur.router)
app.include_router(client.router)
app.include_router(produit.router)
app.include_router(stock.router)
app.include_router(lot.router)  # 🎯 FEFO - Gestion des lots
app.include_router(commande.router)
app.include_router(ligne_commande.router)
app.include_router(reservation.router)
app.include_router(vente.router)
app.include_router(alerte_stock.router)
app.include_router(alerte_expiration.router)  # 🎯 Phase 2 - Alertes intelligentes
app.include_router(livraison.router)  # 🎯 Phase 3 - Gestion des livraisons
app.include_router(auth.router)
app.include_router(prediction.router)

@app.get("/")

@app.get("/health")
def health_check():
    """
    Endpoint pour vérifier l'état de santé du backend.
    Vérifie: DB, modèle ML, configuration Gemini.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }
    
    # Vérifier la connexion à la base de données
    try:
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        health_status["services"]["database"] = "connected"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Vérifier le modèle ML
    if MODELE_ML is not None:
        health_status["services"]["ml_model"] = "loaded"
    else:
        health_status["services"]["ml_model"] = "not_loaded"
        health_status["status"] = "degraded"
    
    # Vérifier la configuration Gemini
    gemini_key = os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        health_status["services"]["gemini_api"] = "configured"
    else:
        health_status["services"]["gemini_api"] = "not_configured"
        health_status["status"] = "degraded"
    
    return health_status
def root():
    return {
        "message": "API Mokpokpo opérationnelle",
        "docs": "/docs"
    }