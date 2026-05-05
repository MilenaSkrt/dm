from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/tryyourself", tags=["Попробуй сам"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def tryyourself_page(request: Request):
    return templates.TemplateResponse("tryyourself.html", {"request": request})