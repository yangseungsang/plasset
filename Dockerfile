# Python 3.10 이미지 사용
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 환경변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 볼륨 생성 - 데이터베이스 파일을 위한 볼륨
VOLUME /app/data

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출 (환경변수 사용)
EXPOSE $PORT

# 애플리케이션 실행 (환경변수 사용)
CMD cd /app && uvicorn app.main:app --host 0.0.0.0 --port $PORT 