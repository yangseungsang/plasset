from pydantic import BaseModel
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 애플리케이션 설정
    APP_NAME: str = "자산관리 시스템"
    DEBUG: bool = True
    APP_PORT: int = 8000
    
    # API 설정
    API_PREFIX: str = "/api"
    
    # 보안 설정
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24시간
    
    # 쿠키 설정
    COOKIE_SECURE: bool = False  # 개발 환경에서는 False, 운영 환경에서는 True
    
    # Nginx 설정
    NGINX_PORT: int = 80
    NGINX_PUBLIC_PORT: int = 80
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 