from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from pydantic import BaseModel, Field

from app.service import user_service, explanation_service
from app.repositories import user_repository
from app.models.user_model import User
from app.models.explanation_model import Explanation
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Pydantic Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: str
    password: str

class ExplanationCreate(BaseModel):
    class_: str = Field(..., alias="class")
    lock_part: str = Field(..., alias="lock-part")
    reason: str

class ProcessApplication(BaseModel):
    application_id: int
    action: str

async def get_current_user_fastapi(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    username = request.cookies.get("username")
    if username:
        return user_repository.get_user_by_username(db, username)
    return None

@router.get("/", response_class=HTMLResponse)
async def index(request: Request, current_user: Annotated[Optional[User], Depends(get_current_user_fastapi)]):
    return templates.TemplateResponse("index.html", {"request": request, "user": current_user})

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request, current_user: Annotated[Optional[User], Depends(get_current_user_fastapi)]):
    return templates.TemplateResponse("login.html", {"request": request, "user": current_user, "error": None})

@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    error = None

    user = user_service.login_user(db, email, password)
    if user:
        response = RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="username", value=user.username, httponly=True, samesite="Lax")
        return response
    else:
        error = 'Email or password is incorrect'
        return templates.TemplateResponse("login.html", {"request": request, "user": None, "error": error})

@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request, current_user: Annotated[Optional[User], Depends(get_current_user_fastapi)]):
    return templates.TemplateResponse("register.html", {"request": request, "user": current_user, "error": None})

@router.post("/register", response_class=HTMLResponse)
async def register_post(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = form.get("username")
    email = form.get("email")
    password = form.get("password")
    error = None

    result = user_service.register_user(db, username, email, password)
    if result:
        response = RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="username", value=username, httponly=True, samesite="Lax")
        return response
    else:
        error = 'User already exists'
        return templates.TemplateResponse("register.html", {"request": request, "user": None, "error": error})

@router.get("/logout")
async def logout():
    response = RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="username")
    return response

@router.get("/explanation", response_class=HTMLResponse)
async def explanation(request: Request, current_user: Annotated[Optional[User], Depends(get_current_user_fastapi)], db: Session = Depends(get_db)):
    explanations = explanation_service.get_all_explanations(db)
    return templates.TemplateResponse("explanation.html", {"request": request, "user": current_user, "explanations": explanations})

@router.get("/create", response_class=HTMLResponse)
async def create_get(request: Request, current_user: Annotated[Optional[User], Depends(get_current_user_fastapi)]):
    if not current_user:
        return RedirectResponse(url=router.url_path_for("login_get"), status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("create.html", {"request": request, "user": current_user})

@router.post("/create", response_class=HTMLResponse)
async def create_post(request: Request, current_user: Annotated[Optional[User], Depends(get_current_user_fastapi)], db: Session = Depends(get_db)):
    if not current_user:
        return RedirectResponse(url=router.url_path_for("login_get"), status_code=status.HTTP_302_FOUND)

    form = await request.form()
    class_ = form.get("class")
    lock_part = form.get("lock-part")
    reason = form.get("reason")

    explanation_service.create_explanation(
        db,
        student_username=current_user.username,
        student_email=current_user.email,
        class_=class_,
        lock_part=lock_part,
        reason=reason
    )
    return RedirectResponse(url=router.url_path_for("explanation"), status_code=status.HTTP_302_FOUND)

@router.get("/users", response_class=HTMLResponse)
async def users(request: Request, current_user: Annotated[Optional[User], Depends(get_current_user_fastapi)], db: Session = Depends(get_db)):
    if not current_user or not current_user.admin:
        return RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_302_FOUND)
    users_list = db.query(User).all()
    return templates.TemplateResponse("users.html", {"request": request, "users": users_list, "user": current_user})

@router.post("/make_manager/{user_id}")
async def make_manager(user_id: int, current_user: Annotated[Optional[User], Depends(get_current_user_fastapi)], db: Session = Depends(get_db)):
    if not current_user or not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    user = user_repository.get_user_by_id(db, user_id)
    if user:
        user.manager = True
        db.commit()
        db.refresh(user)
    return RedirectResponse(url=router.url_path_for("users"), status_code=status.HTTP_302_FOUND)

@router.post("/make_admin/{user_id}")
async def make_admin(user_id: int, current_user: Annotated[Optional[User], Depends(get_current_user_fastapi)], db: Session = Depends(get_db)):
    if not current_user or not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    user = user_repository.get_user_by_id(db, user_id)
    if user:
        user.admin = True
        db.commit()
        db.refresh(user)
    return RedirectResponse(url=router.url_path_for("users"), status_code=status.HTTP_302_FOUND)

@router.get("/submition", response_class=HTMLResponse)
async def submition(request: Request, current_user: Annotated[Optional[User], Depends(get_current_user_fastapi)], db: Session = Depends(get_db)):
    if not current_user or (not current_user.manager and not current_user.admin):
        return RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_302_FOUND)

    explanations = explanation_service.get_pending_explanations(db)
    return templates.TemplateResponse("submition.html", {"request": request, "user": current_user, "explanations": explanations})

@router.post("/process_application")
async def process_application(request: Request, current_user: Annotated[Optional[User], Depends(get_current_user_fastapi)], db: Session = Depends(get_db)):
    if not current_user or (not current_user.manager and not current_user.admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    form = await request.form()
    application_id = form.get("application_id")
    action = form.get("action")

    if application_id and action:
        explanation_service.process_application(db, int(application_id), action, current_user.username)
    return RedirectResponse(url=router.url_path_for("submition"), status_code=status.HTTP_302_FOUND)
