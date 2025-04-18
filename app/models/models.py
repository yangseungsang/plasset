from sqlalchemy import Column, Integer, String, Date, Text, Float, func, Boolean, ForeignKey, JSON
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 자산명
    category = Column(String, nullable=False)  # 카테고리
    serial_number = Column(String, unique=True, nullable=False)  # 시리얼 넘버
    management_number = Column(String, nullable=False)  # 관리 넘버
    acquisition_date = Column(Date, nullable=True)  # 자산 도입일 (필수 아님)
    description = Column(Text, nullable=True)  # 설명
    location = Column(String, nullable=False)  # 장비 보관 장소
    x_coordinate = Column(Float, nullable=True)  # 보관 장소 내 X 좌표
    y_coordinate = Column(Float, nullable=True)  # 보관 장소 내 Y 좌표
    mac_address = Column(String, nullable=True)  # MAC 주소
    ip_address = Column(String, nullable=True)  # IP 주소
    owner = Column(String, nullable=False)  # 소유자 (필수 항목으로 변경)
    network_type = Column(String, nullable=False)  # 네트워크망 유형 (사내망, 장비망, 없음)
    is_in_use = Column(Boolean, nullable=True, default=True)  # 사용여부 (사용중, 미사용, 모름)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 변경 이력 관계 설정
    histories = relationship("AssetHistory", back_populates="asset", cascade="all, delete-orphan")


class AssetHistory(Base):
    __tablename__ = "asset_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    changed_fields = Column(JSON, nullable=False)  # 변경된 필드와 값을 JSON으로 저장
    description = Column(Text, nullable=True)  # 변경 내용 설명
    created_at = Column(DateTime, default=func.now())
    
    # 관계 설정
    asset = relationship("Asset", back_populates="histories")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # 카테고리명
    description = Column(String, nullable=True)  # 카테고리 설명
    created_at = Column(DateTime, default=func.now())


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # 위치명
    image_path = Column(String, nullable=True)  # 위치 이미지 경로
    created_at = Column(DateTime, default=func.now())


class NetworkType(Base):
    __tablename__ = "network_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # 네트워크망 이름
    description = Column(Text, nullable=True)  # 설명
    created_at = Column(DateTime, default=func.now())


class Owner(Base):
    __tablename__ = "owners"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # 소유자명
    department = Column(String, nullable=True)  # 부서
    contact = Column(String, nullable=True)  # 연락처
    created_at = Column(DateTime, default=func.now())


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)  # 사용자 아이디
    email = Column(String, unique=True, nullable=True)  # 이메일
    full_name = Column(String, nullable=True)  # 이름
    hashed_password = Column(String, nullable=False)  # 해시된 비밀번호
    is_active = Column(Boolean, default=True)  # 활성 상태
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())   