# Docker 빌드 에러 해결

Playwright 설치 문제로 빌드가 실패하는 경우 해결 방법입니다.

## 🔥 문제

```
RUN playwright install-deps chromium
exit code: 1
```

## ✅ 해결 방법

### 방법 1: Minimal Dockerfile 사용 (권장) ⭐

**docker-compose.prod.yml 수정:**

```yaml
backend:
  build:
    context: .
    dockerfile: Dockerfile.minimal  # ← 변경
```

**배포:**
```bash
./deploy-docker.sh 49.50.134.250
```

---

### 방법 2: 수동으로 Dockerfile.prod 수정

**Dockerfile.prod에서 변경:**

```dockerfile
# 변경 전
FROM python:3.9-slim
RUN playwright install chromium
RUN playwright install-deps chromium

# 변경 후
FROM python:3.9-bullseye
RUN playwright install --with-deps chromium
```

---

### 방법 3: Base 이미지 변경

**가장 안정적:**

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.40.0-focal

WORKDIR /app

# 시스템 패키지
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션
COPY . .

EXPOSE 8001
CMD ["python3", "server-debug.py"]
```

---

## 🚀 추천 설정

### docker-compose.prod.yml

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.minimal  # 안정적
    # ... 나머지 설정
```

---

## 📋 Dockerfile 비교

| Dockerfile | Base 이미지 | 크기 | 안정성 | 권장 |
|------------|-------------|------|--------|------|
| `Dockerfile.minimal` | python:3.9-bullseye | 중간 | 높음 | ⭐⭐⭐ |
| `Dockerfile.prod` | python:3.9-slim | 작음 | 중간 | ⭐⭐ |
| Playwright Base | playwright/python | 큼 | 최고 | ⭐ |

---

## 🔧 빌드 테스트

```bash
# Dockerfile.minimal 테스트
docker build -f Dockerfile.minimal -t naver-monitor-test .

# 성공하면
docker compose -f docker-compose.prod.yml up -d --build
```

---

## ⚡ 빠른 해결

**서버에서 실행:**

```bash
# 1. docker-compose.prod.yml 수정
nano docker-compose.prod.yml

# "dockerfile: Dockerfile.prod" → "dockerfile: Dockerfile.minimal"로 변경

# 2. 배포
./deploy-docker.sh 49.50.134.250
```

---

## ✅ 완료!

이제 Playwright 설치 문제 없이 빌드됩니다! 🎉

