# main.py

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from auth import oauth, setup_session
from config import KEYCLOAK_URL, REALM, BASE_URL

app = FastAPI()
setup_session(app)

# Check current session details
def get_current_user(request: Request):
    return request.session.get("user")
    if not user:
        # Redirect to login if no session
        raise HTTPException(status_code=307, headers={"Location": "/login"})
    return user


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path in ["/login", "/callback", "/static"]:
        return await call_next(request)

    if not request.session.get("user"):
        return RedirectResponse("/login")

    return await call_next(request)


# # Home route
# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     user = get_current_user(request)
#     if user:
#         return RedirectResponse("/welcome")
#     eles:
#         return ("/login")

# Login route
@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("callback")
    return await oauth.keycloak.authorize_redirect(request, redirect_uri)


# Get user details
@app.get("/callback")
async def callback(request: Request):
    token = await oauth.keycloak.authorize_access_token(request)
    user = token["userinfo"]

    request.session["user"] = {
        "name": user.get("preferred_username"),
        "email": user.get("email"),
        "sub": user.get("sub"),
    }

    return RedirectResponse("/welcome")

# Logout route
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    logout_url = (
        f"{BASE_URL}/protocol/openid-connect/logout"
        f"?redirect_uri=http://localhost:8000"
    )
    return RedirectResponse(logout_url)
