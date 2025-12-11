from flask import Flask, make_response, request, jsonify
from config import SETTINGS
from keycloak_client import KeycloakClient
from models import LoginRequest
from security import extract_bearer_token, decode_access_token, set_token_cookies
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)
kc = KeycloakClient()

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
metrics = PrometheusMetrics(app, path=None)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})
metrics.info("app_info", "Auth service info", version="1.0.0")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/auth/login")
def login():
    body = request.json
    print("Login attempt with body:", body)

    if not body or "username" not in body or "password" not in body:
        return jsonify({"error": "Invalid request"}), 400

    data = LoginRequest(
        username=body["username"],
        password=body["password"]
    )

    try:
        tokens = kc.exchange_password_for_tokens(data)
    except ValueError:
        return jsonify({"error": "Invalid credentials"}), 401

    resp = make_response(jsonify({"status": "ok"}))
    return set_token_cookies(resp, tokens)

@app.post("/auth/signup")
def signup():
    data = request.json

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    try:
        kc.create_user(username, email, password)
        #login after signup
        tokens = kc.exchange_password_for_tokens(LoginRequest(username=username, password=password))
        resp = make_response(jsonify({"status": "ok"}))
        return set_token_cookies(resp, tokens)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.post("/auth/logout")
def logout():
    resp = make_response(jsonify({"status": "logged_out"}))
    resp.delete_cookie("access_token")
    resp.delete_cookie("refresh_token")
    return resp

@app.get("/auth/me")
def me():
    token = request.cookies.get("access_token")
    if not token:
        return jsonify({"error": "Not authenticated"}), 401

    claims = decode_access_token(token)

    return jsonify({
        "sub": claims["sub"],
        "email": claims.get("email"),
        "preferred_username": claims.get("preferred_username"),
        "roles": claims.get("realm_access", {}).get("roles", []),
    })


@app.get("/auth/check")
def check():
    auth = request.headers.get("Authorization")
    token = extract_bearer_token(auth)
    claims = decode_access_token(token)

    return jsonify({"message": f"Hello {claims.get('preferred_username', claims.get('sub'))}"})



if __name__ == "__main__":
    app.run(
        host=SETTINGS.FLASK_HOST,
        port=SETTINGS.FLASK_PORT,
        debug=True
    )
