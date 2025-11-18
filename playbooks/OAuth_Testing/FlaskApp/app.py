from flask import Flask, session, redirect
from flask_session import Session
from config import REDIRECT_URI, BASE_URL
from welcome import welcome_bp
from auth import keycloak
import auth  # import the auth module, not the keycloak object directly
from authlib.integrations.requests_client import OAuth2Session
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)
app.secret_key = "super-secret-key"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

# Initialize OAuth and Keycloak
auth.init_oauth(app)

# Register blueprint
app.register_blueprint(welcome_bp)


@app.route("/")
def index():
    if "user" in session:
        return redirect("/welcome")
    return redirect("/login")


@app.route("/login")
def login():
    # Access keycloak via auth.keycloak
    auth.keycloak.session = OAuth2Session(
        auth.keycloak.client_id,
        auth.keycloak.client_secret,
        verify=False,  # <-- critical
    )
    return auth.keycloak.authorize_redirect(REDIRECT_URI)


@app.route("/callback")
def callback():
    token = auth.keycloak.authorize_access_token()
    userinfo =  token.get("userinfo") #auth.keycloak.parse_id_token(token)
    session["user"] = {
        "name": userinfo.get("preferred_username"),
        "email": userinfo.get("email"),
        "sub": userinfo.get("sub"),
    }
    return redirect("/welcome")


@app.route("/logout")
def logout():
    session.clear()
    logout_url = f"{BASE_URL}/protocol/openid-connect/logout?redirect_uri=http://localhost:5000"
    return redirect(logout_url)


if __name__ == "__main__":
    app.run(debug=True)
