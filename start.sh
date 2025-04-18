#!/bin/bash

# 환경변수 파일 로드
if [ -f .env ]; then
  export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
fi

# Docker Compose 실행
docker-compose up -d

echo "자산관리 애플리케이션이 시작되었습니다."
echo "애플리케이션 URL: http://localhost:${NGINX_PUBLIC_PORT:-80}" 