from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dependencies import require_login
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def assets_list(request: Request, current_user: User = Depends(require_login)):
    """자산 목록 페이지를 반환합니다."""
    return templates.TemplateResponse(
        "assets.html", {"request": request, "current_user": current_user}
    )

@router.get("/add", response_class=HTMLResponse)
async def asset_form(request: Request, current_user: User = Depends(require_login)):
    """자산 추가 폼 페이지를 반환합니다."""
    return templates.TemplateResponse(
        "asset_form.html", 
        {
            "request": request, 
            "title": "자산 추가", 
            "is_update": False, 
            "current_user": current_user
        }
    )

@router.get("/{asset_id}", response_class=HTMLResponse)
async def asset_detail(asset_id: int, request: Request, current_user: User = Depends(require_login)):
    """자산 상세 페이지를 반환합니다."""
    return templates.TemplateResponse(
        "asset_detail.html", 
        {
            "request": request, 
            "asset_id": asset_id, 
            "current_user": current_user
        }
    )

@router.get("/{asset_id}/edit", response_class=HTMLResponse)
async def asset_edit_form(asset_id: int, request: Request, current_user: User = Depends(require_login)):
    """자산 수정 폼 페이지를 반환합니다."""
    return templates.TemplateResponse(
        "asset_form.html", 
        {
            "request": request, 
            "title": "자산 수정", 
            "is_update": True, 
            "asset_id": asset_id, 
            "current_user": current_user
        }
    ) 