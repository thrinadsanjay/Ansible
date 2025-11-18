# welcome.py
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from auth import get_current_user

router = APIRouter()

@router.get("/welcome", response_class=HTMLResponse)
async def welcome(user: dict = Depends(get_current_user)):
    return f"""
    <h1>Welcome {user['name']}!</h1>
    <p>Email: {user['email']}</p>
    <a href="/logout">Logout</a>
    """
