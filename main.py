from fastapi import FastAPI
from contextlib import asynccontextmanager
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
    vente, alerte_stock, auth, prediction, lot, alerte_expiration
)

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
app.include_router(auth.router)
app.include_router(prediction.router)

@app.get("/")
def root():
    return {
        "message": "API Mokpokpo opérationnelle",
        "docs": "/docs"
    }