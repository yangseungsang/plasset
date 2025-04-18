from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, text

from app.database.database import get_db
from app.models import models
from app import schemas
from app.schemas import Asset, AssetCreate, AssetUpdate, Category, CategoryCreate, Location, LocationCreate, Owner, OwnerCreate, NetworkType, NetworkTypeCreate
import pandas as pd
from io import BytesIO
import os
import json
from datetime import datetime
from app.routers.auth import login_required

# 로그인 필요한 라우터 정의
router = APIRouter(dependencies=[Depends(login_required)])


@router.post("/categories/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = models.Category(
        name=category.name,
        description=category.description
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/categories/", response_model=List[schemas.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(models.Category).offset(skip).limit(limit).all()
    return categories


@router.post("/locations/", response_model=schemas.Location)
def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):
    db_location = models.Location(name=location.name, image_path=location.image_path)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


@router.get("/locations/", response_model=List[schemas.Location])
def read_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    locations = db.query(models.Location).offset(skip).limit(limit).all()
    return locations


@router.post("/upload_location_image/{location_id}")
async def upload_location_image(
    location_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    location = db.query(models.Location).filter(models.Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # 디버깅: 업로드 시작 로그
    print(f"이미지 업로드 시작 - 위치 ID: {location_id}, 파일명: {file.filename}")

    # 파일 확장자 검증
    filename = file.filename or ""
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="File must be an image (jpg, jpeg, png)")

    # 파일 저장 경로에 타임스탬프 추가하여 캐시 방지
    timestamp = int(datetime.now().timestamp())
    file_path = f"app/static/images/location_{location_id}_{timestamp}{file_extension}"
    static_path = f"/static/images/location_{location_id}_{timestamp}{file_extension}"

    # 디버깅: 파일 저장 경로 로그
    print(f"이미지 저장 경로: {file_path}")
    print(f"이미지 접근 경로: {static_path}")

    try:
        # 파일 저장
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # 파일 크기 확인
        file_size = os.path.getsize(file_path)
        print(f"저장된 파일 크기: {file_size} 바이트")

        # SQL UPDATE 문을 사용하여 이미지 경로 업데이트
        sql = text("UPDATE locations SET image_path = :image_path WHERE id = :id")
        db.execute(sql, {"image_path": static_path, "id": location_id})
        db.commit()
        
        # 업데이트 결과 확인
        updated_location = db.query(models.Location).filter(models.Location.id == location_id).first()
        if updated_location:
            print(f"업데이트된 위치 정보: ID={updated_location.id}, 이름={updated_location.name}, 이미지={updated_location.image_path}")
        else:
            print(f"경고: 위치 ID {location_id}에 대한 업데이트 확인 실패")
        
        return {
            "filename": file.filename, 
            "path": static_path,
            "timestamp": timestamp
        }
    except Exception as e:
        db.rollback()
        print(f"이미지 업로드 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"이미지 업로드 오류: {str(e)}")


@router.post("/assets/", response_model=schemas.Asset)
def create_asset(asset: schemas.AssetCreate, db: Session = Depends(get_db)):
    try:
        print(f"수신된 자산 데이터: {asset.model_dump()}")
        
        # 시리얼 번호 중복 검사
        db_asset = db.query(models.Asset).filter(models.Asset.serial_number == asset.serial_number).first()
        if db_asset:
            raise HTTPException(status_code=400, detail="Serial number already registered")

        # 카테고리 유효성 검사
        if not asset.category:
            raise HTTPException(status_code=400, detail="Category is required")
        
        # 카테고리 존재 여부 확인
        category = db.query(models.Category).filter(models.Category.name == asset.category).first()
        if not category:
            raise HTTPException(status_code=400, detail=f"Category '{asset.category}' does not exist")
        
        # 위치 유효성 검사
        if not asset.location:
            raise HTTPException(status_code=400, detail="Location is required")
        
        # 위치 존재 여부 확인
        location = db.query(models.Location).filter(models.Location.name == asset.location).first()
        if not location:
            raise HTTPException(status_code=400, detail=f"Location '{asset.location}' does not exist")

        # 데이터 변환 시도
        asset_data = asset.model_dump()
        print(f"모델 변환 후 데이터: {asset_data}")
        
        # 객체 생성
        db_asset = models.Asset(**asset_data)
        
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
        return db_asset
    except Exception as e:
        # 롤백
        db.rollback()
        print(f"자산 생성 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/assets/", response_model=List[schemas.Asset])
def read_assets(
    skip: int = 0, 
    limit: int = 100, 
    category: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Asset)
    
    # 카테고리 필터링
    if category:
        query = query.filter(models.Asset.category == category)
    
    # 위치 필터링
    if location:
        query = query.filter(models.Asset.location == location)
    
    # 검색
    if search:
        query = query.filter(
            or_(
                models.Asset.name.ilike(f"%{search}%"),
                models.Asset.serial_number.ilike(f"%{search}%"),
                models.Asset.management_number.ilike(f"%{search}%"),
                models.Asset.description.ilike(f"%{search}%")
            )
        )
    
    assets = query.offset(skip).limit(limit).all()
    return assets


@router.get("/assets/{asset_id}", response_model=schemas.Asset)
def read_asset(asset_id: int, db: Session = Depends(get_db)):
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if db_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return db_asset


@router.put("/assets/{asset_id}", response_model=schemas.Asset)
def update_asset(asset_id: int, asset: schemas.AssetUpdate, db: Session = Depends(get_db)):
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if db_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # 시리얼 번호가 변경된 경우 중복 검사
    if asset.serial_number and asset.serial_number != db_asset.serial_number:
        serial_exists = db.query(models.Asset).filter(
            models.Asset.serial_number == asset.serial_number,
            models.Asset.id != asset_id
        ).first()
        if serial_exists:
            raise HTTPException(status_code=400, detail="Serial number already registered")
    
    # 변경 이력을 기록하기 위해 기존 정보 저장
    old_data = {
        "name": db_asset.name,
        "category": db_asset.category,
        "serial_number": db_asset.serial_number,
        "management_number": db_asset.management_number,
        "acquisition_date": db_asset.acquisition_date.isoformat() if db_asset.acquisition_date is not None else None,
        "description": db_asset.description,
        "location": db_asset.location,
        "x_coordinate": db_asset.x_coordinate,
        "y_coordinate": db_asset.y_coordinate,
        "mac_address": db_asset.mac_address,
        "ip_address": db_asset.ip_address,
        "owner": db_asset.owner,
        "network_type": db_asset.network_type,
        "is_in_use": db_asset.is_in_use
    }
    
    # 업데이트할 데이터만 변경
    update_data = asset.model_dump(exclude_unset=True)
    
    # 변경된 필드 기록
    changed_fields = {}
    for key, value in update_data.items():
        # acquisition_date 필드가 date 객체인 경우 비교를 위해 문자열로 변환
        if key == "acquisition_date" and value is not None:
            value_str = value.isoformat()
            if old_data[key] != value_str:
                changed_fields[key] = {
                    "old": old_data[key],
                    "new": value_str
                }
        elif old_data[key] != value:
            changed_fields[key] = {
                "old": old_data[key],
                "new": value
            }
    
    # 자산 정보 업데이트
    for key, value in update_data.items():
        setattr(db_asset, key, value)
    
    # 변경 이력이 있는 경우에만 기록
    if changed_fields:
        # 변경 이력 생성
        asset_history = models.AssetHistory(
            asset_id=asset_id,
            changed_fields=changed_fields,
            description=f"자산 정보 수정"
        )
        db.add(asset_history)
    
    db.commit()
    db.refresh(db_asset)
    return db_asset


@router.delete("/assets/{asset_id}")
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if db_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db.delete(db_asset)
    db.commit()
    return {"message": "Asset deleted successfully"}


@router.post("/assets/update_coordinates/{asset_id}")
def update_asset_coordinates(
    asset_id: int, 
    x_coordinate: str = Form(''), 
    y_coordinate: str = Form(''), 
    db: Session = Depends(get_db)
):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # 빈 문자열을 None으로 변환
    x_coordinate_value = None if x_coordinate == '' else float(x_coordinate)
    y_coordinate_value = None if y_coordinate == '' else float(y_coordinate)
    
    # 자산 정보 업데이트 (세션 갱신)
    updated_asset = models.Asset(
        id=asset_id,
        name=asset.name,
        category=asset.category,
        serial_number=asset.serial_number,
        management_number=asset.management_number,
        acquisition_date=asset.acquisition_date,
        description=asset.description,
        location=asset.location,
        x_coordinate=x_coordinate_value,
        y_coordinate=y_coordinate_value,
        created_at=asset.created_at,
        updated_at=asset.updated_at
    )
    db.merge(updated_asset)
    db.commit()
    
    return {"message": "Asset coordinates updated successfully"}


@router.get("/export/assets/")
def export_assets(
    category: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
    network_type: Optional[str] = None,
    is_in_use: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Asset)
    
    # 필터링 적용
    if category:
        categories = category.split(',')
        if categories:
            query = query.filter(models.Asset.category.in_(categories))
    
    if location:
        locations = location.split(',')
        if locations:
            query = query.filter(models.Asset.location.in_(locations))
    
    if network_type:
        network_types = network_type.split(',')
        if network_types:
            query = query.filter(models.Asset.network_type.in_(network_types))
    
    if is_in_use:
        usage_filters = is_in_use.split(',')
        processed_filters = []
        
        for filter_value in usage_filters:
            if filter_value == 'true':
                processed_filters.append(True)
            elif filter_value == 'false':
                processed_filters.append(False)
            elif filter_value == 'null':
                query = query.filter(or_(models.Asset.is_in_use.in_(processed_filters), models.Asset.is_in_use.is_(None)))
                break
        else:
            if processed_filters:
                query = query.filter(models.Asset.is_in_use.in_(processed_filters))
    
    if search:
        query = query.filter(
            or_(
                models.Asset.name.ilike(f"%{search}%"),
                models.Asset.serial_number.ilike(f"%{search}%"),
                models.Asset.management_number.ilike(f"%{search}%"),
                models.Asset.description.ilike(f"%{search}%"),
                models.Asset.owner.ilike(f"%{search}%")
            )
        )
    
    assets = query.all()
    
    # 자산 데이터프레임 생성
    asset_data = []
    for asset in assets:
        is_in_use_text = "모름"
        if asset.is_in_use is True:
            is_in_use_text = "사용중"
        elif asset.is_in_use is False:
            is_in_use_text = "미사용"
            
        asset_data.append({
            "자산명": asset.name,
            "카테고리": asset.category,
            "시리얼 넘버": asset.serial_number,
            "관리 넘버": asset.management_number,
            "도입일": asset.acquisition_date,
            "MAC 주소": asset.mac_address,
            "IP 주소": asset.ip_address,
            "소유자": asset.owner,
            "네트워크망": asset.network_type,
            "사용여부": is_in_use_text,
            "보관 장소": asset.location,
            "설명": asset.description
        })
    
    assets_df = pd.DataFrame(asset_data)
    
    # 보관 장소 데이터 및 이미지 준비
    locations_data = db.query(models.Location).all()
    location_images = {}
    
    for loc in locations_data:
        # 이미지 경로가 있는 경우 저장
        if loc.image_path is not None:
            # 경로에서 상대 경로 추출 (예: /static/images/location_1.jpg -> app/static/images/location_1.jpg)
            full_path = f"app{loc.image_path}"
            if os.path.exists(full_path):
                location_images[loc.id] = full_path
    
    # 엑셀 파일 생성
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        # 자산 목록 시트만 생성
        assets_df.to_excel(writer, sheet_name="자산 목록", index=False)
        
        # 보관 장소 이미지 시트
        if location_images:
            # 이미지 시트 생성
            worksheet = writer.book.add_worksheet("보관 장소 이미지")
            
            # 시트 설정 - 셀 크기 조정
            worksheet.set_column('A:A', 15)
            worksheet.set_column('B:B', 30)
            worksheet.set_column('C:C', 50)
            
            # 헤더 작성
            worksheet.write(0, 0, "ID")
            worksheet.write(0, 1, "장소명")
            worksheet.write(0, 2, "이미지")
            
            # 각 위치에 대한 이미지 추가
            row = 1
            for loc in locations_data:
                if loc.id in location_images:
                    # ID와 장소명 추가
                    worksheet.write(row, 0, loc.id)
                    worksheet.write(row, 1, loc.name)
                    
                    try:
                        # 이미지 추가 (적절한 크기로 조정)
                        worksheet.insert_image(row, 2, location_images[loc.id], {
                            'x_scale': 0.5, 
                            'y_scale': 0.5,
                            'x_offset': 5,
                            'y_offset': 5,
                            'positioning': 1
                        })
                        # 다음 이미지를 위한 행 높이 설정 (이미지 크기에 맞게)
                        worksheet.set_row(row, 180)
                    except Exception as e:
                        worksheet.write(row, 2, f"이미지 추가 실패: {str(e)}")
                    
                    row += 1
    
    output.seek(0)
    
    # 한국 시간으로 현재 날짜를 파일명에 포함
    import pytz
    
    kst = pytz.timezone('Asia/Seoul')
    today = datetime.now(kst).strftime("%Y%m%d_%H%M%S")
    
    headers = {
        "Content-Disposition": f'attachment; filename="asset_list_{today}.xlsx"',
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    
    return StreamingResponse(output, headers=headers)


@router.get("/locations/{location_id}", response_model=schemas.Location)
def read_location(location_id: int, db: Session = Depends(get_db)):
    location = db.query(models.Location).filter(models.Location.id == location_id).first()
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # 디버깅을 위한 로그 추가
    print(f"위치 정보 반환: ID={location.id}, 이름={location.name}, 이미지 경로={location.image_path}")
    
    return location


@router.get("/locations/name/{location_name}", response_model=schemas.Location)
def read_location_by_name(location_name: str, db: Session = Depends(get_db)):
    location = db.query(models.Location).filter(models.Location.name == location_name).first()
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    
    return location


@router.put("/categories/{category_id}", response_model=schemas.Category)
def update_category(category_id: int, category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    
    # 이름 중복 검사
    existing_category = db.query(models.Category).filter(
        models.Category.name == category.name,
        models.Category.id != category_id
    ).first()
    if existing_category:
        raise HTTPException(status_code=400, detail=f"'{category.name}' 카테고리가 이미 존재합니다")
    
    db_category.name = category.name
    db_category.description = category.description
    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    
    # 해당 카테고리를 사용 중인 자산이 있는지 확인
    assets_with_category = db.query(models.Asset).filter(models.Asset.category == db_category.name).count()
    if assets_with_category > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"이 카테고리를 사용 중인 자산이 {assets_with_category}개 있어 삭제할 수 없습니다"
        )
    
    db.delete(db_category)
    db.commit()
    return {"message": "카테고리가 성공적으로 삭제되었습니다"}


@router.post("/owners/", response_model=schemas.Owner)
def create_owner(owner: schemas.OwnerCreate, db: Session = Depends(get_db)):
    db_owner = models.Owner(
        name=owner.name,
        department=owner.department,
        contact=owner.contact
    )
    db.add(db_owner)
    db.commit()
    db.refresh(db_owner)
    return db_owner


@router.get("/owners/", response_model=List[schemas.Owner])
def read_owners(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    owners = db.query(models.Owner).offset(skip).limit(limit).all()
    return owners


@router.get("/owners/{owner_id}", response_model=schemas.Owner)
def read_owner(owner_id: int, db: Session = Depends(get_db)):
    db_owner = db.query(models.Owner).filter(models.Owner.id == owner_id).first()
    if db_owner is None:
        raise HTTPException(status_code=404, detail="Owner not found")
    return db_owner


@router.put("/owners/{owner_id}", response_model=schemas.Owner)
def update_owner(owner_id: int, owner: schemas.OwnerCreate, db: Session = Depends(get_db)):
    db_owner = db.query(models.Owner).filter(models.Owner.id == owner_id).first()
    if db_owner is None:
        raise HTTPException(status_code=404, detail="Owner not found")
    
    for key, value in owner.model_dump().items():
        setattr(db_owner, key, value)
    
    db.commit()
    db.refresh(db_owner)
    return db_owner


@router.delete("/owners/{owner_id}")
def delete_owner(owner_id: int, db: Session = Depends(get_db)):
    db_owner = db.query(models.Owner).filter(models.Owner.id == owner_id).first()
    if db_owner is None:
        raise HTTPException(status_code=404, detail="Owner not found")
    
    # 이 소유자를 참조하는 자산이 있는지 확인
    assets_count = db.query(models.Asset).filter(models.Asset.owner == db_owner.name).count()
    if assets_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete owner: {assets_count} assets are assigned to this owner"
        )
    
    db.delete(db_owner)
    db.commit()
    return {"success": True, "message": "Owner deleted successfully"}


@router.post("/network_types/", response_model=schemas.NetworkType)
def create_network_type(network_type: schemas.NetworkTypeCreate, db: Session = Depends(get_db)):
    db_network_type = models.NetworkType(
        name=network_type.name,
        description=network_type.description
    )
    db.add(db_network_type)
    db.commit()
    db.refresh(db_network_type)
    return db_network_type


@router.get("/network_types/", response_model=List[schemas.NetworkType])
def read_network_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    network_types = db.query(models.NetworkType).offset(skip).limit(limit).all()
    return network_types


@router.get("/network_types/{network_type_id}", response_model=schemas.NetworkType)
def read_network_type(network_type_id: int, db: Session = Depends(get_db)):
    db_network_type = db.query(models.NetworkType).filter(models.NetworkType.id == network_type_id).first()
    if db_network_type is None:
        raise HTTPException(status_code=404, detail="Network type not found")
    return db_network_type


@router.put("/network_types/{network_type_id}", response_model=schemas.NetworkType, response_model_exclude_unset=True)
def update_network_type(network_type_id: int, network_type: schemas.NetworkTypeCreate, db: Session = Depends(get_db), update_assets: bool = Query(False, description="연관된 자산도 함께 업데이트할지 여부")):
    # 트랜잭션 시작
    try:
        db_network_type = db.query(models.NetworkType).filter(models.NetworkType.id == network_type_id).first()
        if db_network_type is None:
            raise HTTPException(status_code=404, detail="네트워크 유형을 찾을 수 없습니다")
        
        # 이름이 변경되는 경우, 이 네트워크 유형을 사용하는 자산 수 확인
        assets_count = 0
        old_name = db_network_type.name
        new_name = network_type.name
        
        if str(old_name) != str(new_name):  # 문자열로 변환하여 비교
            assets_count = db.query(models.Asset).filter(models.Asset.network_type == str(old_name)).count()
            
            # 사용자가 연관 자산 업데이트를 요청했는지 확인
            if assets_count > 0 and not update_assets:
                # 사용자가 업데이트를 명시적으로 요청하지 않았을 때는
                # 직접 JSONResponse를 사용하여 스키마 유효성 검사를 우회합니다
                return JSONResponse(content={
                    "success": False, 
                    "requires_confirmation": True,
                    "assets_count": assets_count,
                    "message": f"'{old_name}' 네트워크 유형을 사용 중인 자산이 {assets_count}개 있습니다. 이름을 변경하면 모든 자산의 네트워크 유형도 '{new_name}'으로 변경됩니다. 계속하시겠습니까?"
                })
        
        # 네트워크 유형 정보 업데이트 - model_dump()는 네이티브 Python 값을 반환함
        db_network_type.name = str(network_type.name)
        if network_type.description is not None:
            db_network_type.description = str(network_type.description)
        
        # 이름이 변경되고 사용자가 연관 자산 업데이트를 승인한 경우
        if str(old_name) != str(new_name) and update_assets and assets_count > 0:
            # 이 네트워크 유형을 사용하는 모든 자산 업데이트
            assets_to_update = db.query(models.Asset).filter(models.Asset.network_type == str(old_name)).all()
            for asset in assets_to_update:
                # 문자열을 직접 할당
                db.execute(
                    text("UPDATE assets SET network_type = :new_name WHERE id = :asset_id"),
                    {"new_name": str(new_name), "asset_id": asset.id}
                )
        
        # 변경사항 저장
        db.commit()
        db.refresh(db_network_type)
        
        # NetworkType 스키마에 맞는 데이터만 반환
        return db_network_type
        
    except Exception as e:
        # 오류 발생 시 트랜잭션 롤백
        db.rollback()
        raise HTTPException(status_code=500, detail=f"네트워크 유형 업데이트 중 오류 발생: {str(e)}")


@router.delete("/network_types/{network_type_id}")
def delete_network_type(network_type_id: int, db: Session = Depends(get_db)):
    db_network_type = db.query(models.NetworkType).filter(models.NetworkType.id == network_type_id).first()
    if db_network_type is None:
        raise HTTPException(status_code=404, detail="네트워크 유형을 찾을 수 없습니다")
    
    # 이 네트워크를 참조하는 자산이 있는지 확인
    assets_count = db.query(models.Asset).filter(models.Asset.network_type == db_network_type.name).count()
    if assets_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"'{db_network_type.name}' 네트워크 유형을 사용 중인 자산이 {assets_count}개 있어 삭제할 수 없습니다. 먼저 해당 자산의 네트워크 유형을 변경해주세요."
        )
    
    db.delete(db_network_type)
    db.commit()
    return {"success": True, "message": f"'{db_network_type.name}' 네트워크 유형이 성공적으로 삭제되었습니다"} 