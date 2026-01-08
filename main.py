from fastapi import FastAPI
from database import engine
from models.model import Base
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from security.limiter import limiter

# Routers
from routers import (
    utilisateur, client, produit, stock,
    commande, ligne_commande, reservation,
    vente, alerte_stock, auth, prediction
)

Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Ferme Mokpokpo")

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
app.include_router(commande.router)
app.include_router(ligne_commande.router)
app.include_router(reservation.router)
app.include_router(vente.router)
app.include_router(alerte_stock.router)
app.include_router(auth.router)
app.include_router(prediction.router)

@app.get("/")
def root():
    return {
        "message": "API Mokpokpo opérationnelle",
        "docs": "/docs"
    }