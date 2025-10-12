# Docker 배포 가이드

Naver Monitor를 Docker로 배포하는 두 가지 방법을 안내합니다.

## 📋 목차

- [배포 옵션 비교](#배포-옵션-비교)
- [방법 1: 간단한 배포 (SQLite)](#방법-1-간단한-배포-sqlite)
- [방법 2: 프로덕션 배포 (PostgreSQL)](#방법-2-프로덕션-배포-postgresql)
- [문제 해결](#문제-해결)

---

## 배포 옵션 비교

### 간단한 배포 vs 프로덕션 배포

| 항목 | 간단한 배포 (SQLite) | 프로덕션 배포 (PostgreSQL) |
|------|---------------------|---------------------------|
| **데이터베이스** | SQLite (파일) | PostgreSQL (서버) |
| **컨테이너 수** | 2개 (백엔드, 프론트엔드) | 5개 (백엔드, 프론트엔드, DB, Redis, Nginx) |
| **설정 복잡도** | ⭐ 간단 | ⭐⭐⭐ 복잡 |
| **성능** | 소규모 | 대규모 |
| **스케일링** | 제한적 | 자유로움 |
| **백업** | 파일 복사 | pg_dump |
| **동시 접속** | 제한적 | 무제한 |
| **적합 환경** | 개인/소규모 | 기업/대규모 |
| **비용** | 낮음 | 중간 |

### 권장 사용 시나리오

#### 간단한 배포 (SQLite) 권장
- ✅ 개인 사용
- ✅ 소규모 팀 (1-5명)
- ✅ 크롤링 타겟 < 100개
- ✅ 빠른 시작 필요
- ✅ 서버 리소스 제한적

#### 프로덕션 배포 (PostgreSQL) 권장
- ✅ 기업 사용
- ✅ 중대규모 팀 (5명 이상)
- ✅ 크롤링 타겟 > 100개
- ✅ 고가용성 필요
- ✅ 충분한 서버 리소스

---

## 방법 1: 간단한 배포 (SQLite)

### 특징
- ✅ SQLite 파일 데이터베이스
- ✅ 최소 설정
- ✅ 2개 컨테이너만 (백엔드, 프론트엔드)
- ✅ 5분 안에 배포 완료

### 시스템 요구사항

**최소 사양:**
- CPU: 1 Core
- RAM: 2 GB
- Disk: 10 GB

**권장 사양:**
- CPU: 2 Core
- RAM: 4 GB
- Disk: 20 GB

### 배포 단계

#### 1️⃣ 데이터베이스 초기화

```bash
# 데이터베이스 생성
python3 init-db.py
```

#### 2️⃣ 환경 변수 설정 (선택사항)

```bash
# .env 파일 생성
cp env.aligo.example .env

# 필요한 API 키 설정
nano .env
```

**선택사항 설정:**
```bash
# 알리고 SMS (선택)
ALIGO_API_KEY=your_key
ALIGO_USER_ID=your_id
ALIGO_SENDER=01012345678

# OpenAI API (선택)
OPENAI_API_KEY=sk-proj-xxxxx

# JWT Secret (권장)
SECRET_KEY=your-super-secret-key-here
```

#### 3️⃣ 배포 실행

```bash
# 한 줄 명령어로 배포
./deploy-simple.sh
```

또는 수동:
```bash
docker-compose -f docker-compose.simple.yml up -d
```

#### 4️⃣ 접속 확인

```bash
# 서비스 상태
docker-compose -f docker-compose.simple.yml ps

# 헬스체크
curl http://localhost:8001/

# 브라우저 접속
http://localhost:3000
```

### 관리 명령어

```bash
# 로그 확인
docker-compose -f docker-compose.simple.yml logs -f

# 재시작
docker-compose -f docker-compose.simple.yml restart

# 중지
docker-compose -f docker-compose.simple.yml down

# 업데이트 배포
git pull
docker-compose -f docker-compose.simple.yml up -d --build
```

### 백업 및 복원

```bash
# 백업
cp naver_monitor.db naver_monitor.db.backup.$(date +%Y%m%d)

# 복원
cp naver_monitor.db.backup.20250110 naver_monitor.db

# 컨테이너 재시작
docker-compose -f docker-compose.simple.yml restart backend
```

---

## 방법 2: 프로덕션 배포 (PostgreSQL)

### 특징
- ✅ PostgreSQL 데이터베이스
- ✅ Redis 캐싱
- ✅ Nginx 리버스 프록시
- ✅ 고가용성
- ✅ 스케일링 가능

### 시스템 요구사항

**최소 사양:**
- CPU: 2 Core
- RAM: 4 GB
- Disk: 20 GB

**권장 사양:**
- CPU: 4 Core
- RAM: 8 GB
- Disk: 50 GB (SSD)

### 배포 단계

#### 1️⃣ 환경 변수 설정

```bash
# 환경 변수 파일 생성
cp env.production.example .env.production

# 필수 항목 수정
nano .env.production
```

**필수 변경 항목:**
```bash
# 강력한 비밀번호 생성
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 64)

# 도메인 설정
CORS_ORIGINS=https://yourdomain.com
VITE_API_URL=https://yourdomain.com/api
```

#### 2️⃣ 배포 실행

```bash
# 자동 배포
./deploy.sh
```

또는 수동:
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
```

#### 3️⃣ SSL 설정 (선택사항)

```bash
# Let's Encrypt 인증서
certbot certonly --standalone -d yourdomain.com

# 인증서 복사
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem

# Nginx 설정에서 HTTPS 활성화
nano nginx/nginx.conf
# (HTTPS 서버 블록 주석 해제)

# Nginx 재시작
docker-compose -f docker-compose.prod.yml restart nginx
```

### 관리 명령어

```bash
# 서비스 상태
docker-compose -f docker-compose.prod.yml --env-file .env.production ps

# 로그 확인
docker-compose -f docker-compose.prod.yml --env-file .env.production logs -f

# 재시작
docker-compose -f docker-compose.prod.yml --env-file .env.production restart

# 스케일링
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --scale backend=3
```

### 백업

```bash
# PostgreSQL 백업
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U admin naver_monitor > backup_$(date +%Y%m%d).sql

# 압축
gzip backup_$(date +%Y%m%d).sql
```

---

## 문제 해결

### Docker 빌드 실패

**증상:**
```
ERROR: failed to build: failed to solve: process ... did not complete successfully: exit code: 100
```

**해결:**

#### 1. Dockerfile.simple 사용 (권장)

```bash
# 간단한 배포 사용
./deploy-simple.sh
```

#### 2. Playwright 의존성 문제

```bash
# Dockerfile.prod 수정됨
# 이미 Playwright 의존성 포함되어 있음
docker-compose -f docker-compose.prod.yml build --no-cache
```

#### 3. apt-get 오류

```bash
# 네트워크 확인
ping -c 3 archive.ubuntu.com

# Docker 재시작
sudo systemctl restart docker

# 다시 빌드
docker-compose -f docker-compose.simple.yml build
```

### 컨테이너 시작 실패

**증상:**
```
ERROR: Container ... is unhealthy
```

**해결:**
```bash
# 로그 확인
docker-compose -f docker-compose.simple.yml logs backend

# 데이터베이스 권한 확인
ls -la naver_monitor.db

# 권한 수정
chmod 666 naver_monitor.db

# 재시작
docker-compose -f docker-compose.simple.yml restart
```

### 포트 충돌

**증상:**
```
ERROR: ... address already in use
```

**해결:**
```bash
# 사용 중인 프로세스 확인
lsof -i:8001
lsof -i:3000

# 종료
kill -9 <PID>

# 포트 변경 (docker-compose.simple.yml)
ports:
  - "8002:8000"  # 8001 → 8002
```

---

## 권장 배포 방법

### 개인/소규모

```bash
# 간단한 배포 (SQLite) 사용
./deploy-simple.sh
```

### 기업/대규모

```bash
# 프로덕션 배포 (PostgreSQL) 사용
./deploy.sh
```

---

## 상세 문서

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - 전체 프로덕션 배포 가이드
- **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** - 빠른 배포
- **[README.md](README.md)** - 프로젝트 개요

---

**마지막 업데이트:** 2025-10-11  
**버전:** 1.0.0

