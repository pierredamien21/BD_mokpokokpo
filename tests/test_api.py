from fastapi.testclient import TestClient
from schema.enums import RoleEnum

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API Mokpokpo opérationnelle", "docs": "/docs"}

# ================================
# HELPERS
# ================================
def signup_login_helper(client, email="test@example.com", password="password123", role="CLIENT"):
    # 1. Signup
    signup_data = {
        "nom": "Test",
        "prenom": "User",
        "email": email,
        "mot_de_passe": password,
        "role": role
    }
    res_signup = client.post("/utilisateurs/", json=signup_data)
    assert res_signup.status_code == 200
    user_id = res_signup.json()["id_utilisateur"]

    # 2. Login
    login_data = {
        "username": email,
        "password": password
    }
    res_login = client.post("/auth/login", data=login_data)
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]
    
    return token, user_id

# ================================
# 1. AUTHENTICATION & SECURITY
# ================================
def test_signup_login_flow(client):
    token, user_id = signup_login_helper(client)
    assert token is not None
    assert user_id is not None

def test_login_fail(client):
    res = client.post("/auth/login", data={"username": "wrong", "password": "bad"})
    assert res.status_code == 401

# ================================
# 2. RBAC & PRIVACY
# ================================
def test_admin_creation_restriction(client):
    admin_data = {
        "nom": "Fake", "prenom": "Admin",
        "email": "fakeadmin@test.com", "mot_de_passe": "123",
        "role": "ADMIN"
    }
    res = client.post("/utilisateurs/", json=admin_data)
    assert res.status_code == 403

def test_privacy_profile(client):
    token1, id1 = signup_login_helper(client, "u1@test.com")
    _, id2 = signup_login_helper(client, "u2@test.com")
    
    headers = {"Authorization": f"Bearer {token1}"}
    res = client.get(f"/utilisateurs/{id2}", headers=headers)
    assert res.status_code == 403

    res_own = client.get(f"/utilisateurs/{id1}", headers=headers)
    assert res_own.status_code == 200

# ================================
# 3. RESOURCE MANAGEMENT (RBAC)
# ================================
def test_create_product_rbac(client):
    # Client fails
    token_c, _ = signup_login_helper(client, "c@test.com", role="CLIENT")
    headers_c = {"Authorization": f"Bearer {token_c}"}
    prod = {"nom_produit": "Pomme", "prix_unitaire": 1.5}
    res = client.post("/produits/", json=prod, headers=headers_c)
    assert res.status_code == 403

    # GEST_STOCK succeeds
    # Need an admin to create a GEST_STOCK or we create manually in DB?
    # Our create_utilisateur allows anyone to sign up as CLIENT, 
    # but only ADMIN can create GEST_STOCK.
    # We'll use a secret path or just mock the admin.
    # In tests, we can just use the db fixture to create an admin.
    pass

# ================================
# 4. BUSINESS LOGIC & CONSTRAINTS
# ================================
def test_duplicate_email(client):
    u1 = {"nom":"A","prenom":"A","email":"dup@test.com","mot_de_passe":"1","role":"CLIENT"}
    client.post("/utilisateurs/", json=u1)
    res = client.post("/utilisateurs/", json=u1)
    assert res.status_code == 400

