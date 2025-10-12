# Docker 빌드 오류 해결 가이드

Docker 빌드 시 발생하는 일반적인 오류와 해결 방법을 안내합니다.

## 🔥 일반적인 오류

### 오류 1: apt-get exit code 100

**증상:**
```
ERROR: failed to solve: process "/bin/sh -c apt-get update ..." 
did not complete successfully: exit code: 100
```

**원인:**
- APT 저장소 미러 서버 접속 실패
- 네트워크 문제
- 저장소 캐시 손상

**해결 방법:**

#### 방법 1: Ubuntu 기반 Dockerfile 사용 (권장)

```bash
# docker-compose.prod.yml 수정
# dockerfile: Dockerfile.prod → Dockerfile.ubuntu

# 또는 수동으로
docker build -f Dockerfile.ubuntu -t naver-monitor-backend .
```

#### 방법 2: 간단한 배포 사용

```bash
# SQLite 기반 간단한 배포
./deploy-simple.sh
```

#### 방법 3: 미러 서버 변경

`Dockerfile.prod` 파일 수정:
```dockerfile
# 한국 미러 사용
RUN sed -i 's|http://deb.debian.org|http://ftp.kr.debian.org|g' /etc/apt/sources.list && \
    apt-get update
```

#### 방법 4: 프록시 설정 (회사 환경)

```bash
# Docker 빌드 시 프록시 설정
docker build --build-arg HTTP_PROXY=http://proxy.company.com:8080 \
             --build-arg HTTPS_PROXY=http://proxy.company.com:8080 \
             -f Dockerfile.ubuntu .
```

---

### 오류 2: Playwright 설치 실패

**증상:**
```
ERROR: playwright install chromium failed
```

**해결:**

#### 방법 1: 시스템 의존성 자동 설치

```dockerfile
# Dockerfile에 추가
RUN playwright install --with-deps chromium
```

#### 방법 2: 수동 의존성 설치

```dockerfile
RUN apt-get update && \
    apt-get install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libpango-1.0-0 libcairo2 libasound2 && \
    playwright install chromium
```

#### 방법 3: Playwright 없이 배포 (크롤링 비활성화)

```bash
# requirements.txt에서 playwright 제거
# 크롤링 기능은 비활성화됨
```

---

### 오류 3: 네트워크 타임아웃

**증상:**
```
Could not connect to archive.ubuntu.com
```

**해결:**

```bash
# DNS 설정
docker build --network=host -f Dockerfile.ubuntu .

# 또는 Docker daemon.json 수정
sudo nano /etc/docker/daemon.json

# 추가:
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}

# Docker 재시작
sudo systemctl restart docker
```

---

### 오류 4: 디스크 공간 부족

**증상:**
```
no space left on device
```

**해결:**

```bash
# 사용하지 않는 이미지 삭제
docker system prune -a

# 빌드 캐시 삭제
docker builder prune

# 디스크 사용량 확인
docker system df

# 볼륨 정리
docker volume prune
```

---

## 🛠️ 빌드 옵션

### 옵션 1: Ubuntu 기반 (가장 안정적)

```bash
# Dockerfile.ubuntu 사용
docker build -f Dockerfile.ubuntu -t naver-monitor:latest .
docker run -d -p 8001:8000 naver-monitor:latest
```

**장점:**
- ✅ 가장 안정적
- ✅ 풍부한 패키지
- ✅ 문서화 잘됨

**단점:**
- ❌ 이미지 크기 큼 (~1.5GB)
- ❌ 빌드 시간 김

### 옵션 2: Python Slim (가벼움)

```bash
# Dockerfile.simple 사용
docker build -f Dockerfile.simple -t naver-monitor:simple .
```

**장점:**
- ✅ 이미지 작음 (~800MB)
- ✅ 빌드 빠름

**단점:**
- ❌ 일부 패키지 설치 어려울 수 있음

### 옵션 3: 로컬 빌드 없이 배포

```bash
# Docker Hub에서 Python 이미지 직접 사용
# Dockerfile 없이 docker-compose만으로 실행

# docker-compose.yml
services:
  backend:
    image: python:3.9
    command: sh -c "pip install -r requirements.txt && uvicorn server-debug:app --host 0.0.0.0"
    volumes:
      - .:/app
    working_dir: /app
```

---

## 🚀 권장 배포 순서

### 1단계: 간단한 배포로 테스트

```bash
./deploy-simple.sh
```

### 2단계: 문제 없으면 프로덕션 배포

```bash
./deploy.sh
```

### 3단계: 오류 발생 시

```bash
# Ubuntu 기반으로 재시도
docker build -f Dockerfile.ubuntu -t naver-monitor:latest .
docker run -d -p 8001:8000 -p 3000:3000 naver-monitor:latest
```

---

## 💡 디버깅 팁

### 빌드 과정 확인

```bash
# 단계별 확인
docker build -f Dockerfile.ubuntu --progress=plain .

# 특정 단계까지만 빌드
docker build -f Dockerfile.ubuntu --target <stage> .
```

### 중간 컨테이너 확인

```bash
# 실패한 단계의 이미지 ID 확인
docker images

# 컨테이너 실행하여 수동 확인
docker run -it <IMAGE_ID> /bin/bash

# 수동으로 apt-get 실행
apt-get update
apt-get install -y curl
```

### 네트워크 테스트

```bash
# 빌드 중 네트워크 테스트
docker run -it python:3.9-slim /bin/bash
# 내부에서:
apt-get update
ping -c 3 deb.debian.org
```

---

## 🔧 대체 방법

### Docker 없이 배포

```bash
# 1. 직접 설치
sudo apt-get install python3.9 python3-pip
pip install -r requirements.txt
playwright install --with-deps chromium

# 2. 서비스 실행
python3 server-debug.py &
cd frontend && npm run build && npx serve -s dist &
```

### systemd 서비스 등록

```bash
# /etc/systemd/system/naver-monitor.service
[Unit]
Description=Naver Monitor API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/naver-monitor
ExecStart=/path/to/venv/bin/python server-debug.py
Restart=always

[Install]
WantedBy=multi-user.target

# 활성화
sudo systemctl enable naver-monitor
sudo systemctl start naver-monitor
```

---

## 📋 체크리스트

배포 전 확인사항:

- [ ] Docker 설치 확인 (`docker --version`)
- [ ] Docker Compose 설치 확인 (`docker-compose --version`)
- [ ] 인터넷 연결 확인 (`ping -c 3 google.com`)
- [ ] 디스크 공간 확인 (`df -h`)
- [ ] 포트 사용 확인 (`lsof -i:8001 -i:3000`)
- [ ] 환경 변수 설정 (`.env` 파일)
- [ ] 데이터베이스 초기화 (`init-db.py`)

---

## 🎯 빠른 해결책

### 오류가 계속되면?

```bash
# 1. 모든 Docker 정리
docker system prune -a --volumes

# 2. 간단한 배포 사용
./deploy-simple.sh

# 3. 그래도 안 되면 로컬 실행
./start-test.sh
```

---

## 📞 지원

더 자세한 내용은 다음 문서를 참고하세요:

- [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) - Docker 배포 가이드
- [DEPLOYMENT.md](DEPLOYMENT.md) - 전체 배포 가이드
- [README.md](README.md) - 프로젝트 개요

---

**마지막 업데이트:** 2025-10-11

