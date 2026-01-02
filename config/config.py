import os
import secrets
import string
from dotenv import load_dotenv

# Charge .env
load_dotenv()

class Settings:
    # Vérification et validation
    def __init__(self):
        self._validate_config()
    
    def _validate_config(self):
        """Validation minimale de sécurité"""
        
        # DATABASE_URL - obligatoire
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        if not self.DATABASE_URL:
            raise ValueError(" DATABASE_URL manquant. Créez un fichier .env")
        
        # SECRET_KEY - génère si manquante
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        if not self.SECRET_KEY:
            print("  SECRET_KEY manquante, génération automatique...")
            self.SECRET_KEY = self._generate_secret_key()
        elif len(self.SECRET_KEY) < 32:
            print(" SECRET_KEY trop courte, génération d'une nouvelle...")
            self.SECRET_KEY = self._generate_secret_key()
        
        # DEBUG - sécurité en production
        debug_value = os.getenv("DEBUG", "False").lower()
        self.DEBUG = debug_value == "true"
        
        # Désactiver automatiquement en production
        if os.getenv("ENVIRONMENT") == "production":
            self.DEBUG = False
        
        # Autres configurations
        self.APP_NAME = os.getenv("APP_NAME", "Mon Application")
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    
    def _generate_secret_key(self):
        """Génère une clé secrète aléatoire"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(64))
    
    def mask_sensitive_info(self):
        """Retourne la config sans données sensibles"""
        masked_url = self.DATABASE_URL
        if ":" in self.DATABASE_URL and "@" in self.DATABASE_URL:
            # Masque le mot de passe dans l'URL
            parts = self.DATABASE_URL.split("@")
            if "://" in parts[0]:
                protocol_user = parts[0].split("://")[0] + "://"
                credentials = parts[0].split("://")[1]
                if ":" in credentials:
                    user = credentials.split(":")[0]
                    masked_url = f"{protocol_user}{user}:****@{parts[1]}"
        
        return {
            "app_name": self.APP_NAME,
            "app_version": self.APP_VERSION,
            "debug": self.DEBUG,
            "database_url": masked_url,
            "secret_key_length": len(self.SECRET_KEY)
        }

# Instance unique
settings = Settings()