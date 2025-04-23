import pytest
from datetime import date
from sqlalchemy.orm import Session

from app.models.models import Asset, Category, Location, User, AssetHistory, NetworkType, Owner
from app.utils.auth import get_password_hash
import json


def test_db_connection(test_db):
    """데이터베이스 연결 테스트"""
    # 간단한 쿼리 실행으로 연결 확인
    result = test_db.execute("SELECT 1").fetchone()
    assert result[0] == 1


def test_category_crud(test_db):
    """카테고리 CRUD 테스트"""
    # 생성
    new_category = Category(name="테스트 카테고리", description="테스트 설명")
    test_db.add(new_category)
    test_db.commit()
    test_db.refresh(new_category)
    
    assert new_category.id is not None
    assert new_category.name == "테스트 카테고리"
    
    # 조회
    category = test_db.query(Category).filter(Category.name == "테스트 카테고리").first()
    assert category is not None
    assert category.description == "테스트 설명"
    
    # 수정
    category.description = "수정된 설명"
    test_db.commit()
    test_db.refresh(category)
    
    updated_category = test_db.query(Category).filter(Category.id == category.id).first()
    assert updated_category.description == "수정된 설명"
    
    # 삭제
    test_db.delete(category)
    test_db.commit()
    
    deleted_category = test_db.query(Category).filter(Category.id == category.id).first()
    assert deleted_category is None


def test_location_crud(test_db):
    """위치 CRUD 테스트"""
    # 생성
    new_location = Location(name="테스트 위치", image_path="/static/images/test.jpg")
    test_db.add(new_location)
    test_db.commit()
    test_db.refresh(new_location)
    
    assert new_location.id is not None
    assert new_location.name == "테스트 위치"
    
    # 조회
    location = test_db.query(Location).filter(Location.name == "테스트 위치").first()
    assert location is not None
    assert location.image_path == "/static/images/test.jpg"
    
    # 수정
    location.image_path = "/static/images/updated.jpg"
    test_db.commit()
    test_db.refresh(location)
    
    updated_location = test_db.query(Location).filter(Location.id == location.id).first()
    assert updated_location.image_path == "/static/images/updated.jpg"
    
    # 삭제
    test_db.delete(location)
    test_db.commit()
    
    deleted_location = test_db.query(Location).filter(Location.id == location.id).first()
    assert deleted_location is None


def test_asset_crud(test_db):
    """자산 CRUD 테스트"""
    # 필요한 관련 데이터 생성
    category = Category(name="테스트 카테고리", description="테스트 설명")
    location = Location(name="테스트 위치", image_path="/static/images/test.jpg")
    owner = Owner(name="테스트 소유자", department="테스트 부서")
    network_type = NetworkType(name="테스트 네트워크", description="테스트 네트워크 설명")
    
    test_db.add_all([category, location, owner, network_type])
    test_db.commit()
    
    # 자산 생성
    new_asset = Asset(
        name="테스트 자산",
        category=category.name,
        serial_number="TEST-SN-001",
        management_number="TEST-MN-001",
        acquisition_date=date.today(),
        description="테스트 자산 설명",
        location=location.name,
        owner=owner.name,
        network_type=network_type.name,
        is_in_use=True,
        mac_address="AA:BB:CC:DD:EE:FF",
        ip_address="192.168.0.100"
    )
    
    test_db.add(new_asset)
    test_db.commit()
    test_db.refresh(new_asset)
    
    assert new_asset.id is not None
    assert new_asset.name == "테스트 자산"
    assert new_asset.serial_number == "TEST-SN-001"
    
    # 자산 조회
    asset = test_db.query(Asset).filter(Asset.serial_number == "TEST-SN-001").first()
    assert asset is not None
    assert asset.category == "테스트 카테고리"
    assert asset.location == "테스트 위치"
    
    # 자산 수정
    asset.description = "수정된 자산 설명"
    asset.is_in_use = False
    test_db.commit()
    test_db.refresh(asset)
    
    updated_asset = test_db.query(Asset).filter(Asset.id == asset.id).first()
    assert updated_asset.description == "수정된 자산 설명"
    assert updated_asset.is_in_use is False
    
    # 자산 이력 생성 테스트
    asset_history = AssetHistory(
        asset_id=asset.id,
        changed_fields=json.dumps({
            "description": "수정된 자산 설명",
            "is_in_use": False
        }),
        description="자산 정보 업데이트"
    )
    
    test_db.add(asset_history)
    test_db.commit()
    test_db.refresh(asset_history)
    
    # 이력 조회
    history = test_db.query(AssetHistory).filter(AssetHistory.asset_id == asset.id).first()
    assert history is not None
    assert "description" in json.loads(history.changed_fields)
    
    # 자산 삭제 (이력도 cascade로 삭제되어야 함)
    test_db.delete(asset)
    test_db.commit()
    
    deleted_asset = test_db.query(Asset).filter(Asset.id == asset.id).first()
    assert deleted_asset is None
    
    # 이력도 삭제되었는지 확인
    deleted_history = test_db.query(AssetHistory).filter(AssetHistory.asset_id == asset.id).first()
    assert deleted_history is None
    
    # 정리
    test_db.delete(category)
    test_db.delete(location)
    test_db.delete(owner)
    test_db.delete(network_type)
    test_db.commit()


def test_user_auth(test_db):
    """사용자 인증 관련 테스트"""
    # 테스트 유저 생성
    hashed_password = get_password_hash("testpassword123")
    test_user = User(
        username="testauth",
        email="testauth@example.com",
        full_name="테스트 인증 사용자",
        hashed_password=hashed_password,
        is_active=True
    )
    
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)
    
    # 사용자 조회
    user = test_db.query(User).filter(User.username == "testauth").first()
    assert user is not None
    assert user.email == "testauth@example.com"
    
    # 패스워드 해시 검증
    from app.utils.auth import verify_password
    assert verify_password("testpassword123", user.hashed_password) is True
    assert verify_password("wrongpassword", user.hashed_password) is False
    
    # 사용자 상태 변경
    user.is_active = False
    test_db.commit()
    test_db.refresh(user)
    
    inactive_user = test_db.query(User).filter(User.username == "testauth").first()
    assert inactive_user.is_active is False
    
    # 사용자 삭제
    test_db.delete(user)
    test_db.commit()
    
    deleted_user = test_db.query(User).filter(User.username == "testauth").first()
    assert deleted_user is None 