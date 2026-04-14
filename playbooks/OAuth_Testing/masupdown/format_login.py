from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import subprocess
import os
import urllib.parse
from datetime import timedelta
import requests
import logging
from logging.handlers import RotatingFileHandler
#import jwt
from authlib.integrations.flask_client import OAuth
from authlib.integrations.requests_client import OAuth2Session
import sys


# Create logs/ directory if not exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure root logger
log_formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

file_handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=5 * 1024 * 1024,   # 5 MB per file
    backupCount=5               # keep last 5 log files
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

app = Flask(__name__)

# Attach handler to Flask’s logger
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# Secret key for sessions
app.secret_key = os.getenv("SECRET_KEY", "supersecret")

app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False

# Credentials (use hashed passwords in production)
USERNAME = os.getenv("WEB_USER", "commissioning")
PASSWORD = os.getenv("WEB_PASS", "ckc89")

# Set session lifetime (e.g., 15 minutes)
app.permanent_session_lifetime = timedelta(seconds=600)

# Allowed commands
ALLOWED_COMMANDS = {
    "container_status": "podman ps",
    "up": "./scripts/up.sh",
    "down": "./scripts/down.sh",
    "down_alt": "./scripts/down.sh --extras"
}

# HTML templates
TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Docker Commands</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f8f8f8;
        }
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .command-form {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }
        .command-form button,
        .command-form label {
            padding: 10px 16px;
            font-size: 14px;
            cursor: pointer;
        }
        #output {
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
        }
        pre {
            background: #f0f0f0;
            padding: 15px;
            border: 1px solid #ccc;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
    </style>
    <script>
    function showLoading() {
        document.getElementById('output').innerHTML = '<h3>Running...</h3>';
    }
    </script>
</head>
<body>
    <div class="top-bar">
        <h2>Container Up and Down</h2>
        <h4> Welcome, {{ session['user'] }}</h4>
        <p><a href="{{ url_for('logout') }}">Logout</a></p>
    </div>
    <p style="color: #aa0000; font-weight: bold; margin-top: 5px;">
       ⚠️ This session will automatically log out after 5 minutes of inactivity.
    </p>

    <ul style="margin-top: 0; margin-bottom: 20px; padding-left: 20px; color: #555;">
        <li>Click <strong>Container Status</strong> to view running containers.</li>
        <li>Use <strong>Up</strong> to start your environment.</li>
        <li>Use <strong>Down</strong> to stop containers.</li>
        <li>Check the box to also stop extras when using Down.</li>
    </ul>

    <form method="POST" class="command-form" onsubmit="showLoading()">
        <button name="cmd" value="container_status">Container Status</button>
        <button name="cmd" value="up">Up</button>
        <button name="cmd" value="down">Down</button>
        <label>
            <input type="checkbox" name="alt_toggle" value="1">
            Down all extras containers too
        </label>
    </form>

    <div id="output">
    {% if output %}
        <h3>Output:</h3>
        <pre>{{ output }}</pre>
    {% endif %}
    </div>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-box {
            background: #fff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            width: 320px;
            box-sizing: border-box;
        }
        .login-box h2 {
            margin-bottom: 20px;
            text-align: left;
        }
        .login-box form {
            display: flex;
            flex-direction: column;
        }
        .login-box input[type="text"],
        .login-box input[type="password"],
        .login-box button {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border-radius: 6px;
            box-sizing: border-box;
            font-size: 14px;
        }
        .login-box input[type="text"],
        .login-box input[type="password"] {
            border: 1px solid #ccc;
            background: #eee;
        }
        .login-box button {
            background: #000;
            color: #fff;
            border: none;
            font-weight: bold;
            cursor: pointer;
        }
        .oauth-box button {
            background: #6495ED;
            color: #fff;
            border: none;
            font-weight: bold;
            cursor: pointer;
        }
        .custom-divider {
            border: none; 
            border-top: 2px solid #ccc;
            margin: 20px 0; 
        }
        ul {
            color: red;
            padding-left: 20px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>User login</h2>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <ul>{% for msg in messages %}<li>{{ msg }}</li>{% endfor %}</ul>
            {% endif %}
        {% endwith %}
        <form method="post">
            <input type="text" name="username" placeholder="username" required>
            <input type="password" name="password" placeholder="password" required>
            <button type="submit">Login</button>

        {% if openid_enabled %}
            <hr class="custom-divider">
            <div class="oauth-box">
                <button type="button" class="oauth-btn" onclick="window.location='{{ url_for('oauth_login') }}'">
                    Login with {{ openid_name }}
                </button>
            {% endif %} 
        </div>
        </form>
    </div>
</body>
</html>
"""

openid_enabled = os.environ.get("openid_enabled", "True")
openid_name = os.environ.get("openid_name", "Keycloak")
openid_config_url = os.environ.get("openid_config_url")
openid_client_id = os.environ.get("openid_client_id")
openid_secret = os.environ.get("openid_secret")
openid_scope = os.environ.get("openid_scope", "openid profile email")
redirect_uri= os.environ.get("redirect_uri")
SSL_CERT_FILE = os.environ.get("SSL_CERT_FILE", None)


# Initialize OAuth and Keycloak
oauth = OAuth(app)
keycloak = oauth.register(
    name="keycloak",
    server_metadata_url=openid_config_url,
    client_id=openid_client_id,
    client_secret=openid_secret,
    client_kwargs={"scope": openid_scope, "verify": SSL_CERT_FILE },
    server_metadata_url_kwargs={"verify": SSL_CERT_FILE},
)

# Routes
@app.before_request
def log_request_info():
    app.logger.info(f"Route accessed: {request.path} Method: {request.method}")
    if request.method == 'POST':
        app.logger.info(f"Form data: {request.form}")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        app.logger.info(f'Login attempt for user: {username}')

        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session.permanent = True
            session['user'] = USERNAME
            app.logger.info(f'Successful login for user: {username}')
            return redirect(url_for('index'))
        else:
            app.logger.warning(f'Failed login for user: {username}')
            flash("Invalid credentials")
            return redirect(url_for('login'))
    return render_template_string(LOGIN_TEMPLATE, openid_enabled=openid_enabled, openid_name=openid_name )


@app.route('/oauth/login')
def oauth_login():
    return keycloak.authorize_redirect(redirect_uri=redirect_uri)    

@app.route('/callback')
def oauth_callback():
    token = keycloak.authorize_access_token()
    if not token:
        app.logger.error('Failed to obtain token from Keycloak')
        flash("Authentication failed")
        return redirect(url_for('login'))

    userinfo = keycloak.userinfo(token=token)
    if not userinfo:
            app.logger.error("Failed to fetch user info from Keycloak")
            flash("Failed to retrieve user info")
            return redirect(url_for('login'))

    userinfo =  token.get("userinfo")
    session["user"] = userinfo.get("preferred_username")
    session["user_info"] = {
        "name": userinfo.get("preferred_username"),
        "email": userinfo.get("email"),
        "sub": userinfo.get("sub"),
        "auth_type": "keycloak"
    }
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    user = session.get("user_info")
    
    if user and user.get("auth_type") == "keycloak":
        # Keycloak logout URL
        response = requests.get(openid_config_url)
        keycloak_logout_url = response.json().get("end_session_endpoint")

        # Add redirect back to your app after logout
        redirect_after_logout = url_for('index', _external=True)
        session.clear()
        logout_redirect = url_for('index', _external=True)

        return redirect(
            f"{keycloak_logout_url}"
            f"?post_logout_redirect_uri={logout_redirect}"
            f"&client_id={openid_client_id}"
        )

    app.logger.info(f'Successful logout')
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        cmd_key = request.form.get('cmd')
        use_alt = request.form.get('alt_toggle') == '1'

        app.logger.info(f"User ran command: {cmd_key}")
        os.chdir(os.path.expanduser('~/ti-sdv-install'))
        app.logger.info(os.getcwd())

        if cmd_key == "down" and use_alt:
            command = ALLOWED_COMMANDS.get("down_alt")
        else:
            command = ALLOWED_COMMANDS.get(cmd_key)

        if command:
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                app.logger.info(f"Executed command: {cmd_key}")
                app.logger.info(result)
                session['output'] = result.stdout
            except subprocess.CalledProcessError as e:
                app.logger.info(f"Failed command: {cmd_key}")
                session['output'] = f"Error:\n{e.stderr}"
        return redirect(url_for('index'))

    output = session.pop('output', '')
    return render_template_string(TEMPLATE, output=output)

# Disable caching
@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3111)
