from flask import Blueprint, session, render_template
from auth import login_required

welcome_bp = Blueprint("welcome", __name__)

@welcome_bp.route("/welcome")
@login_required
def welcome():
    user = session["user"]
    return render_template("welcome.html", user=user)
