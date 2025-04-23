# 도커 이미지 빌드 및 실행 방법

## 빌드 방법

다음 명령어를 사용하여 도커 이미지를 빌드합니다:

```bash
docker build -t asset-management .
```

## 실행 방법

다음 명령어를 사용하여 도커 컨테이너를 실행합니다:

```bash
docker run -d --name asset-app -p 8000:8000 -v $(pwd)/data:/app/data asset-management
```

이 명령은 다음과 같은 작업을 수행합니다:
- `-d`: 백그라운드에서 컨테이너를 실행합니다.
- `--name asset-app`: 컨테이너 이름을 'asset-app'으로 지정합니다.
- `-p 8000:8000`: 호스트의 8000 포트를 컨테이너의 8000 포트에 매핑합니다.
- `-v $(pwd)/data:/app/data`: 호스트의 ./data 디렉토리를 컨테이너의 /app/data 디렉토리에 마운트합니다. 이를 통해 SQLite 데이터베이스 파일이 컨테이너가 종료되더라도 유지됩니다.

## 접속 방법

웹 브라우저에서 다음 URL로 접속합니다:

```
http://localhost:8000
```

## 이미지 및 데모

프로젝트의 작동 방식을 보여주는 이미지와 데모 동영상을 아래에 포함시켰습니다.

![데모 이미지](./images/demo.png)

[데모 동영상 보기](https://example.com/demo)

## 추가 정보

이 프로젝트는 FastAPI와 SQLAlchemy를 사용하여 구축되었습니다. 자세한 사용법과 API 문서는 [여기](./docs/api.md)에서 확인할 수 있습니다.

프로젝트에 기여하고 싶으신 분들은 [CONTRIBUTING.md](./CONTRIBUTING.md)를 참조해주세요.
