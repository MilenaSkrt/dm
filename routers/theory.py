from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/theory", tags=["Теория"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def theory_page(request: Request):
    return templates.TemplateResponse("theory.html", {"request": request})