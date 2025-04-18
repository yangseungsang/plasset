"""
데이터베이스 초기화 스크립트
샘플 카테고리와 위치를 생성합니다.
"""
from datetime import date
from sqlalchemy.orm import Session

from app.database.database import Base, engine, SessionLocal, get_db
from app.models import models
from app.utils.auth import get_password_hash

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

def init_db():
    db = next(get_db())
    # 초기 데이터 넣기
    try:
        # 카테고리 추가
        categories = ["PC", "서버", "네트워크 장비", "모니터", "주변기기", "기타"]
        for category_name in categories:
            category = db.query(models.Category).filter(models.Category.name == category_name).first()
            if not category:
                db_category = models.Category(name=category_name)
                db.add(db_category)
                db.commit()
                db.refresh(db_category)
                print(f"카테고리 '{category_name}' 생성됨")
            else:
                print(f"카테고리 '{category_name}' 이미 존재함")
        
        # 위치 추가
        locations = ["본사", "연구소", "1층 서버실", "2층 사무실", "3층 회의실", "창고"]
        for location_name in locations:
            location = db.query(models.Location).filter(models.Location.name == location_name).first()
            if not location:
                db_location = models.Location(name=location_name)
                db.add(db_location)
                db.commit()
                db.refresh(db_location)
                print(f"위치 '{location_name}' 생성됨")
            else:
                print(f"위치 '{location_name}' 이미 존재함")
        
        # 네트워크망 추가
        network_types = ["사내망", "장비망", "혼합", "없음"]
        for network_name in network_types:
            network = db.query(models.NetworkType).filter(models.NetworkType.name == network_name).first()
            if not network:
                db_network = models.NetworkType(name=network_name)
                db.add(db_network)
                db.commit()
                db.refresh(db_network)
                print(f"네트워크망 '{network_name}' 생성됨")
            else:
                print(f"네트워크망 '{network_name}' 이미 존재함")
        
        # 기본 소유자 추가
        owners = ["홍길동", "김철수", "이영희", "박문수"]
        for owner_name in owners:
            owner = db.query(models.Owner).filter(models.Owner.name == owner_name).first()
            if not owner:
                db_owner = models.Owner(name=owner_name)
                db.add(db_owner)
                db.commit()
                db.refresh(db_owner)
                print(f"소유자 '{owner_name}' 생성됨")
            else:
                print(f"소유자 '{owner_name}' 이미 존재함")
                
        # 기본 관리자 계정 추가
        admin_username = "admin"
        admin_user = db.query(models.User).filter(models.User.username == admin_username).first()
        if not admin_user:
            # 초기 암호는 "admin"으로 설정
            hashed_password = get_password_hash("admin")
            db_admin = models.User(
                username=admin_username,
                hashed_password=hashed_password,
                full_name="시스템 관리자",
                is_active=True
            )
            db.add(db_admin)
            db.commit()
            db.refresh(db_admin)
            print(f"관리자 계정 '{admin_username}' 생성됨 (비밀번호: admin)")
        else:
            print(f"관리자 계정 '{admin_username}' 이미 존재함")
                
        print("초기 데이터 생성 완료")
    except Exception as e:
        print(f"초기 데이터 생성 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    print("데이터베이스 초기화를 시작합니다...")
    init_db()
    print("데이터베이스 초기화가 완료되었습니다.") 