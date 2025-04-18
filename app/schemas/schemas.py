from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LocationBase(BaseModel):
    name: str
    image_path: Optional[str] = None


class LocationCreate(LocationBase):
    pass


class Location(LocationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AssetBase(BaseModel):
    name: str
    category: str
    serial_number: str
    management_number: str
    acquisition_date: Optional[date] = None
    description: Optional[str] = None
    location: str
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None
    mac_address: Optional[str] = None
    ip_address: Optional[str] = None
    owner: str
    network_type: str
    is_in_use: Optional[bool] = None


# 자산 이력 스키마
class AssetHistoryBase(BaseModel):
    asset_id: int
    changed_fields: Dict[str, Any]
    description: Optional[str] = None


class AssetHistoryCreate(AssetHistoryBase):
    pass


class AssetHistory(AssetHistoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssetCreate(AssetBase):
    # acquisition_date는 이제 선택적 필드입니다
    class Config:
        json_schema_extra = {
            "example": {
                "name": "노트북",
                "category": "PC",
                "serial_number": "SN12345",
                "management_number": "MN12345",
                "acquisition_date": "2023-01-01",
                "description": "개발용 노트북",
                "location": "사무실",
                "x_coordinate": None,
                "y_coordinate": None,
                "mac_address": "00:1A:2B:3C:4D:5E",
                "ip_address": "192.168.1.100",
                "owner": "홍길동",
                "network_type": "사내망",
                "is_in_use": True  # True: 사용중, False: 미사용, None: 모름
            }
        }


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    serial_number: Optional[str] = None
    management_number: Optional[str] = None
    acquisition_date: Optional[date] = None
    description: Optional[str] = None
    location: Optional[str] = None
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None
    mac_address: Optional[str] = None
    ip_address: Optional[str] = None
    owner: Optional[str] = None
    network_type: Optional[str] = None
    is_in_use: Optional[bool] = None


class Asset(AssetBase):
    id: int
    created_at: datetime
    updated_at: datetime
    histories: List[AssetHistory] = []

    class Config:
        from_attributes = True


class NetworkTypeBase(BaseModel):
    name: str
    description: Optional[str] = None


class NetworkTypeCreate(NetworkTypeBase):
    pass


class NetworkType(NetworkTypeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OwnerBase(BaseModel):
    name: str
    department: Optional[str] = None
    contact: Optional[str] = None


class OwnerCreate(OwnerBase):
    pass


class Owner(OwnerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 