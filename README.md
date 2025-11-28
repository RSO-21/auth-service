# auth-service

### Running MS

First setup instructions are below.

Run flask MS with:
python app.py

and also run docker container.

### First setup

First install all python requirements with:

pip install -r requirements.txt

Then set up **KEYCLOAK**

1. cd keycloak-local/
2. docker compose up (before install Docker Desktop if not already)

You'll see logs like:
Keycloak 23.0.x running on http://0.0.0.0:8080
Admin username: admin

3. Go to: http://localhost:8080

Click Administration Console
Login: admin / admin

4. In Keycloak:

- Left menu → Realm selector
- Click → Create realm
- Name: frifood

5. Backend uses KEYCLOAK_CLIENT_ID and KEYCLOAK_CLIENT_SECRET
   So you must create a confidential client.
   Left menu → Clients
   Create client

Settings:
Client ID: frifood-auth
Client type: OpenID Connect

Click Next
On Capability config:
✔ Client authentication → enabled
✔ Standard flow → enabled (optional)
✔ Direct access grants → enabled ← needed for /auth/login

Save

Now Keycloak will generate a client secret:
Clients → frifood-auth → Credentials
Copy it into .env:
KEYCLOAK_CLIENT_SECRET=your_secret

7. Create test users

Left menu → Users
Add user → username: testuser@test.com
Under Credentials:
Set password (password)
“Temporary” = OFF
Now this user can log in using your Angular login form.

8. Configure .env for Flask Auth Service in root of repo.
   FLASK_HOST=0.0.0.0
   FLASK_PORT=8001
   KEYCLOAK_BASE_URL=http://localhost:8080
   KEYCLOAK_REALM=frifood
   KEYCLOAK_CLIENT_ID=frifood-auth
   KEYCLOAK_CLIENT_SECRET=YOUR_SECRET_HERE

9. Left menu -> Clients
   Click frifood-auth
   Tab -> Client scopes
   Click frifood-auth-dedicated
   Tab -> Mappers
   Add Mapper -> By Configuration -> Audience

Fill the mapper form:
Name: audience-frifood-auth
Included Client Audience: frifood-auth
Add to ID token: ON
Add to acces token: ON
Add to token introspection: ON
Click save

This ensures that next login produces a token with "aud":frifood-auth

10. Test flow:
    Angular login form → enter:
    username: testuser@test.com
    password: password

Requests should succeed:
POST /auth/login → should return proper tokens
GET /auth/me → should return user claims
Angular should store token in local storage

---

Next time you want to start you don't have to do this all again. Also do not need to call docker compose up everytime, just start the container in Docker.
