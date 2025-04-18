from fastapi import Depends, HTTPException, Request, status
from app.services.auth import get_current_user_from_cookie
from app.models.user import User
from typing import Optional

async def get_current_user(request: Request) -> Optional[User]:
    """현재 로그인한 사용자 정보를 반환합니다."""
    return await get_current_user_from_cookie(request)

async def require_login(current_user: Optional[User] = Depends(get_current_user)):
    """로그인이 필요한 페이지에 사용하는 종속성입니다."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            detail="로그인이 필요합니다.",
            headers={"Location": "/login"}
        )
    return current_user 