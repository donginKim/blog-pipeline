# Docker 배포 가이드

외부 서버에서 Docker Compose를 사용하여 Naver Monitor를 배포하는 가이드입니다.

## 🎯 개요

Docker Compose를 사용하면:
- ✅ localhost 의존성 제거
- ✅ PostgreSQL 사용 (프로덕션 환경)
- ✅ 서비스 간 네트워크 자동 구성
- ✅ 환경 변수로 유연한 설정
- ✅ 쉬운 배포 및 관리

## 📋 시스템 구성

```
┌─────────────────────────────────────────┐
│         외부 서버 (49.50.134.250)        │
├─────────────────────────────────────────┤
│                                          │
│  ┌────────────┐  ┌─────────────────┐   │
│  │  Frontend  │  │    Backend      │   │
│  │  (Nginx)   │  │   (FastAPI)     │   │
│  │  :3000     │  │   :8001         │   │
│  └────────────┘  └─────────────────┘   │
│         │                 │             │
│         │                 │             │
│         │        ┌────────▼──────┐      │
│         │        │  PostgreSQL   │      │
│         │        │    :5432      │      │
│         │        └───────────────┘      │
│                                          │
│       docker-network (bridge)           │
└─────────────────────────────────────────┘
```

## 🚀 빠른 시작

### 1단계: Docker 설치 (최초 1회)

```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# 재로그인 또는
newgrp docker

# Docker 확인
docker --version
docker compose version
```

### 2단계: 배포 스크립트 실행 ⭐

```bash
# 공인 IP를 인자로 전달
./deploy-docker.sh 49.50.134.250
```

**자동 수행:**
1. ✅ .env 파일 생성
2. ✅ PUBLIC_IP, CORS 설정
3. ✅ Docker 이미지 빌드
4. ✅ 컨테이너 시작
5. ✅ 데이터베이스 초기화

### 3단계: ACG 설정

네이버 클라우드 콘솔에서 포트 열기:
- TCP 3000 (프론트엔드)
- TCP 8001 (백엔드)

### 4단계: 접속 테스트

```
http://49.50.134.250:3000
```

**로그인:**
- 사용자명: `testuser`
- 비밀번호: `testpassword123`

---

## 🔧 수동 배포

### .env 파일 생성

```bash
cp env.production.example .env
```

**편집:**
```bash
nano .env
```

**필수 설정:**
```env
PUBLIC_IP=49.50.134.250
POSTGRES_PASSWORD=강력한_비밀번호
SECRET_KEY=매우_강력한_시크릿_키
```

### Docker Compose 실행

```bash
# 빌드 및 시작
docker compose -f docker-compose.prod.yml up -d --build

# 로그 확인
docker compose -f docker-compose.prod.yml logs -f

# 상태 확인
docker compose -f docker-compose.prod.yml ps
```

### 데이터베이스 초기화

```bash
docker exec -it naver-monitor-backend python3 init-db-postgres.py
```

---

## 📊 컨테이너 관리

### 상태 확인

```bash
# 컨테이너 목록
docker compose -f docker-compose.prod.yml ps

# 상세 정보
docker ps
```

### 로그 확인

```bash
# 전체 로그
docker compose -f docker-compose.prod.yml logs -f

# 백엔드만
docker compose -f docker-compose.prod.yml logs -f backend

# 프론트엔드만
docker compose -f docker-compose.prod.yml logs -f frontend

# 데이터베이스만
docker compose -f docker-compose.prod.yml logs -f db
```

### 서비스 제어

```bash
# 중지
docker compose -f docker-compose.prod.yml stop

# 시작
docker compose -f docker-compose.prod.yml start

# 재시작
docker compose -f docker-compose.prod.yml restart

# 완전 종료 (볼륨 유지)
docker compose -f docker-compose.prod.yml down

# 완전 삭제 (볼륨 포함)
docker compose -f docker-compose.prod.yml down -v
```

### 개별 서비스 재시작

```bash
# 백엔드만 재시작
docker compose -f docker-compose.prod.yml restart backend

# 프론트엔드만 재시작
docker compose -f docker-compose.prod.yml restart frontend
```

---

## 🔐 보안 설정

### 비밀번호 변경

```bash
docker exec -it naver-monitor-backend python3 change-password.py
```

### .env 파일 보안

```bash
# 권한 설정
chmod 600 .env

# 확인
ls -la .env
# -rw------- 1 user group ... .env
```

### 강력한 시크릿 키 생성

```bash
# SECRET_KEY 생성
openssl rand -base64 32

# POSTGRES_PASSWORD 생성
openssl rand -base64 32
```

