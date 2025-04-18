import uvicorn

if __name__ == "__main__":
    # 애플리케이션 실행
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 