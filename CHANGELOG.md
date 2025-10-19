# Changelog

프로젝트 변경 사항을 기록합니다.

---

## [2.0.1] - 2025-10-13

### 🔧 Fixed
- **PostgreSQL Boolean 타입 호환성 수정**
  - 모든 SQL 쿼리에서 `is_active = 1` → `is_active = TRUE` 변경
  - PostgreSQL과 SQLite 모두 호환

- **FastAPI Deprecation 경고 수정**
  - `@app.on_event("startup")` → `lifespan` 이벤트 핸들러로 마이그레이션
  - `@app.on_event("shutdown")` → `lifespan` 이벤트 핸들러로 마이그레이션

- **CORS 설정 개선**
  - `expose_headers` 추가
  - HTTPS 지원 추가
  - 중복 제거 로직 추가

- **Docker 이미지 경량화**
  - `Dockerfile.light` 생성 (~300MB)
  - 시스템 chromium 사용으로 용량 1/4 감소

### ✨ Added
- **데이터베이스 자동 초기화**
  - 컨테이너 시작 시 자동으로 `init-db-postgres.py` 실행
  - `fix-database-now.sh` 스크립트 추가
  - `check-admin-account.sh` 스크립트 추가

- **빠른 재배포 스크립트**
  - `quick-redeploy.sh` - 백엔드만 빠르게 재시작
  - `quick-fix-port.sh` - 포트 충돌 자동 해결

- **포트 관리 도구**
  - `fix-port-8001.sh` - 대화형 포트 정리
  - `check-cors.sh` - CORS 설정 확인

### 📝 Documentation
- `DOCKER_SIZE_COMPARISON.md` - Docker 이미지 크기 비교
- `README_DOCKER.md` - Docker 빌드 트러블슈팅
- `CHANGELOG.md` - 변경 사항 기록

---

## [2.0.0] - 2025-10-12

### 🎉 Initial Release

#### Backend
- FastAPI 기반 RESTful API
- PostgreSQL 데이터베이스
- JWT 인증
- Playwright 기반 네이버 검색 크롤링
- 스케줄러 (APScheduler)
- Aligo SMS 알림
- OpenAI API 기반 AI 블로그 작성

#### Frontend
- React 18 + TypeScript
- Vite 빌드 시스템
- Tailwind CSS
- React Query
- 대시보드, 키워드, 블로그, 타겟 관리
- 크롤링 결과 조회
- 설정 페이지
- AI 생성 글 관리

#### Features
- 키워드 및 블로그 관리
- 타겟 설정 (키워드-블로그 연결)
- 네이버 검색 크롤링
- 크롤링 결과 분석
- 순위 추적
- 자동 크롤링 스케줄
- SMS 알림
- AI 블로그 자동 작성
- 크롤링 기록 조회

#### Docker
- Production 배포 지원
- PostgreSQL 포함
- 자동 빌드 및 배포
- 환경 변수 관리

---

## Version History

- **2.0.1** - PostgreSQL 호환성 및 최적화
- **2.0.0** - 초기 릴리즈 (대대적인 리뉴얼)
- **1.x** - 레거시 버전 (SQLite + Jinja2)

---

## 업데이트 적용 방법

### 서버에서

```bash
# 1. 코드 업데이트
git pull

# 2. 빠른 재배포
./quick-redeploy.sh 49.50.134.250

# 또는 전체 재배포
./deploy-docker.sh 49.50.134.250
```

### 로컬에서

```bash
# 1. 코드 업데이트
git pull

# 2. 백엔드 재시작
./start-server.sh

# 또는 전체 재시작
./start-test.sh
```

---

## 다음 버전 계획

### v2.1.0 (예정)
- [ ] 네이버 블로그 자동 발행 API
- [ ] 결과 비교 기능 (이전 vs 현재)
- [ ] 이메일 알림
- [ ] 커스텀 대시보드 위젯
- [ ] 데이터 내보내기 (Excel, CSV)

### v2.2.0 (예정)
- [ ] 멀티 유저 지원
- [ ] 권한 관리
- [ ] 팀 협업 기능
- [ ] 댓글 모니터링

---

**버전 정보 확인:**
```bash
curl http://49.50.134.250:8001/ | grep version
```

