FT_KEYCLOAK_URL = "https://keycloak.sanjay-lab.online"
REALM = "sanjay-lab"
CLIENT_ID = "fastapi"
CLIENT_SECRET = "ygDeNwcwZAhbUEoK2DQxcYRnrXZTyq4u"

REDIRECT_URI = "http://localhost:8000/callback"

OIDC_CONFIG_URL = f"{FT_KEYCLOAK_URL}/auth/realms/{REALM}/.well-known/openid-configuration"
BASE_URL = f"{FT_KEYCLOAK_URL}/auth/realms/{REALM}"