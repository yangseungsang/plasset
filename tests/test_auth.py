import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.utils.auth import get_password_hash


def test_login_success(client):
    """로그인 성공 테스트"""
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpassword"},
        allow_redirects=False
    )
    
    # 리다이렉트 상태 코드 확인
    assert response.status_code == status.HTTP_302_FOUND
    
    # 쿠키에 액세스 토큰이 설정되었는지 확인
    assert "access_token" in response.cookies
    
    # 리다이렉션 URL 확인
    assert response.headers["location"] == "/"


def test_login_failure(client):
    """로그인 실패 테스트"""
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "wrongpassword"},
        allow_redirects=False
    )
    
    # 401 Unauthorized 또는 로그인 페이지로 반환되는지 확인
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # 에러 메시지가 응답에 포함되어 있는지 확인
    assert "아이디 또는 비밀번호가 올바르지 않습니다" in response.text


def test_logout(client):
    """로그아웃 테스트"""
    # 먼저 로그인
    login_response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpassword"},
        allow_redirects=False
    )
    
    # 로그인 쿠키를 저장
    cookies = login_response.cookies
    
    # 로그아웃 요청
    client.cookies = cookies
    logout_response = client.get("/logout", allow_redirects=False)
    
    # 리다이렉트 상태 코드 확인
    assert logout_response.status_code == status.HTTP_302_FOUND
    
    # 쿠키가 삭제되었는지 확인 (쿠키 값이 삭제되거나 만료됨)
    assert "access_token" not in logout_response.cookies or not logout_response.cookies["access_token"].value
    
    # 리다이렉션 URL이 로그인 페이지인지 확인
    assert logout_response.headers["location"] == "/login"


def test_protected_route_with_auth(authenticated_client):
    """인증된 사용자의 보호된 경로 접근 테스트"""
    # 자산 목록 페이지 접근 (보호된 경로)
    response = authenticated_client.get("/assets")
    
    # 성공적으로 접근 가능해야 함
    assert response.status_code == 200
    
    # 페이지 내용에 적절한 내용이 포함되어 있는지 확인
    assert "자산 목록" in response.text


def test_protected_route_without_auth(client):
    """인증되지 않은 사용자의 보호된 경로 접근 테스트"""
    # 자산 목록 페이지 접근 시도 (로그인 없이)
    response = client.get("/assets", allow_redirects=False)
    
    # 로그인 페이지로 리다이렉트 되어야 함
    assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_307_TEMPORARY_REDIRECT]
    assert "/login" in response.headers["location"]


def test_register_user(client, test_db):
    """사용자 등록 테스트"""
    # 새 사용자 등록
    response = client.post(
        "/register",
        params={
            "username": "newuser",
            "password": "newpassword",
            "email": "newuser@example.com",
            "full_name": "New User"
        }
    )
    
    # 등록 성공 확인
    assert response.status_code == 200
    assert "성공적으로 등록" in response.json()["message"]
    
    # 새 사용자로 로그인 시도
    login_response = client.post(
        "/login",
        data={"username": "newuser", "password": "newpassword"},
        allow_redirects=False
    )
    
    # 로그인 성공 확인
    assert login_response.status_code == status.HTTP_302_FOUND
    assert "access_token" in login_response.cookies


def test_register_duplicate_user(client, test_db):
    """중복 사용자 등록 테스트"""
    # 기존 사용자와 동일한 이름으로 등록 시도
    response = client.post(
        "/register",
        params={
            "username": "testuser",  # 이미 존재하는 사용자명
            "password": "newpassword",
            "email": "another@example.com",
            "full_name": "Duplicate User"
        }
    )
    
    # 등록 실패 확인
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "이미 사용 중" in response.json()["detail"] 