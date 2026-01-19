import requests
from config import SETTINGS
from models import LoginRequest, TokenResponse, UserInfo

class KeycloakClient:

    def exchange_password_for_tokens(self, data: LoginRequest) -> TokenResponse:
        payload = {
            "grant_type": "password",
            "client_id": SETTINGS.KEYCLOAK_CLIENT_ID,
            "client_secret": SETTINGS.KEYCLOAK_CLIENT_SECRET,
            "username": data.username,
            "password": data.password,
        }

        r = requests.post(SETTINGS.token_url, data=payload)
        if r.status_code != 200:
            raise ValueError(f"Token exchange failed ({r.status_code}): {r.text}")

        body = r.json()

        return TokenResponse(
            access_token=body["access_token"],
            refresh_token=body.get("refresh_token"),
            id_token=body.get("id_token"),
            token_type=body.get("token_type", "Bearer"),
            expires_in=body["expires_in"],
            scope=body.get("scope"),
        )

    def get_userinfo(self, access_token: str) -> UserInfo:
        headers = {"Authorization": f"Bearer {access_token}"}

        r = requests.get(SETTINGS.userinfo_url, headers=headers)
        r.raise_for_status()

        body = r.json()

        realm_access = body.get("realm_access", {})
        roles = realm_access.get("roles", []) or []

        return UserInfo(
            sub=body.get("sub", ""),
            email=body.get("email"),
            preferred_username=body.get("preferred_username"),
            email_verified=body.get("email_verified"),
            roles=roles,
        )
        
    def get_admin_token(self) -> str:
        payload = {
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": SETTINGS.KEYCLOAK_ADMIN,
            "password": SETTINGS.KEYCLOAK_ADMIN_PASSWORD,
        }
        r = requests.post(SETTINGS.admin_token_url, data=payload)
        
        r.raise_for_status()
        return r.json()["access_token"]
    
    def create_user(self, username: str, email: str, password: str) -> str:
        token = self.get_admin_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "username": username,
            "email": email,
            "enabled": True,
            "emailVerified": False,
            "credentials": [
                {
                    "type": "password",
                    "value": password,
                    "temporary": False
                }
            ]
        }

        url = f"{SETTINGS.KEYCLOAK_BASE_URL}/admin/realms/{SETTINGS.KEYCLOAK_REALM}/users"
        r = requests.post(url, headers=headers, json=payload)

        if r.status_code not in (200, 201):
            raise Exception(f"Error creating user: {r.text}")

        # ✅ THIS IS THE KEY PART
        location = r.headers.get("Location")
        if not location:
            raise Exception("Keycloak did not return Location header")

        user_id = location.rstrip("/").split("/")[-1]
        return user_id
