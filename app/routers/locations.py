from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from app.database.database import get_db
from app.models.models import Location, Asset
from app.schemas import Location as LocationSchema, LocationCreate
from fastapi.responses import FileResponse
from app.routers.auth import login_required

router = APIRouter(
    prefix="/api/locations",
    tags=["locations"],
    dependencies=[Depends(login_required)]
)


@router.get("/", response_model=List[LocationSchema])
def get_locations(db: Session = Depends(get_db)):
    locations = db.query(Location).all()
    return locations


@router.get("/name/{name}", response_model=LocationSchema)
def get_location_by_name(name: str, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.name == name).first()
    if not location:
        raise HTTPException(status_code=404, detail=f"위치 '{name}'을(를) 찾을 수 없습니다")
    return location


@router.get("/{id}", response_model=LocationSchema)
def get_location(id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == id).first()
    if not location:
        raise HTTPException(status_code=404, detail=f"위치 ID {id}을(를) 찾을 수 없습니다")
    return location


@router.delete("/{id}")
def delete_location(id: int, db: Session = Depends(get_db)):
    # 삭제할 보관 장소 조회
    location = db.query(Location).filter(Location.id == id).first()
    if not location:
        raise HTTPException(status_code=404, detail=f"위치 ID {id}을(를) 찾을 수 없습니다")
    
    # 해당 보관 장소 이름에 해당하는 자산이 있는지 확인
    location_name = getattr(location, 'name', '')
    assets_count = db.query(Asset).filter(Asset.location == location_name).count()
    if assets_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"이 보관 장소에 {assets_count}개의 자산이 있습니다. 자산을 먼저 다른 위치로 이동하세요."
        )
    
    # 이미지 파일이 있으면 삭제
    image_path = getattr(location, 'image_path', None)  # 안전하게 속성 접근
    if isinstance(image_path, str) and image_path:
        file_path = f"app{image_path}"
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"이미지 파일 삭제 중 오류 발생: {e}")
    
    # 데이터베이스에서 보관 장소 삭제
    db.delete(location)
    db.commit()
    
    location_name = getattr(location, 'name', 'Unknown')  # 안전하게 속성 접근
    return {"message": f"보관 장소 '{location_name}'이(가) 삭제되었습니다."} 