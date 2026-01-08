import pytest
from services.prediction_service import PredictionService
from models.model import Vente, Commande, Client, Utilisateur, Produit, LigneCommande
from decimal import Decimal
from datetime import datetime

def test_get_historical_sales_data(db_session):
    # Setup: Create some data
    user = Utilisateur(nom="Test", prenom="User", email="test@test.com", mot_de_passe="xxx", role="CLIENT")
    db_session.add(user)
    db_session.flush()
    
    client = Client(id_utilisateur=user.id_utilisateur, telephone="123", adresse="Test")
    db_session.add(client)
    db_session.flush()
    
    prod = Produit(nom_produit="Tomate", type_produit="Legume", prix_unitaire=Decimal("10.0"))
    db_session.add(prod)
    db_session.flush()
    
    cmd = Commande(id_client=client.id_client, montant_total=Decimal("100.0"), statut="ACCEPTEE")
    db_session.add(cmd)
    db_session.flush()
    
    vente = Vente(id_commande=cmd.id_commande, chiffre_affaires=Decimal("100.0"), date_vente=datetime.now())
    db_session.add(vente)
    db_session.commit()
    
    service = PredictionService(db_session)
    data = service.get_historical_sales_data()
    
    assert len(data) >= 1
    assert data[0]["ca"] == 100.0

def test_prediction_endpoint_auth(client):
    # Test that it requires auth and specific roles
    response = client.get("/predictions/sales")
    assert response.status_code == 401 # Should be unauthorized without token
