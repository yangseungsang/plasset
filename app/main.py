from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os
import importlib
import sys

from app.api import assets
from app.routers import locations, auth
from app.database.database import engine, SessionLocal
from app.models import models
from app.init_db import init_db
from app.routers.auth import login_required, ACCESS_TOKEN_COOKIE_KEY
import sqlalchemy

# 데이터 디렉토리 확인 및 생성
data_dir = os.path.join(os.getcwd(), "data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    print(f"데이터 디렉토리 생성됨: {data_dir}")

# 데이터베이스에 연결 가능한지 확인
try:
    # 연결 테스트
    db = SessionLocal()
    db.execute(sqlalchemy.text("SELECT 1"))
    print("데이터베이스 연결 성공!")
    db.close()
except Exception as e:
    print(f"데이터베이스 연결 오류: {e}")

# 데이터베이스 테이블 생성 (이미 존재하는 테이블은 건드리지 않음)
print("데이터베이스 테이블 확인 및 생성 시작...")
# models.Base.metadata.drop_all(bind=engine)  # 기존 테이블 삭제 코드 제거
models.Base.metadata.create_all(bind=engine)  # 테이블이 없는 경우만 새로 생성
print("데이터베이스 테이블 확인 완료!")

# 샘플 데이터 생성 (데이터가 없는 경우에만)
db = SessionLocal()
if db.query(models.Category).count() == 0 and db.query(models.Location).count() == 0:
    print("샘플 데이터 생성 시작...")
    init_db()
    print("샘플 데이터 생성 완료!")
else:
    print("기존 데이터 유지...")
db.close()

app = FastAPI(title="자산관리 시스템")

# 인증 미들웨어 클래스
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 인증 없이 접근 가능한 경로 목록
        public_paths = [
            '/login', 
            '/logout',
            '/static',
            '/favicon.ico'
        ]
        
        path = request.url.path
        
        # 공개 경로는 인증 검사 제외
        for public_path in public_paths:
            if path.startswith(public_path):
                return await call_next(request)
            
        # 쿠키에서 토큰 확인
        token = request.cookies.get(ACCESS_TOKEN_COOKIE_KEY)
        if not token:
            print(f"미인증 접근 시도: {path}, 리다이렉트합니다.")
            # 로그인 페이지로 리다이렉트
            return RedirectResponse(url="/login", status_code=303)
            
        return await call_next(request)

# 인증 미들웨어 등록
app.add_middleware(AuthMiddleware)

# 정적 파일 마운트 - name 매개변수가 중요합니다
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="app/templates")

# API 라우터 등록
app.include_router(assets.router, prefix="/api", tags=["assets"])
app.include_router(locations.router)
app.include_router(auth.router)

def reload_modules():
    """개발 중 모듈 리로드 함수"""
    modules_to_reload = [
        "app.schemas",
        "app.models.models",
        "app.api.assets"
    ]
    
    for module_name in modules_to_reload:
        try:
            if module_name in sys.modules:
                print(f"모듈 리로드 중: {module_name}")
                importlib.reload(sys.modules[module_name])
            else:
                print(f"모듈 처음 로드 중: {module_name}")
                importlib.import_module(module_name)
        except Exception as e:
            print(f"모듈 리로드 오류 {module_name}: {str(e)}")

# 서버 시작 전 모듈 리로드
reload_modules()

@app.get("/")
async def root(request: Request, user = Depends(login_required)):
    """메인 페이지로 리다이렉트"""
    return RedirectResponse(url="/assets")


@app.get("/assets")
async def assets_page(request: Request, user = Depends(login_required)):
    """자산 목록 페이지"""
    return templates.TemplateResponse(
        "assets.html", {"request": request, "title": "자산 목록", "user": user}
    )


@app.get("/assets/create")
async def create_asset_page(request: Request, user = Depends(login_required)):
    """자산 추가 페이지"""
    return templates.TemplateResponse(
        "asset_form.html", {"request": request, "title": "자산 추가", "is_update": False, "user": user}
    )


@app.get("/assets/{asset_id}")
async def view_asset_page(request: Request, asset_id: int, user = Depends(login_required)):
    """자산 상세 페이지"""
    return templates.TemplateResponse(
        "asset_detail.html", {"request": request, "title": "자산 상세", "asset_id": asset_id, "user": user}
    )


@app.get("/assets/{asset_id}/edit")
async def edit_asset_page(request: Request, asset_id: int, user = Depends(login_required)):
    """자산 수정 페이지"""
    return templates.TemplateResponse(
        "asset_form.html", 
        {"request": request, "title": "자산 수정", "is_update": True, "asset_id": asset_id, "user": user}
    )


@app.get("/locations")
async def locations_page(request: Request, user = Depends(login_required)):
    """보관 장소 관리 페이지"""
    return templates.TemplateResponse(
        "locations.html", {"request": request, "title": "보관 장소 관리", "user": user}
    )


@app.get("/locations/{location_id}")
async def view_location_page(request: Request, location_id: int, user = Depends(login_required)):
    """위치 상세 및 자산 배치 페이지"""
    return templates.TemplateResponse(
        "location_detail.html", 
        {"request": request, "title": "위치 상세", "location_id": location_id, "user": user}
    )

@app.get("/categories")
async def categories_page(request: Request, user = Depends(login_required)):
    """카테고리 관리 페이지"""
    return templates.TemplateResponse(
        "categories.html", {"request": request, "title": "카테고리 관리", "user": user}
    ) 