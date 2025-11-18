# auth.py
import requests
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from config import (
    CLIENT_ID, CLIENT_SECRET, REDIRECT_URI,
    OIDC_CONFIG_URL
)

# Load OIDC metadata
metadata = requests.get(OIDC_CONFIG_URL, verify=False).json()

oauth = OAuth(Config())

oauth.register(
    name='keycloak',
    server_metadata_url=OIDC_CONFIG_URL,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        'scope': 'openid profile email',
        'verify': False
    }
)

def setup_session(app):
    app.add_middleware(SessionMiddleware, secret_key="SUPERSECRETKEY")
