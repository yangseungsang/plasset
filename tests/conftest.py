import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database.database import Base, get_db
from app.utils.auth import get_password_hash
from app.models.models import User, Category, Location, NetworkType, Owner

# 테스트용 데이터베이스 설정
TEST_DB_PATH = "test_asset_management.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///./{TEST_DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 테스트용 DB 세션 의존성 오버라이드
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """테스트 데이터베이스 초기화 및 샘플 데이터 생성"""
    # 기존에 테스트 DB가 있다면 삭제
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # 샘플 데이터 생성
    db = TestingSessionLocal()
    try:
        # 테스트 유저 생성
        hashed_password = get_password_hash("testpassword")
        test_user = User(
            username="testuser",
            email="test@example.com",
            full_name="테스트 사용자",
            hashed_password=hashed_password,
            is_active=True
        )
        
        # 카테고리 생성
        categories = [
            Category(name="노트북", description="노트북 장비"),
            Category(name="서버", description="서버 장비"),
            Category(name="네트워크", description="네트워크 장비")
        ]
        
        # 위치 생성
        locations = [
            Location(name="본사 1층", image_path="/static/images/location_1.jpg"),
            Location(name="본사 2층", image_path="/static/images/location_2.jpg"),
            Location(name="데이터센터", image_path="/static/images/location_3.jpg")
        ]
        
        # 네트워크 타입 생성
        network_types = [
            NetworkType(name="사내망", description="회사 내부 네트워크"),
            NetworkType(name="장비망", description="장비 전용 네트워크"),
            NetworkType(name="없음", description="네트워크 미사용")
        ]
        
        # 소유자 생성
        owners = [
            Owner(name="IT팀", department="IT부서", contact="it@example.com"),
            Owner(name="개발팀", department="개발부서", contact="dev@example.com")
        ]
        
        # DB에 추가
        db.add(test_user)
        db.add_all(categories)
        db.add_all(locations)
        db.add_all(network_types)
        db.add_all(owners)
        
        db.commit()
    finally:
        db.close()
    
    # 테스트 종료 후 정리
    yield
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(scope="function")
def test_db():
    """테스트용 DB 세션 픽스처"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    """API 테스트를 위한 TestClient 픽스처"""
    # 의존성 오버라이드
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def authenticated_client(client):
    """인증된 테스트 클라이언트"""
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpassword"},
        allow_redirects=False
    )
    
    # 쿠키에서 세션 추출
    cookies = response.cookies
    
    # 새 클라이언트에 세션 설정
    client.cookies = cookies
    
    return client 