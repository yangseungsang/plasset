from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth import authenticate_user, create_access_token
from app.services.auth import get_current_user, get_password_hash
from app.models.user import User
from app.config import settings
from typing import Optional
import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    """로그인 페이지를 렌더링합니다."""
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": error}
    )

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    username: str = None,
    password: str = None,
    remember: bool = False,
):
    """로그인 처리를 합니다."""
    # OAuth2PasswordRequestForm 대신 일반 form 처리
    if not username or not password:
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")
        remember = form_data.get("remember") in ["true", "on", "1", "yes"]

    # 사용자 인증
    user = authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "아이디 또는 비밀번호가 올바르지 않습니다."
            },
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    # 액세스 토큰 생성
    token_expires = datetime.timedelta(days=30 if remember else 1)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=token_expires
    )

    # 쿠키에 토큰 저장
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    if remember:
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=30 * 24 * 60 * 60,  # 30일
            expires=30 * 24 * 60 * 60,  # 30일
            samesite="lax",
            secure=settings.COOKIE_SECURE
        )
    else:
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            samesite="lax",
            secure=settings.COOKIE_SECURE
        )

    return response

@router.get("/logout")
async def logout(response: Response):
    """로그아웃 처리를 합니다."""
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response 