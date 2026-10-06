import bleach
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.database import comments

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/comments", response_class=HTMLResponse)
def get_comments(request: Request):
    return templates.TemplateResponse("comments.html", {"request": request, "comments": comments})


@router.post("/comments", response_class=HTMLResponse)
def post_comment(request: Request, comment: str = Form(...)):
    clean = bleach.clean(comment)
    comments.append(clean)
    return templates.TemplateResponse("comments.html", {"request": request, "comments": comments})
