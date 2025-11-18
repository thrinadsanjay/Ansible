from flask import session, redirect
from authlib.integrations.flask_client import OAuth
from authlib.integrations.requests_client import OAuth2Session
from config import BASE_URL, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
import urllib3

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

oauth = OAuth()
keycloak = None

def init_oauth(app):
    global keycloak
    oauth.init_app(app)
    keycloak = oauth.register(
        name="keycloak",
        server_metadata_url=f"{BASE_URL}/.well-known/openid-configuration",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        client_kwargs={"scope": "openid profile email"},
        client_class=OAuth2Session,
        fetch_token=lambda url, **kwargs: oauth.keycloak.fetch_token(url, verify=False, **kwargs),
        server_metadata_url_kwargs={"verify": False},  # <-- critical
        # Add this to force all requests to skip SSL verification
        client_metadata={"verify": False}
    )

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated
