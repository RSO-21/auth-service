import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "8001"))

    KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL")
    KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
    KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
    
    KEYCLOAK_ADMIN = os.getenv("KEYCLOAK_ADMIN")
    KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD")

    @property
    def token_url(self):
        return f"{self.KEYCLOAK_BASE_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/token"

    @property
    def userinfo_url(self):
        return f"{self.KEYCLOAK_BASE_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/userinfo"

    @property
    def jwks_url(self):
        return f"{self.KEYCLOAK_BASE_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/certs"

    @property
    def admin_token_url(self):
        return f"{self.KEYCLOAK_BASE_URL}/realms/master/protocol/openid-connect/token"

SETTINGS = Settings()
