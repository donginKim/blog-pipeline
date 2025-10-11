# 프로덕션 배포 가이드

Naver Monitor를 Docker Compose를 사용하여 프로덕션 환경에 배포하는 방법을 안내합니다.

## 목차

- [시스템 요구사항](#시스템-요구사항)
- [배포 아키텍처](#배포-아키텍처)
- [배포 준비](#배포-준비)
- [배포 실행](#배포-실행)
- [서비스 관리](#서비스-관리)
- [SSL/HTTPS 설정](#sslhttps-설정)
- [백업 및 복원](#백업-및-복원)
- [모니터링](#모니터링)
- [문제 해결](#문제-해결)

---

## 시스템 요구사항

### 하드웨어

| 구분 | 최소 사양 | 권장 사양 |
|------|-----------|-----------|
| CPU | 2 Core | 4 Core |
| RAM | 4 GB | 8 GB |
| 디스크 | 20 GB | 50 GB (SSD 권장) |
| 네트워크 | 100 Mbps | 1 Gbps |

### 소프트웨어

- **OS**: Ubuntu 20.04 LTS 이상 / CentOS 8 이상 / Debian 11 이상
- **Docker**: 20.10 이상
- **Docker Compose**: 2.0 이상

---

## 배포 아키텍처

```
┌─────────────────────────────────────────────────┐
│                   인터넷                         │
└─────────────────┬───────────────────────────────┘
                  │
                  │ HTTPS (443) / HTTP (80)
                  │
┌─────────────────▼───────────────────────────────┐
│              Nginx (리버스 프록시)                │
│         - SSL 종료                               │
│         - 정적 파일 캐싱                          │
│         - 부하 분산                               │
└──────────┬──────────────────┬───────────────────┘
           │                  │
           │ /api/*           │ /*
           │                  │
┌──────────▼──────────┐  ┌────▼─────────────────┐
│  FastAPI Backend    │  │  React Frontend      │
│  - API 서버         │  │  - SPA               │
│  - 크롤링 엔진       │  │  - UI                │
│  - 비즈니스 로직     │  │                      │
└──────┬──────┬───────┘  └──────────────────────┘
       │      │
       │      └─────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────┐
│ PostgreSQL  │  │   Redis     │
│ - 데이터 저장│  │ - 캐싱      │
│ - 영구 저장소│  │ - 세션      │
└─────────────┘  └─────────────┘
```

### 서비스 구성

1. **Nginx**: 리버스 프록시 및 SSL 종료
2. **Backend**: FastAPI 기반 API 서버
3. **Frontend**: React SPA
4. **PostgreSQL**: 메인 데이터베이스
5. **Redis**: 캐싱 및 세션 관리

---

## 배포 준비

### 1. 저장소 클론

```bash
git clone https://github.com/yourusername/naver-monitor.git
cd naver-monitor
```

### 2. 환경 변수 설정

```bash
# 예시 파일 복사
cp env.production.example .env.production

# 환경 변수 편집
nano .env.production
```

#### 필수 설정 항목

```bash
# 데이터베이스
POSTGRES_PASSWORD=강력한_비밀번호_입력

# Redis
REDIS_PASSWORD=강력한_비밀번호_입력

# JWT 인증
SECRET_KEY=최소_32자_이상의_무작위_문자열

# 도메인 (실제 도메인으로 변경)
CORS_ORIGINS=https://yourdomain.com
VITE_API_URL=https://yourdomain.com/api
```

#### 비밀번호 생성 예시

```bash
# PostgreSQL 비밀번호 (32자)
openssl rand -base64 32

# Redis 비밀번호 (32자)
openssl rand -base64 32

# JWT Secret Key (64자)
openssl rand -base64 64
```

### 3. SSL 인증서 준비 (선택사항)

#### Let's Encrypt 사용

```bash
# Certbot 설치
sudo apt-get update
sudo apt-get install certbot

# 인증서 발급
sudo certbot certonly --standalone -d yourdomain.com

# 인증서 복사
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
sudo chmod 644 nginx/ssl/*.pem
```

#### 자체 서명 인증서 (테스트용)

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/CN=yourdomain.com"
```

---

## 배포 실행

### 자동 배포 (권장)

```bash
./deploy.sh
```

이 스크립트는 다음 작업을 자동으로 수행합니다:
1. ✅ 환경 변수 확인
2. ✅ Docker 환경 확인
3. ✅ 이미지 빌드
4. ✅ 컨테이너 시작
5. ✅ 헬스체크
6. ✅ 상태 확인

### 수동 배포

#### 1. 이미지 빌드

```bash
docker-compose -f docker-compose.prod.yml \
  --env-file .env.production build
```

#### 2. 컨테이너 시작

```bash
docker-compose -f docker-compose.prod.yml \
  --env-file .env.production up -d
```

#### 3. 상태 확인

```bash
docker-compose -f docker-compose.prod.yml ps
```

### 배포 확인

```bash
# 서비스 접속
curl http://localhost/health

# API 문서 확인
curl http://localhost/api/docs

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 서비스 관리

### 기본 명령어

```bash
# 서비스 중지
docker-compose -f docker-compose.prod.yml down

# 서비스 재시작
docker-compose -f docker-compose.prod.yml restart

# 특정 서비스만 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 로그 확인 (실시간)
docker-compose -f docker-compose.prod.yml logs -f

# 특정 서비스 로그
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 스케일링

```bash
# 백엔드 워커 증가
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# 상태 확인
docker-compose -f docker-compose.prod.yml ps
```

### 업데이트 배포

```bash
# 1. 코드 업데이트
git pull origin main

# 2. 이미지 재빌드
docker-compose -f docker-compose.prod.yml \
  --env-file .env.production build

# 3. 무중단 재배포
docker-compose -f docker-compose.prod.yml \
  --env-file .env.production up -d --no-deps --build backend frontend

# 4. 확인
docker-compose -f docker-compose.prod.yml ps
```

### 데이터베이스 마이그레이션

```bash
# 백엔드 컨테이너 접속
docker-compose -f docker-compose.prod.yml exec backend bash

# Alembic 마이그레이션 실행
alembic upgrade head

# 종료
exit
```

---

## SSL/HTTPS 설정

### Nginx SSL 활성화

`nginx/nginx.conf` 파일에서 HTTPS 서버 블록의 주석을 해제합니다:

```nginx
# HTTPS 서버 주석 해제
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # ... 나머지 설정
}
```

### HTTP to HTTPS 리다이렉트

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        return 301 https://$host$request_uri;
    }
}
```

### SSL 갱신 자동화 (Let's Encrypt)

```bash
# Cron 작업 추가
sudo crontab -e

# 매월 1일 오전 3시에 갱신
0 3 1 * * certbot renew --quiet && \
  cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /path/to/nginx/ssl/cert.pem && \
  cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /path/to/nginx/ssl/key.pem && \
  docker-compose -f /path/to/docker-compose.prod.yml restart nginx
```

---

## 백업 및 복원

### 데이터베이스 백업

#### 자동 백업 스크립트

```bash
#!/bin/bash
# backup-db.sh

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/naver_monitor_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

# PostgreSQL 백업
docker-compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U admin naver_monitor > $BACKUP_FILE

# 압축
gzip $BACKUP_FILE

# 7일 이상 된 백업 삭제
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "✅ 백업 완료: ${BACKUP_FILE}.gz"
```

#### 백업 자동화 (Cron)

```bash
# 매일 오전 2시에 백업
0 2 * * * /path/to/backup-db.sh >> /var/log/naver-monitor-backup.log 2>&1
```

### 데이터베이스 복원

```bash
# 백업 파일 압축 해제
gunzip naver_monitor_20250110_020000.sql.gz

# 데이터베이스 복원
cat naver_monitor_20250110_020000.sql | \
  docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U admin naver_monitor
```

### 볼륨 백업

```bash
# 전체 볼륨 백업
docker run --rm \
  -v naver-monitor_postgres_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/postgres_data_$(date +%Y%m%d).tar.gz /data

# Redis 데이터 백업
docker run --rm \
  -v naver-monitor_redis_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/redis_data_$(date +%Y%m%d).tar.gz /data
```

---

## 모니터링

### 헬스체크 엔드포인트

```bash
# Nginx 헬스체크
curl http://localhost/health

# 백엔드 헬스체크
curl http://localhost/api/health

# 프론트엔드 헬스체크
curl http://localhost:3000/health
```

### 로그 모니터링

```bash
# 전체 로그 (실시간)
docker-compose -f docker-compose.prod.yml logs -f

# 에러 로그만
docker-compose -f docker-compose.prod.yml logs | grep ERROR

# 로그 파일 직접 확인
tail -f logs/nginx/access.log
tail -f logs/nginx/error.log
```

### 리소스 모니터링

```bash
# 컨테이너 리소스 사용량
docker stats

# 디스크 사용량
df -h

# Docker 볼륨 사용량
docker system df -v
```

### 외부 모니터링 도구 연동

#### Prometheus + Grafana (선택사항)

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
```

---

## 문제 해결

### Q1: 컨테이너가 시작되지 않음

**증상:**
```
ERROR: Container ... is unhealthy
```

**해결:**
```bash
# 1. 로그 확인
docker-compose -f docker-compose.prod.yml logs

# 2. 특정 서비스 로그
docker-compose -f docker-compose.prod.yml logs backend

# 3. 헬스체크 수동 실행
docker-compose -f docker-compose.prod.yml exec backend curl http://localhost:8000/health
```

---

### Q2: 데이터베이스 연결 실패

**증상:**
```
could not connect to server: Connection refused
```

**해결:**
```bash
# 1. PostgreSQL 상태 확인
docker-compose -f docker-compose.prod.yml ps postgres

# 2. PostgreSQL 로그 확인
docker-compose -f docker-compose.prod.yml logs postgres

# 3. 연결 테스트
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U admin -d naver_monitor -c "SELECT 1;"

# 4. 환경 변수 확인
docker-compose -f docker-compose.prod.yml exec backend env | grep DATABASE
```

---

### Q3: 502 Bad Gateway 오류

**증상:**
브라우저에서 502 오류

**해결:**
```bash
# 1. 백엔드 상태 확인
docker-compose -f docker-compose.prod.yml ps backend

# 2. Nginx 설정 테스트
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# 3. Nginx 재시작
docker-compose -f docker-compose.prod.yml restart nginx

# 4. 백엔드 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

---

### Q4: 디스크 공간 부족

**증상:**
```
no space left on device
```

**해결:**
```bash
# 1. 디스크 사용량 확인
df -h
docker system df

# 2. 사용하지 않는 이미지 삭제
docker image prune -a

# 3. 사용하지 않는 볼륨 삭제
docker volume prune

# 4. 로그 정리
docker-compose -f docker-compose.prod.yml logs --tail=0 -f &
rm -rf logs/*.log

# 5. 오래된 백업 삭제
find /backups -name "*.sql.gz" -mtime +30 -delete
```

---

### Q5: 크롤링이 작동하지 않음

**증상:**
크롤링 결과가 없음

**해결:**
```bash
# 1. Playwright 브라우저 설치 확인
docker-compose -f docker-compose.prod.yml exec backend playwright install chromium

# 2. 크롤링 로그 확인
docker-compose -f docker-compose.prod.yml logs backend | grep "크롤링"

# 3. 메모리 확인 (Playwright는 메모리 사용량이 높음)
docker stats backend

# 4. 타임아웃 증가 (필요시)
# .env.production에 추가:
# CRAWL_TIMEOUT=120
```

---

## 성능 최적화

### 데이터베이스 최적화

```sql
-- PostgreSQL 연결
docker-compose -f docker-compose.prod.yml exec postgres psql -U admin naver_monitor

-- 인덱스 확인
SELECT tablename, indexname FROM pg_indexes WHERE schemaname = 'public';

-- 느린 쿼리 분석
SELECT query, mean_exec_time, calls FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;

-- VACUUM 실행
VACUUM ANALYZE;
```

### Nginx 캐싱

```nginx
# nginx/nginx.conf에 추가
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    proxy_cache_bypass $http_cache_control;
    add_header X-Cache-Status $upstream_cache_status;
    # ... 나머지 설정
}
```

### Redis 최적화

```bash
# redis.conf 추가 설정
# maxmemory 1gb
# maxmemory-policy allkeys-lru
```

---

## 보안 체크리스트

- [ ] 강력한 비밀번호 설정 (DB, Redis, JWT)
- [ ] SSL/TLS 인증서 설정
- [ ] 방화벽 설정 (필요한 포트만 개방)
- [ ] 기본 계정 비밀번호 변경
- [ ] 정기적인 백업 설정
- [ ] 로그 모니터링 설정
- [ ] 보안 업데이트 자동화
- [ ] CORS 설정 확인
- [ ] SQL Injection 방지 확인
- [ ] XSS 방지 헤더 설정

---

## 유용한 명령어 모음

```bash
# 전체 재시작
docker-compose -f docker-compose.prod.yml restart

# 볼륨 포함 전체 삭제
docker-compose -f docker-compose.prod.yml down -v

# 이미지 강제 재빌드
docker-compose -f docker-compose.prod.yml build --no-cache

# 특정 서비스 셸 접속
docker-compose -f docker-compose.prod.yml exec backend bash

# 컨테이너 리소스 제한
docker-compose -f docker-compose.prod.yml up -d --scale backend=2 \
  --cpus=2 --memory=4g

# 네트워크 확인
docker network ls
docker network inspect naver-monitor_naver-monitor-network
```

---

## 참고 자료

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)
- [Nginx 문서](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**마지막 업데이트:** 2025-10-10  
**버전:** 1.0.0

