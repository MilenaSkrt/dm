from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/physics", tags=["Обучение"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def physics_page(request: Request):
    return templates.TemplateResponse("physics.html", {"request": request})