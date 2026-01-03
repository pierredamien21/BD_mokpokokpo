import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db
from models.model import Base

# Base de données de test en mémoire (SQLite)
# Note: SQLite ne supporte pas certains types Postgres, mais pour des tests basiques ça passe souvent.
# Si échec, il faudra mock ou utiliser une vraie DB de test.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture de base de données
@pytest.fixture(scope="function")
def db_session():
    # Création des tables
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

# Fixture Client API
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    app.state.limiter.enabled = False # Disable rate limit for tests
    yield TestClient(app)
    app.dependency_overrides = {}
    app.state.limiter.enabled = True
