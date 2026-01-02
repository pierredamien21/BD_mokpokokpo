from fastapi import FastAPI
from database import engine
from models.model import Base

# Routers
from routers import (
    utilisateur, client, produit, stock,
    commande, ligne_commande, reservation,
    vente, alerte_stock
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Ferme Mokpokpo")

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

@app.get("/")
def root():
    return {
        "message": "API Mokpokpo opérationnelle",
        "docs": "/docs"
    }