---

## 🔍 트러블슈팅

### 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker compose -f docker-compose.prod.yml logs

# 특정 컨테이너 로그
docker logs naver-monitor-backend
docker logs naver-monitor-frontend
docker logs naver-monitor-db
```

### 데이터베이스 연결 실패

```bash
# 데이터베이스 상태 확인
docker compose -f docker-compose.prod.yml ps db

# 데이터베이스 로그
docker compose -f docker-compose.prod.yml logs db

# 데이터베이스 접속 테스트
docker exec -it naver-monitor-db psql -U naver_monitor -d naver_monitor
```

### CORS 에러

**.env 파일 확인:**
```bash
cat .env | grep CORS_ORIGINS
```

**업데이트:**
```bash
# .env 파일 수정
nano .env

# 백엔드 재시작
docker compose -f docker-compose.prod.yml restart backend
```

### 디스크 용량 부족

```bash
# 사용하지 않는 이미지 삭제
docker system prune -a

# 볼륨 확인
docker volume ls

# 빌드 캐시 삭제
docker builder prune -a
```

---

## 🔄 업데이트

### 코드 업데이트

```bash
# 1. 코드 pull
git pull

# 2. 재빌드 및 재시작
docker compose -f docker-compose.prod.yml up -d --build

# 3. 로그 확인
docker compose -f docker-compose.prod.yml logs -f
```

### 환경 변수 변경

```bash
# 1. .env 수정
nano .env

# 2. 컨테이너 재생성 (재빌드 필요 없음)
docker compose -f docker-compose.prod.yml up -d

# 3. 확인
docker compose -f docker-compose.prod.yml logs -f backend
```

---

## 📦 백업 및 복원

### 데이터베이스 백업

```bash
# 백업 생성
docker exec naver-monitor-db pg_dump -U naver_monitor naver_monitor > backup_$(date +%Y%m%d).sql

# 백업 확인
ls -lh backup_*.sql
```

### 데이터베이스 복원

```bash
# 복원
docker exec -i naver-monitor-db psql -U naver_monitor naver_monitor < backup_20241019.sql
```

### 볼륨 백업

```bash
# 볼륨 목록
docker volume ls | grep naver-monitor

# 볼륨 백업 (tar)
docker run --rm -v naver-monitor_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data_$(date +%Y%m%d).tar.gz -C /data .
```

---

## 🎯 환경 변수 전체 목록

### 필수 설정

| 변수 | 설명 | 예시 |
|------|------|------|
| `PUBLIC_IP` | 공인 IP 주소 | `49.50.134.250` |
| `POSTGRES_PASSWORD` | DB 비밀번호 | `강력한_비밀번호` |
| `SECRET_KEY` | JWT 시크릿 키 | `매우_강력한_키` |

### 선택 설정

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `BACKEND_PORT` | 백엔드 포트 | `8001` |
| `FRONTEND_PORT` | 프론트엔드 포트 | `3000` |
| `POSTGRES_USER` | DB 사용자명 | `naver_monitor` |
| `POSTGRES_DB` | DB 이름 | `naver_monitor` |
| `ALIGO_API_KEY` | Aligo SMS API 키 | (비어있음) |
| `ALIGO_USER_ID` | Aligo 사용자 ID | (비어있음) |
| `ALIGO_SENDER` | Aligo 발신번호 | (비어있음) |
| `OPENAI_API_KEY` | OpenAI API 키 | (비어있음) |

---

## 🎉 완료!

**배포 확인:**

```bash
# 컨테이너 상태
docker compose -f docker-compose.prod.yml ps

# 접속 테스트
curl http://49.50.134.250:8001/
curl http://49.50.134.250:3000/
```

**브라우저 접속:**

```
http://49.50.134.250:3000
```

**모든 준비가 완료되었습니다!** 🎊🚀

---

## 📋 체크리스트

서버에서:
- [ ] Docker 설치
- [ ] `./deploy-docker.sh 49.50.134.250` 실행
- [ ] 컨테이너 상태 확인
- [ ] 로그 확인

네이버 클라우드:
- [ ] ACG 설정 (TCP 3000, 8001)

브라우저:
- [ ] 프론트엔드 접속 확인
- [ ] 로그인 테스트
- [ ] 비밀번호 변경

보안:
- [ ] .env 파일 권한 설정 (600)
- [ ] SECRET_KEY 변경
- [ ] POSTGRES_PASSWORD 변경
- [ ] 사용자 비밀번호 변경

**모든 단계 완료!** ✅
