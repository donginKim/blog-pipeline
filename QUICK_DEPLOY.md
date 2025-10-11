# 빠른 배포 가이드

프로덕션 환경에 Naver Monitor를 빠르게 배포하는 방법입니다.

## 🚀 5분 안에 배포하기

### 1️⃣ 사전 준비

```bash
# Docker 및 Docker Compose 설치 확인
docker --version
docker-compose --version
```

### 2️⃣ 환경 변수 설정

```bash
# 환경 변수 파일 생성
cp env.production.example .env.production

# 중요! 다음 항목을 반드시 변경하세요:
nano .env.production
```

**필수 변경 항목:**
```bash
POSTGRES_PASSWORD=여기에_강력한_비밀번호  # 32자 이상
REDIS_PASSWORD=여기에_강력한_비밀번호      # 32자 이상
SECRET_KEY=여기에_JWT_시크릿_키            # 64자 이상
CORS_ORIGINS=https://yourdomain.com       # 실제 도메인
```

**비밀번호 생성:**
```bash
# PostgreSQL 비밀번호
openssl rand -base64 32

# Redis 비밀번호
openssl rand -base64 32

# JWT Secret Key
openssl rand -base64 64
```

### 3️⃣ 배포 실행

```bash
# 한 줄 명령어로 배포
./deploy.sh
```

또는 수동 배포:
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
```

### 4️⃣ 접속 확인

```bash
# 서비스 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 헬스체크
curl http://localhost/health

# 브라우저 접속
# http://localhost (또는 http://your-server-ip)
```

### 5️⃣ 첫 로그인

```
사용자명: admin
비밀번호: admin123
```

⚠️ **첫 로그인 후 반드시 비밀번호 변경!**

```bash
python3 update-account.py
# 선택: 3 (비밀번호 변경)
```

---

## 📊 서비스 확인

### 접속 URL

- **프론트엔드**: http://localhost
- **API 문서**: http://localhost/api/docs
- **백엔드 API**: http://localhost/api

### 서비스 상태

```bash
# 전체 서비스
docker-compose -f docker-compose.prod.yml ps

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 🔧 기본 관리 명령어

### 서비스 제어

```bash
# 중지
docker-compose -f docker-compose.prod.yml down

# 재시작
docker-compose -f docker-compose.prod.yml restart

# 재배포
./deploy.sh
```

### 로그 확인

```bash
# 전체 로그
docker-compose -f docker-compose.prod.yml logs -f

# 백엔드만
docker-compose -f docker-compose.prod.yml logs -f backend

# 최근 100줄
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### 백업

```bash
# 데이터베이스 백업
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U admin naver_monitor > backup_$(date +%Y%m%d).sql

# 압축
gzip backup_$(date +%Y%m%d).sql
```

---

## ⚠️ 주의사항

### 보안

- [ ] `.env.production` 파일의 비밀번호를 반드시 변경
- [ ] 기본 계정(admin) 비밀번호 변경
- [ ] 방화벽 설정 (필요한 포트만 개방)
- [ ] SSL/HTTPS 설정 (프로덕션 필수)

### 포트

기본 포트:
- `80`: HTTP (Nginx)
- `443`: HTTPS (Nginx, SSL 설정 시)
- `5432`: PostgreSQL (외부 접근 비권장)
- `6379`: Redis (외부 접근 비권장)

### 리소스

최소 사양:
- CPU: 2 Core
- RAM: 4 GB
- Disk: 20 GB

권장 사양:
- CPU: 4 Core
- RAM: 8 GB
- Disk: 50 GB (SSD)

---

## 🆘 문제 해결

### 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker-compose -f docker-compose.prod.yml logs

# 특정 서비스 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

### 502 Bad Gateway

```bash
# 백엔드 상태 확인
docker-compose -f docker-compose.prod.yml ps backend

# 백엔드 재시작
docker-compose -f docker-compose.prod.yml restart backend nginx
```

### 데이터베이스 연결 오류

```bash
# PostgreSQL 상태 확인
docker-compose -f docker-compose.prod.yml ps postgres

# 연결 테스트
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U admin -d naver_monitor -c "SELECT 1;"
```

### 로그인 실패

```bash
# 사용자 확인
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U admin -d naver_monitor -c "SELECT username, email, is_active FROM users;"

# 비밀번호 재설정
python3 update-account.py
```

---

## 📖 상세 문서

더 자세한 내용은 다음 문서를 참고하세요:

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - 전체 배포 가이드
  - SSL/HTTPS 설정
  - 백업 및 복원
  - 모니터링
  - 성능 최적화
  
- **[ACCOUNT_MANAGEMENT.md](ACCOUNT_MANAGEMENT.md)** - 계정 관리
  - 사용자 생성/수정/삭제
  - 비밀번호 변경
  - 권한 관리

---

## 🎯 다음 단계

배포 완료 후:

1. ✅ 비밀번호 변경
2. ✅ 백업 설정
3. ✅ SSL 인증서 설정 (프로덕션)
4. ✅ 모니터링 설정
5. ✅ 크롤링 설정 및 테스트

---

**도움이 필요하신가요?**

- 전체 문서: [DEPLOYMENT.md](DEPLOYMENT.md)
- 이슈 리포트: GitHub Issues
- 문의: 관리자에게 문의

---

**마지막 업데이트:** 2025-10-10

