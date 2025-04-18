"""
MAC 주소, IP 주소, 소유자, 네트워크망, 사용여부 필드를 Asset 모델에 추가하는 스크립트

이 스크립트는 다음을 수행합니다:
1. 데이터베이스에 새 필드(mac_address, ip_address, owner, network_type, is_in_use)를 추가합니다
2. owner 필드는 필수 필드로 설정하고, 기존 NULL 값이 있으면 '미지정'으로 설정합니다
3. network_type 필드는 필수 필드로 설정하고, 기존 NULL 값이 있으면 '없음'으로 설정합니다
4. is_in_use 필드는 BOOLEAN 타입으로 추가하며, 사용중(TRUE)/미사용(FALSE)/모름(NULL) 값을 가질 수 있습니다
"""

import os
import sqlite3
import sys

# 데이터베이스 파일 경로
DATABASE_PATH = "./asset_management.db"

def update_schema():
    """데이터베이스 스키마 업데이트"""
    # 데이터베이스 파일이 존재하는지 확인
    if not os.path.exists(DATABASE_PATH):
        print(f"데이터베이스 파일을 찾을 수 없습니다: {DATABASE_PATH}")
        sys.exit(1)

    print(f"데이터베이스 경로: {DATABASE_PATH}")
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # 테이블 스키마 확인
        cursor.execute("PRAGMA table_info(assets)")
        columns = {row[1] for row in cursor.fetchall()}

        # mac_address 컬럼 추가 (존재하지 않는 경우)
        if "mac_address" not in columns:
            cursor.execute("ALTER TABLE assets ADD COLUMN mac_address TEXT")
            print("'mac_address' 필드가 추가되었습니다.")
        else:
            print("'mac_address' 필드가 이미 존재합니다.")

        # ip_address 컬럼 추가 (존재하지 않는 경우)
        if "ip_address" not in columns:
            cursor.execute("ALTER TABLE assets ADD COLUMN ip_address TEXT")
            print("'ip_address' 필드가 추가되었습니다.")
        else:
            print("'ip_address' 필드가 이미 존재합니다.")

        # network_type 컬럼 추가 (존재하지 않는 경우)
        if "network_type" not in columns:
            cursor.execute("ALTER TABLE assets ADD COLUMN network_type TEXT NOT NULL DEFAULT '없음'")
            print("'network_type' 필드가 추가되었습니다 (필수 항목).")
        else:
            # 이미 존재하는 경우, NULL 값을 '없음'으로 업데이트
            cursor.execute("UPDATE assets SET network_type = '없음' WHERE network_type IS NULL")
            rows_updated = cursor.rowcount
            print(f"{rows_updated}개 레코드가 업데이트되었습니다 (network_type NULL → '없음')")
            print("'network_type' 필드가 이미 존재합니다.")

        # is_in_use 컬럼 추가 (존재하지 않는 경우)
        if "is_in_use" not in columns:
            cursor.execute("ALTER TABLE assets ADD COLUMN is_in_use BOOLEAN DEFAULT 1")
            print("'is_in_use' 필드가 추가되었습니다 (사용중: TRUE, 미사용: FALSE, 모름: NULL).")
        else:
            print("'is_in_use' 필드가 이미 존재합니다.")

        # owner 컬럼 추가 및 NULL 값 처리 (존재하지 않는 경우)
        if "owner" not in columns:
            cursor.execute("ALTER TABLE assets ADD COLUMN owner TEXT NOT NULL DEFAULT '미지정'")
            print("'owner' 필드가 추가되었습니다.")
        else:
            # 이미 존재하는 경우, NULL 값을 '미지정'으로 업데이트하고 NOT NULL 제약 조건 추가
            cursor.execute("UPDATE assets SET owner = '미지정' WHERE owner IS NULL")
            rows_updated = cursor.rowcount
            print(f"{rows_updated}개 레코드가 업데이트되었습니다 (owner NULL → '미지정')")
            
            # SQLite는 기존 컬럼에 NOT NULL 제약 조건을 직접 추가할 수 없으므로 아래 코드는 실행하지 않음
            # 이미 models.py에서 nullable=False로 설정되어 있으므로 새 레코드에는 적용됨
            print("'owner' 필드가 이미 존재합니다.")

        conn.commit()
        print("데이터베이스 스키마 업데이트가 성공적으로 완료되었습니다.")

    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_schema() 