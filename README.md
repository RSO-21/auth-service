# auth-service

### Running MS

First setup instructions are below.

Run flask MS with:
```
python app.py
```

or build the container:
```
docker build -t auth-service .
docker run --env-file .env -p 8005:8000 auth-service
```

The same image is consumed by the shared `dev-stack/docker-compose.yml`, which also launches Keycloak + Postgres so everything is wired together automatically.

### First setup

Contact me for .env.

First install all python requirements with:

```
pip install -r requirements.txt
```

Then set up **KEYCLOAK**
Make sure you have Docker Desktop installed

1. cd keycloak-local/
2. docker compose up -d (or rely on the dev stack compose file which already includes this service)
   Check Docker Desktop to see container running.

Test flow:
Angular login form → enter:
username: testuser@test.com
password: password

Requests should succeed:
POST /auth/login → should return proper tokens
GET /auth/me → should return user claims
Angular should store token in local storage

---

Next time you want to start you don't have to do this all again. Also do not need to call docker compose up everytime, just start the container in Docker.
