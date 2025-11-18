#KEYCLOAK_URL = "http://192.168.55.37:8080"
KEYCLOAK_URL = "https://keycloak.sanjay-lab.online"
REALM = "sanjay-lab"
CLIENT_ID = "fastapi"
CLIENT_SECRET = "WlnQrFAQm7oxdX0hl2SwJWc4HtfSj0NV"

REDIRECT_URI = "http://localhost:5000/callback"
BASE_URL = f"{KEYCLOAK_URL}/auth/realms/{REALM}"