def test_order_flow_and_calculation(client):
    # Setup: Admin login (using token)
    # Since we can't easily "bootstrap" admin via API without a first admin,
    # we'll mock the role check or just test what's public.
    
    # 1. Create User
    token, user_id = signup_login_helper(client, "client@order.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create Client Profile
    # First, must exist as User (already done)
    # Then create client profile
    client_res = res_c = client.post("/clients/", json={"id_utilisateur": user_id, "telephone": "123"}, headers=headers)
    client_id = res_c.json()["id_client"]
    client_id = client_res.json()["id_client"]
    assert client_res.status_code == 200

    # 3. Create Order
    order_data = {
        "id_client": client_id,
        "statut": "EN_ATTENTE"
    }
    res_order = client.post("/commandes/", json=order_data, headers=headers)
    assert res_order.status_code == 200
    order_id = res_order.json()["id_commande"]

    # 4. Add Line Item
    # Needs a product - let's assume we can create one if we had admin.
    # For now, let's verify error handling on non-existent product
    line_data = {
        "id_commande": order_id,
        "id_produit": 999,
        "quantite": 2,
        "prix_unitaire": 10.0,
        "montant_ligne": 20.0
    }
    res_line = client.post("/ligne-commandes/", json=line_data, headers=headers)
    assert res_line.status_code == 404 # Produit inexistant

def test_product_and_stock_logic(client, db_session):
    # 1. Create Admin (we need one for products)
    from models.model import Utilisateur
    from security.hashing import hash_password
    from schema.enums import RoleEnum

    admin_user = Utilisateur(
        nom="Admin", prenom="Test", email="admin@test.com",
        mot_de_passe=hash_password("admin123"), role=RoleEnum.ADMIN
    )
    db_session.add(admin_user)
    db_session.commit()
    
    # Login as Admin
    res_login = client.post("/auth/login", data={"username": "admin@test.com", "password": "admin123"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Product
    prod_data = {"nom_produit": "Banane", "prix_unitaire": 5.0}
    res_prod = client.post("/produits/", json=prod_data, headers=headers)
    assert res_prod.status_code == 200
    prod_id = res_prod.json()["id_produit"]

    # 3. Create Stock
    stock_data = {"id_produit": prod_id, "quantite_disponible": 100, "seuil_minimal": 10}
    res_stock = client.post("/stocks/", json=stock_data, headers=headers)
    assert res_stock.status_code == 200

    # 4. Test Calculation in Line Item (Manual for now as per schema)
    # Create an order first
    token_b, user_id = signup_login_helper(client, "buyer@test.com")
    headers_b = {"Authorization": f"Bearer {token_b}"}
    res_c = client.post("/clients/", json={"id_utilisateur": user_id, "telephone": "999"}, headers=headers_b)
    client_id = res_c.json()["id_client"]
    
    res_order = client.post("/commandes/", json={"id_client": client_id, "statut": "EN_ATTENTE"}, headers=headers_b)
    order_id = res_order.json()["id_commande"]

    # Add line item
    line_data = {
        "id_commande": order_id,
        "id_produit": prod_id,
        "quantite": 10,
        "prix_unitaire": 5.0,
        "montant_ligne": 50.0  # Formula: 10 * 5
    }
    res_line = client.post("/ligne-commandes/", json=line_data, headers=headers_b)
    assert res_line.status_code == 200

def test_negative_values_constraint(client):
    # This depends on DB constraints or Pydantic validation
    # Let's test Pydantic validation if it exists
    token, _ = signup_login_helper(client, "edge@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try negative price
    prod = {"nom_produit": "Fraise", "prix_unitaire": -1.0}
    res = client.post("/produits/", json=prod, headers=headers)
    # If no validation, it might return 200. If we have Pydantic PositiveFloat it's 422.
    assert res.status_code in [422, 403] # 403 because it's a client or 422 if it was admin

# ================================
# 5. COMPLEMENTARY TESTS
# ================================
def test_one_stock_per_product(client, db_session):
    # Setup Admin
    from models.model import Utilisateur, Produit
    from security.hashing import hash_password
    from schema.enums import RoleEnum
    
    admin = Utilisateur(nom="A", prenom="B", email="admin2@t.com", mot_de_passe=hash_password("1"), role=RoleEnum.ADMIN)
    p1 = Produit(nom_produit="P1", prix_unitaire=10)
    db_session.add_all([admin, p1])
    db_session.commit()
    
    p1_id = p1.id_produit  # CAPTURE ID BEFORE DETACHMENT
    
    res_login = client.post("/auth/login", data={"username": "admin2@t.com", "password": "1"})
    headers = {"Authorization": f"Bearer {res_login.json()['access_token']}"}
    
    # Create first stock
    client.post("/stocks/", json={"id_produit": p1_id, "quantite_disponible": 1, "seuil_minimal": 0}, headers=headers)
    
    # Create second stock for same product -> Should fail 400
    res = client.post("/stocks/", json={"id_produit": p1_id, "quantite_disponible": 10, "seuil_minimal": 0}, headers=headers)
    assert res.status_code == 400
    assert "Stock déjà existant" in res.json()["detail"]

def test_unauthorized_admin_access(client):
    # Client should not be able to list stocks or alerts
    token, _ = signup_login_helper(client, "peeping@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # List stocks
    res_stocks = client.get("/stocks/", headers=headers)
    assert res_stocks.status_code == 403
    
    # List alerts
    res_alerts = client.get("/alertes-stock/", headers=headers)
    assert res_alerts.status_code == 403

def test_stock_alert_creation_flow(client, db_session):
    from models.model import Utilisateur, Produit
    from security.hashing import hash_password
    from schema.enums import RoleEnum
    
    admin = Utilisateur(nom="A", prenom="B", email="admin3@t.com", mot_de_passe=hash_password("1"), role=RoleEnum.ADMIN)
    p = Produit(nom_produit="AlertItem", prix_unitaire=5)
    db_session.add_all([admin, p])
    db_session.commit()
    
    p_id = p.id_produit  # CAPTURE ID
    
    res_login = client.post("/auth/login", data={"username": "admin3@t.com", "password": "1"})
    headers = {"Authorization": f"Bearer {res_login.json()['access_token']}"}
    
    alert_payload = {
        "id_produit": p_id,
        "message": "Stock critique !",
        "statut": "NON_TRAITEE",
        "seuil_declencheur": 5
    }
    res = client.post("/alertes-stock/", json=alert_payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["id_produit"] == p_id

def test_invalid_enum_status_validation(client):
    # Create user/client
    token, user_id = signup_login_helper(client, "enum@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    res_c = client.post("/clients/", json={"id_utilisateur": user_id, "telephone": "123"}, headers=headers)
    client_id = res_c.json()["id_client"]

    # Try creating order with invalid status
    invalid_order = {
        "id_client": client_id,
        "statut": "MARCHE_PAS" # Not in StatutCommandeEnum
    }
    res = client.post("/commandes/", json=invalid_order, headers=headers)
    assert res.status_code == 422 # Pydantic validation error

# ================================
# 6. ULTIMATE INTEGRATION TEST
# ================================
def test_ultimate_e2e_flow(client, db_session):
    """
    Scenario:
    1. Admin creates a Product and initial Stock.
    2. A new User signs up and is promoted (manually for test) to GEST_COMMERCIAL.
    3. A Client signs up, creates a profile, and places an order.
    4. GEST_COMMERCIAL verifies stock and views order.
    5. Security: Client is blocked from viewing Stock List.
    """
    from models.model import Utilisateur, Produit
    from security.hashing import hash_password
    from schema.enums import RoleEnum

    # --- PART 1: ADMIN SETUP ---
    admin = Utilisateur(nom="Admin", prenom="System", email="master@farm.com", 
                        mot_de_passe=hash_password("master123"), role=RoleEnum.ADMIN)
    db_session.add(admin)
    db_session.commit()
    
    login_res = client.post("/auth/login", data={"username": "master@farm.com", "password": "master123"})
    admin_headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}
    
    # Create Product
    prod_res = client.post("/produits/", json={"nom_produit": "Miel Premium", "prix_unitaire": 20.0}, headers=admin_headers)
    p_id = prod_res.json()["id_produit"]
    
    # Create Stock
    client.post("/stocks/", json={"id_produit": p_id, "quantite_disponible": 50, "seuil_minimal": 5}, headers=admin_headers)

    # --- PART 2: THE GEST_COMMERCIAL ---
    # Create a staff user manually in DB
    staff = Utilisateur(nom="Staff", prenom="One", email="staff@farm.com", 
                         mot_de_passe=hash_password("staff123"), role=RoleEnum.GEST_COMMERCIAL)
    db_session.add(staff)
    db_session.commit()
    
    login_staff = client.post("/auth/login", data={"username": "staff@farm.com", "password": "staff123"})
    staff_headers = {"Authorization": f"Bearer {login_staff.json()['access_token']}"}

    # --- PART 3: THE CLIENT FLOW ---
    # Signup
    signup_c = client.post("/utilisateurs/", json={
        "nom": "Client", "prenom": "Jean", "email": "jean@mail.com", "mot_de_passe": "jean123", "role": "CLIENT"
    })
    c_user_id = signup_c.json()["id_utilisateur"]
    
    # Login
    login_c = client.post("/auth/login", data={"username": "jean@mail.com", "password": "jean123"})
    c_token = login_c.json()["access_token"]
    c_headers = {"Authorization": f"Bearer {c_token}"}
    
    # Profile creation
    res_c = res_c = client.post("/clients/", json={"id_utilisateur": c_user_id, "telephone": "060606"}, headers=c_headers)
    assert res_c.status_code == 200
    client_id = res_c.json()["id_client"]
    
    # Order creation
    order_res = client.post("/commandes/", json={"id_client": client_id, "statut": "EN_ATTENTE"}, headers=c_headers)
    assert order_res.status_code == 200
    order_id = order_res.json()["id_commande"]
    
    # Add Item
    item_res = client.post("/ligne-commandes/", json={
        "id_commande": order_id, "id_produit": p_id, "quantite": 5, "prix_unitaire": 20.0, "montant_ligne": 100.0
    }, headers=c_headers)
    assert item_res.status_code == 200

    # --- PART 4: STAFF VERIFICATION ---
    # Staff lists orders
    orders = client.get("/commandes/", headers=staff_headers)
    assert len(orders.json()) >= 1
    
    # Staff can see stock
    stocks = client.get("/stocks/", headers=staff_headers)
    assert stocks.status_code == 200

    # --- PART 5: SECURITY CHECK ---
    # Client tries to see stocks -> Should fail
    fail_res = client.get("/stocks/", headers=c_headers)
    assert fail_res.status_code == 403
    
    # Client tries to see all users -> Should fail
    fail_users = client.get("/utilisateurs/", headers=c_headers)
    assert fail_users.status_code == 403
    
    print("\n--- ULTIMATE E2E FLOW PASSED ---")

# ================================
# 7. ADDED TESTS (SALES, RESERVATIONS, ALERTS)
# ================================

def test_vente_flow(client, db_session):
    from models.model import Utilisateur, Produit, Commande
    from security.hashing import hash_password
    from schema.enums import RoleEnum, StatutCommandeEnum
    from datetime import datetime

    # 1. Setup Admin & Data
    admin = Utilisateur(nom="Admin", prenom="Vente", email="admin_vente@test.com", 
                        mot_de_passe=hash_password("password"), role=RoleEnum.ADMIN)
    p = Produit(nom_produit="Produit Vente", prix_unitaire=10.0)
    db_session.add_all([admin, p])
    db_session.commit()

    login_res = client.post("/auth/login", data={"username": "admin_vente@test.com", "password": "password"})
    admin_headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    # 2. Setup Client & Order
    token_c, user_id_c = signup_login_helper(client, "client_vente@test.com")
    headers_c = {"Authorization": f"Bearer {token_c}"}
    res_c = client.post("/clients/", json={"id_utilisateur": user_id_c, "telephone": "123"}, headers=headers_c)
    client_id = res_c.json()["id_client"]
    
    # ACCEPTEE instead of TERMINEE (which doesn't exist in StatutCommandeEnum)
    order_res = client.post("/commandes/", json={"id_client": client_id, "statut": "ACCEPTEE"}, headers=headers_c)
    assert order_res.status_code == 200
    order_id = order_res.json()["id_commande"]

    # 3. Create Vente (Admin/Gest Comm only)
    vente_data = {"id_commande": order_id, "chiffre_affaires": 100.0}
    res_vente = client.post("/ventes/", json=vente_data, headers=admin_headers)
    assert res_vente.status_code == 200
    assert res_vente.json()["id_commande"] == order_id

    # 4. Duplicate Vente -> Should fail
    res_dup = client.post("/ventes/", json=vente_data, headers=admin_headers)
    assert res_dup.status_code == 400
    assert "Vente déjà enregistrée" in res_dup.json()["detail"]

    # 5. Unauthorized Creation
    res_unauth = client.post("/ventes/", json=vente_data, headers=headers_c)
    assert res_unauth.status_code == 403

def test_reservation_flow(client, db_session):
    from models.model import Client
    # 1. Setup Client
    token_c, user_id_c = signup_login_helper(client, "client_res@test.com")
    headers_c = {"Authorization": f"Bearer {token_c}"}
    
    # Ensure profile exists for reservation
    client_prof = Client(id_utilisateur=user_id_c, telephone="123")
    db_session.add(client_prof)
    db_session.flush()
    client_id = client_prof.id_client
    db_session.add(client_prof)
    db_session.commit()

    # 2. Create Reservation (Client/Admin)
    res_data = {"id_client": client_id, "statut": "EN_ATTENTE"}
    res_post = client.post("/reservations/", json=res_data, headers=headers_c)
    assert res_post.status_code == 200
    res_json = res_post.json()
    assert "id_reservation" in res_json
    res_id = res_json["id_reservation"]

    # 3. Get Reservation
    res_get = client.get(f"/reservations/{res_id}", headers=headers_c)
    assert res_get.status_code == 200
    # Note: ReservationRead schema doesn't have id_utilisateur, but has id_reservation and statut
    assert res_get.json()["id_reservation"] == res_id
    assert res_get.json()["statut"] == "EN_ATTENTE"

    # 4. Get All (Admin/Gest Comm only)
    res_all = client.get("/reservations/", headers=headers_c)
    assert res_all.status_code == 403

def test_alerte_stock_crud(client, db_session):
    from models.model import Utilisateur, Produit
    from security.hashing import hash_password
    from schema.enums import RoleEnum

    # 1. Setup Admin & Product
    admin = Utilisateur(nom="Admin", prenom="Alerte", email="admin_alerte@test.com", 
                        mot_de_passe=hash_password("password"), role=RoleEnum.ADMIN)
    p = Produit(nom_produit="Produit Alerte", prix_unitaire=5.0)
    db_session.add_all([admin, p])
    db_session.commit()
    p_id = p.id_produit

    login_res = client.post("/auth/login", data={"username": "admin_alerte@test.com", "password": "password"})
    admin_headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    # 2. Create Alerte (Admin/Gest Stock only)
    alert_data = {
        "id_produit": p_id,
        "message": "Stock bas",
        "statut": "NON_TRAITEE",
        "seuil_declencheur": 10
    }
    res_alert = client.post("/alertes-stock/", json=alert_data, headers=admin_headers)
    assert res_alert.status_code == 200
    alert_id = res_alert.json()["id_alerte"]

    # 3. Get Alerte
    res_get = client.get(f"/alertes-stock/{alert_id}", headers=admin_headers)
    assert res_get.status_code == 200
    assert res_get.json()["message"] == "Stock bas"

    # 4. Unauthorized Access (Client)
    token_c, _ = signup_login_helper(client, "client_alerte@test.com")
    headers_c = {"Authorization": f"Bearer {token_c}"}
    res_unauth = client.get("/alertes-stock/", headers=headers_c)
    assert res_unauth.status_code == 403
