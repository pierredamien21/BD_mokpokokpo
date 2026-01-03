from fastapi import FastAPI
from database import engine
from models.model import Base
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Routers
from routers import (
    utilisateur, client, produit, stock,
    commande, ligne_commande, reservation,
    vente, alerte_stock, auth
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Ferme Mokpokpo")
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

@app.get("/")
def root():
    return {
        "message": "API Mokpokpo opérationnelle",
        "docs": "/docs"
    }