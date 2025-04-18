"""
자산 변경 이력(AssetHistory) 테이블을 생성하는 스크립트

이 스크립트는 다음을 수행합니다:
1. 데이터베이스에 asset_histories 테이블을 생성합니다.
2. 테이블이 이미 존재하는 경우 스키마를 업데이트합니다.
"""

import os
import sqlite3
import sys
import json

# 데이터베이스 파일 경로
DATABASE_PATH = "./asset_management.db"

def create_asset_history_table():
    """자산 변경 이력 테이블 생성"""
    # 데이터베이스 파일이 존재하는지 확인
    if not os.path.exists(DATABASE_PATH):
        print(f"데이터베이스 파일을 찾을 수 없습니다: {DATABASE_PATH}")
        sys.exit(1)

    print(f"데이터베이스 경로: {DATABASE_PATH}")
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # 테이블 존재 여부 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='asset_histories'")
        if cursor.fetchone() is None:
            # 테이블이 없는 경우 생성
            cursor.execute("""
            CREATE TABLE asset_histories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER NOT NULL,
                changed_fields TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE
            )
            """)
            print("'asset_histories' 테이블이 생성되었습니다.")
        else:
            print("'asset_histories' 테이블이 이미 존재합니다.")

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
    create_asset_history_table() 