from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/optimization", tags=["Оптимизация"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def optimization_page(request: Request):
    return templates.TemplateResponse("optimization.html", {"request": request})