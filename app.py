from flask import Flask, make_response, request, jsonify
from flask_restx import Api, Resource
from config import SETTINGS
from keycloak_client import KeycloakClient
from models import LoginRequest
from security import extract_bearer_token, decode_access_token, set_token_cookies
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from rabbitmq_publisher import publish_user_created
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

api = Api(
    app,
    title="Auth Service API",
    version="1.0",
    description="Authentication & Authorization API",
    doc="/docs"  # 👈 Swagger UI path
)

ns = api.namespace("auth", description="Auth operations")

kc = KeycloakClient()

CORS(app, resources={r"/*": {"origins": ["http://localhost:4200"]}}, supports_credentials=True)
metrics = PrometheusMetrics(app, path=None)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})
metrics.info("app_info", "Auth service info", version="1.0.0")

@api.route("/health")  # note: api.route works too
class Health(Resource):
    def get(self):
        return {"status": "ok"}, 200


@ns.route("/login")     # becomes /auth/login because namespace = "auth"
class Login(Resource):
    def post(self):
        body = request.json
        if not body or "username" not in body or "password" not in body:
            return {"error": "Invalid request"}, 400

        data = LoginRequest(username=body["username"], password=body["password"])

        try:
            tokens = kc.exchange_password_for_tokens(data)
        except ValueError:
            return {"error": "Invalid credentials"}, 401

        resp = make_response(jsonify({"status": "ok"}))
        return set_token_cookies(resp, tokens)


@ns.route("/signup")
class Signup(Resource):
    def post(self):
        data = request.json or {}
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        logger.info("[SIGNUP] Creating user in Keycloak: %s", username)

        if not username or not email or not password:
            return {"error": "Missing fields"}, 400

        try:
            user_id = kc.create_user(username, email, password)
            logger.info("[SIGNUP] User created in Keycloak with ID: %s", user_id)
            
            publish_user_created(
                user_id=user_id,
                username=username,
                email=email
            )
            
            tokens = kc.exchange_password_for_tokens(LoginRequest(username=username, password=password))
            resp = make_response(jsonify({"status": "ok"}))
            return set_token_cookies(resp, tokens)
        except Exception as e:
            logger.error("[SIGNUP] Error during signup: %s", str(e))
            return {"error": str(e)}, 400


@ns.route("/logout")
class Logout(Resource):
    def post(self):
        resp = make_response(jsonify({"status": "logged_out"}))
        resp.delete_cookie("access_token")
        resp.delete_cookie("refresh_token")
        return resp


@ns.route("/me")
class Me(Resource):
    def get(self):
        token = request.cookies.get("access_token")
        if not token:
            return {"error": "Not authenticated"}, 401

        claims = decode_access_token(token)
        return {
            "sub": claims["sub"],
            "email": claims.get("email"),
            "preferred_username": claims.get("preferred_username"),
            "roles": claims.get("realm_access", {}).get("roles", []),
        }, 200


@ns.route("/check")
class Check(Resource):
    def get(self):
        auth = request.headers.get("Authorization")
        token = extract_bearer_token(auth)
        claims = decode_access_token(token)
        return {"message": f"Hello {claims.get('preferred_username', claims.get('sub'))}"}, 200



if __name__ == "__main__":
    app.run(
        host=SETTINGS.FLASK_HOST,
        port=SETTINGS.FLASK_PORT,
        debug=True
    )
