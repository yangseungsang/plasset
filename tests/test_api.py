import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.models import Asset


def test_read_categories(client, test_db):
    """카테고리 목록 조회 테스트"""
    response = client.get("/api/categories/")
    assert response.status_code == 200
    
    categories = response.json()
    assert len(categories) >= 3
    
    # 테스트 데이터의 카테고리 확인
    category_names = [category["name"] for category in categories]
    assert "노트북" in category_names
    assert "서버" in category_names
    assert "네트워크" in category_names


def test_read_locations(client, test_db):
    """위치 목록 조회 테스트"""
    response = client.get("/api/locations/")
    assert response.status_code == 200
    
    locations = response.json()
    assert len(locations) >= 3
    
    # 테스트 데이터의 위치 확인
    location_names = [location["name"] for location in locations]
    assert "본사 1층" in location_names
    assert "본사 2층" in location_names
    assert "데이터센터" in location_names


def test_create_and_read_asset(authenticated_client, test_db):
    """자산 생성 및 조회 테스트"""
    # 1. 자산 생성
    asset_data = {
        "name": "테스트 노트북",
        "category": "노트북",
        "serial_number": "SN-TEST-1234",
        "management_number": "MN-TEST-1234",
        "acquisition_date": str(date.today()),
        "description": "테스트용 노트북입니다.",
        "location": "본사 1층",
        "owner": "IT팀",
        "network_type": "사내망",
        "is_in_use": True,
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "ip_address": "192.168.0.100"
    }
    
    response = authenticated_client.post("/api/assets/", json=asset_data)
    assert response.status_code == 200
    
    new_asset = response.json()
    assert new_asset["name"] == "테스트 노트북"
    assert new_asset["serial_number"] == "SN-TEST-1234"
    
    # 생성된 자산 ID 저장
    asset_id = new_asset["id"]
    
    # 2. 자산 개별 조회
    response = authenticated_client.get(f"/api/assets/{asset_id}")
    assert response.status_code == 200
    
    asset = response.json()
    assert asset["id"] == asset_id
    assert asset["name"] == "테스트 노트북"
    assert asset["category"] == "노트북"
    assert asset["serial_number"] == "SN-TEST-1234"
    
    # 3. 자산 목록 조회
    response = authenticated_client.get("/api/assets/")
    assert response.status_code == 200
    
    assets = response.json()
    assert len(assets) >= 1
    
    # 생성한 자산이 목록에 있는지 확인
    asset_found = False
    for a in assets:
        if a["id"] == asset_id:
            asset_found = True
            break
    
    assert asset_found


def test_update_asset(authenticated_client, test_db):
    """자산 수정 테스트"""
    # 1. 자산 생성
    asset_data = {
        "name": "수정 테스트용 노트북",
        "category": "노트북",
        "serial_number": "SN-UPDATE-TEST",
        "management_number": "MN-UPDATE-TEST",
        "acquisition_date": str(date.today()),
        "description": "수정 테스트용 노트북입니다.",
        "location": "본사 1층",
        "owner": "IT팀",
        "network_type": "사내망",
        "is_in_use": True
    }
    
    response = authenticated_client.post("/api/assets/", json=asset_data)
    assert response.status_code == 200
    asset_id = response.json()["id"]
    
    # 2. 자산 수정
    update_data = {
        "name": "수정된 노트북",
        "description": "자산 정보가 수정되었습니다.",
        "location": "본사 2층"
    }
    
    response = authenticated_client.put(f"/api/assets/{asset_id}", json=update_data)
    assert response.status_code == 200
    
    updated_asset = response.json()
    assert updated_asset["name"] == "수정된 노트북"
    assert updated_asset["description"] == "자산 정보가 수정되었습니다."
    assert updated_asset["location"] == "본사 2층"
    
    # 원래 정보는 유지되어야 함
    assert updated_asset["category"] == "노트북"
    assert updated_asset["serial_number"] == "SN-UPDATE-TEST"


def test_delete_asset(authenticated_client, test_db):
    """자산 삭제 테스트"""
    # 1. 자산 생성
    asset_data = {
        "name": "삭제 테스트용 노트북",
        "category": "노트북",
        "serial_number": "SN-DELETE-TEST",
        "management_number": "MN-DELETE-TEST",
        "acquisition_date": str(date.today()),
        "description": "삭제 테스트용 노트북입니다.",
        "location": "본사 1층",
        "owner": "IT팀",
        "network_type": "사내망",
        "is_in_use": True
    }
    
    response = authenticated_client.post("/api/assets/", json=asset_data)
    assert response.status_code == 200
    asset_id = response.json()["id"]
    
    # 2. 자산 삭제
    response = authenticated_client.delete(f"/api/assets/{asset_id}")
    assert response.status_code == 200
    
    # 3. 삭제된 자산 조회 시도 (404 예상)
    response = authenticated_client.get(f"/api/assets/{asset_id}")
    assert response.status_code == 404


def test_filter_assets(authenticated_client, test_db):
    """자산 필터링 테스트"""
    # 테스트용 자산 여러 개 생성
    asset_data1 = {
        "name": "필터 테스트 노트북 1",
        "category": "노트북",
        "serial_number": "SN-FILTER-1",
        "management_number": "MN-FILTER-1",
        "location": "본사 1층",
        "owner": "IT팀",
        "network_type": "사내망",
        "is_in_use": True
    }
    
    asset_data2 = {
        "name": "필터 테스트 서버 1",
        "category": "서버",
        "serial_number": "SN-FILTER-2",
        "management_number": "MN-FILTER-2",
        "location": "데이터센터",
        "owner": "IT팀",
        "network_type": "장비망",
        "is_in_use": True
    }
    
    asset_data3 = {
        "name": "필터 테스트 네트워크 장비",
        "category": "네트워크",
        "serial_number": "SN-FILTER-3",
        "management_number": "MN-FILTER-3",
        "location": "데이터센터",
        "owner": "IT팀",
        "network_type": "장비망",
        "is_in_use": False
    }
    
    authenticated_client.post("/api/assets/", json=asset_data1)
    authenticated_client.post("/api/assets/", json=asset_data2)
    authenticated_client.post("/api/assets/", json=asset_data3)
    
    # 카테고리 필터링 테스트
    response = authenticated_client.get("/api/assets/?category=서버")
    assert response.status_code == 200
    filtered_assets = response.json()
    
    # 적어도 하나의 "서버" 카테고리 자산이 있어야 함
    assert any(asset["category"] == "서버" for asset in filtered_assets)
    # "노트북" 카테고리는 없어야 함
    assert all(asset["category"] != "노트북" or "필터 테스트 노트북" not in asset["name"] for asset in filtered_assets)
    
    # 위치 필터링 테스트
    response = authenticated_client.get("/api/assets/?location=데이터센터")
    assert response.status_code == 200
    filtered_assets = response.json()
    
    # 모든 자산의 위치가 "데이터센터"여야 함
    assert all(asset["location"] == "데이터센터" for asset in filtered_assets)
    
    # 검색 필터링 테스트
    response = authenticated_client.get("/api/assets/?search=필터 테스트")
    assert response.status_code == 200
    filtered_assets = response.json()
    
    # 모든 "필터 테스트" 자산이 포함되어야 함
    assert len(filtered_assets) >= 3
    assert any("필터 테스트 노트북" in asset["name"] for asset in filtered_assets)
    assert any("필터 테스트 서버" in asset["name"] for asset in filtered_assets)
    assert any("필터 테스트 네트워크" in asset["name"] for asset in filtered_assets) 