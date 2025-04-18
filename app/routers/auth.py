from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Optional

from app.database.database import get_db
from app.models.models import User
from app.utils.auth import (
    authenticate_user, 
    create_access_token, 
    get_password_hash
)

router = APIRouter()

# 템플릿 설정
templates = Jinja2Templates(directory="app/templates")

# 쿠키 설정
ACCESS_TOKEN_COOKIE_KEY = "access_token"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7일

# 인증 관련 라우트

@router.get("/login")
async def login_page(request: Request):
    """로그인 페이지"""
    return templates.TemplateResponse(
        "login.html", {"request": request, "title": "로그인"}
    )

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """로그인 처리"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse(
            "login.html", 
            {
                "request": request, 
                "title": "로그인", 
                "error": "아이디 또는 비밀번호가 올바르지 않습니다."
            },
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    # 토큰 생성
    access_token = create_access_token(
        data={"sub": user.username}
    )
    
    # 쿠키에 토큰 저장
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_KEY,
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    return response

@router.get("/logout")
async def logout(response: Response):
    """로그아웃 처리"""
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    # 쿠키 삭제 처리
    response.delete_cookie(ACCESS_TOKEN_COOKIE_KEY)
    # 추가적으로 브라우저에 쿠키 삭제 지시
    response.headers["Clear-Site-Data"] = '"cookies"'
    return response

# 사용자 관리자만 접근 가능한 API 엔드포인트
@router.post("/register")
async def register_user(
    username: str, 
    password: str, 
    email: Optional[str] = None, 
    full_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """새 사용자 등록 (관리 목적)"""
    # 중복 사용자 확인
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자 이름이 이미 사용 중입니다."
        )
    
    # 새 사용자 생성
    hashed_password = get_password_hash(password)
    new_user = User(
        username=username,
        hashed_password=hashed_password,
        email=email,
        full_name=full_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "사용자가 성공적으로 등록되었습니다."}

# 인증 확인 미들웨어 함수
async def verify_token_cookie(request: Request, db: Session = Depends(get_db)):
    """쿠키에서 토큰을 확인하고 인증된 사용자를 반환"""
    from jose import jwt, JWTError
    from app.utils.auth import SECRET_KEY, ALGORITHM
    
    token = request.cookies.get(ACCESS_TOKEN_COOKIE_KEY)
    if not token:
        print("토큰이 없음")
        return None
    
    try:
        # 토큰 검증
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        exp_time = payload.get("exp")
        
        # 사용자명 확인
        if not username:
            print("토큰에 사용자명 없음")
            return None
            
        # 만료 시간 확인
        if not exp_time or datetime.utcnow() > datetime.fromtimestamp(exp_time):
            print("토큰 만료됨")
            return None
        
        # 사용자 존재 여부 확인
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"사용자 {username} 없음")
            return None
            
        return user
    except JWTError as e:
        print(f"JWT 토큰 오류: {str(e)}")
        return None
    except Exception as e:
        print(f"토큰 검증 중 예외 발생: {str(e)}")
        return None

# 인증 요구 미들웨어
def login_required(request: Request, db: Session = Depends(get_db)):
    """사용자가 로그인되어 있어야 접근 가능한 페이지를 위한 의존성"""
    user = verify_token_cookie(request, db)
    if user is None:
        # 로그인 페이지로 리다이렉트
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"}
        )
    return user 