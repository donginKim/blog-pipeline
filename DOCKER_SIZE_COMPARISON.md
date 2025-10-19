# Docker 이미지 크기 비교

## 📊 이미지 크기 예상치

| Dockerfile | Base 이미지 | 예상 크기 | Playwright | 추천 |
|------------|-------------|-----------|------------|------|
| **Dockerfile.light** ⭐ | python:3.9-slim | ~300MB | 시스템 chromium | **✅ 권장** |
| Dockerfile.minimal | python:3.9-bullseye | ~800MB | Playwright + chromium | ⚠️ 안정적 |
| Dockerfile.prod | python:3.9-slim | ~1.2GB | Playwright 전체 | ❌ 너무 큼 |
| Playwright 공식 | playwright/python | ~2GB+ | 모든 브라우저 | ❌ 매우 큼 |

---

## ⚡ 권장: Dockerfile.light

### 장점
- ✅ **작은 용량** (~300MB)
- ✅ **빠른 빌드** (시스템 패키지만)
- ✅ **충분한 기능** (Chromium 포함)
- ✅ **낮은 디스크 사용**

### 설정
**docker-compose.prod.yml:**
```yaml
backend:
  build:
    dockerfile: Dockerfile.light
  environment:
    CHROMIUM_PATH: /usr/bin/chromium
```

---

## 🔍 용량 차이 이유

### Dockerfile.light (300MB)
```
python:3.9-slim     200MB
+ chromium           80MB
+ 기타 패키지         20MB
= 총 300MB
```

### Dockerfile.minimal (800MB)
```
python:3.9-bullseye 400MB
+ playwright        300MB
+ chromium (playwright) 100MB
= 총 800MB
```

### Dockerfile.prod (1.2GB)
```
python:3.9-slim     200MB
+ 모든 playwright 의존성 500MB
+ chromium (playwright) 500MB
= 총 1.2GB
```

---

## 🚀 현재 설정 (최적화)

`docker-compose.prod.yml`이 이미 `Dockerfile.light`를 사용하도록 설정되어 있습니다!

```bash
# 빌드 및 확인
docker compose -f docker-compose.prod.yml build backend

# 이미지 크기 확인
docker images | grep naver-monitor
```

---

## 📦 디스크 공간 확인

### 빌드 전
```bash
df -h
```

### 이미지 크기 확인
```bash
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

---

## ⚙️ 추가 최적화 옵션

### 1. Multi-stage Build (더 작게)
```dockerfile
# Stage 1: 빌드
FROM python:3.9 as builder
# ... 빌드 단계

# Stage 2: 런타임 (더 작음)
FROM python:3.9-slim
COPY --from=builder /app /app
```

### 2. Alpine Linux (최소)
```dockerfile
FROM python:3.9-alpine
# 크기: ~150MB
# 단점: 호환성 문제 가능
```

---

## ✅ 최종 추천

**지금 설정 (`Dockerfile.light`) 그대로 사용하세요!**

- 용량: ~300MB (허용 범위)
- 안정성: 높음
- 빌드 속도: 빠름
- 유지보수: 쉬움

---

## 🔧 배포

```bash
# 서버에서
./deploy-docker.sh 49.50.134.250

# 용량 확인
docker system df
```

완벽한 균형입니다! 🎉

