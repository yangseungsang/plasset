from fastapi import APIRouter
from app.routes import auth
from app.routes import assets

router = APIRouter()

# 라우터 등록
router.include_router(auth.router, tags=["auth"])
router.include_router(assets.router, prefix="/assets", tags=["assets"]) 