import jwt
from jwt.algorithms import RSAAlgorithm
import requests
from flask import abort
from config import SETTINGS

JWKS_CACHE = None


def get_jwks():
    global JWKS_CACHE
    if JWKS_CACHE:
        return JWKS_CACHE

    r = requests.get(SETTINGS.jwks_url)
    r.raise_for_status()
    JWKS_CACHE = r.json()
    return JWKS_CACHE


def extract_bearer_token(auth_header: str | None) -> str:
    if not auth_header:
        abort(401, "Missing Authorization header")

    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        abort(401, "Invalid Authorization header")

    return parts[1]


def decode_access_token(token: str):
    jwks = get_jwks()
    keys = jwks["keys"]

    # Decode header to get the "kid"
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    # Find matching key in JWKS
    key_data = next((k for k in keys if k["kid"] == kid), None)

    if not key_data:
        abort(401, f"No matching JWKS key for kid={kid}")

    public_key = RSAAlgorithm.from_jwk(key_data)

    try:
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=SETTINGS.KEYCLOAK_CLIENT_ID,
            options={"verify_exp": True},
        )
        return decoded
    except jwt.ExpiredSignatureError:
        abort(401, "Token expired")
    except jwt.InvalidTokenError:
        abort(401, "Invalid token")
