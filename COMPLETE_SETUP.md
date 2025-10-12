# 네이버 클라우드 완전 설정 가이드

49.50.134.250 서버에서 Naver Monitor를 완전히 설정하는 방법입니다.

## 🎯 전체 프로세스 요약

```
1. 디스크 정리         → emergency-cleanup.sh
2. 서버 설정          → setup-server.sh
3. 백엔드 시작         → start-server.sh
4. 프론트엔드 빌드     → build-frontend.sh (선택)
5. ACG 설정          → 네이버 클라우드 콘솔
6. 비밀번호 변경       → change-password.py
7. 접속 테스트         → http://49.50.134.250:8001/docs
```

---

## 🚀 완전 자동 설정

### 한 번에 실행 (백엔드만)

```bash
./emergency-cleanup.sh && \
./setup-server.sh && \
./start-server.sh && \
python3 change-password.py
```

### 프론트엔드 포함

```bash
# Node.js 설치 (최초 1회)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 빌드 및 시작
./build-frontend.sh 49.50.134.250
./start-server.sh
```

---

## 📋 단계별 상세 가이드

### 1단계: 긴급 디스크 정리

```bash
./emergency-cleanup.sh
```

**효과:** 5-8GB 확보

**확인:**
```bash
df -h
# 사용률 100% → 60-70%로 감소
```

---

### 2단계: 서버 설정

```bash
./setup-server.sh
```

**작업:**
- ✅ 가상환경 생성
- ✅ 패키지 설치
- ✅ Playwright 설치
- ✅ 데이터베이스 초기화

**소요 시간:** 3-5분

---

### 3단계: 백엔드 시작

```bash
./start-server.sh
```

**실행:**
- ✅ 백엔드 API (포트 8001)
- ✅ 백그라운드 실행

**확인:**
```bash
./check-server.sh
```

---

### 4단계: 프론트엔드 설정 (선택사항)

#### A. Node.js 설치

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 확인
node --version
npm --version
```

#### B. 프론트엔드 빌드

```bash
./build-frontend.sh 49.50.134.250
```

**작업:**
- ✅ `frontend/.env` 생성 (API URL 설정)
- ✅ 패키지 설치
- ✅ 프로덕션 빌드

#### C. 서버 재시작 (프론트엔드 포함)

```bash
./stop-server.sh
./start-server.sh
```

---

### 5단계: 네이버 클라우드 ACG 설정 (필수!)

#### 콘솔 접속

```
https://console.ncloud.com
```

#### 설정 경로

```
1. Server → Server 메뉴
2. 서버 선택 (s19946ec6360)
3. ACG 탭 클릭
4. ACG 이름 클릭
5. 인바운드 규칙 → 규칙 추가
```

#### 규칙 추가

**백엔드 (필수):**
```
프로토콜: TCP
포트 번호: 8001
접근 소스: 0.0.0.0/0
설명: Naver Monitor API
```

**프론트엔드 (선택):**
```
프로토콜: TCP
포트 번호: 3000
접근 소스: 0.0.0.0/0
설명: Naver Monitor Frontend
```

#### 적용

```
저장 → 적용 (서버에 반영)
```

---

### 6단계: 비밀번호 변경

```bash
python3 change-password.py
```

**입력:**
```
사용자 ID: 1
새 비밀번호: ********
비밀번호 확인: ********
✅ 비밀번호가 변경되었습니다!
```

---

### 7단계: 접속 테스트

#### 백엔드 API

```bash
# 로컬 PC에서
curl http://49.50.134.250:8001/

# 브라우저
http://49.50.134.250:8001/docs
```

#### 프론트엔드

```
http://49.50.134.250:3000
```

---

## 🔧 프론트엔드 API URL 문제 해결

### 문제

프론트엔드가 `http://localhost:8001`로 호출 → 공인 IP에서 작동 안 함

### 해결

#### 방법 1: 환경 변수 (자동)

```bash
# 빌드 스크립트가 자동으로 설정
./build-frontend.sh 49.50.134.250

# frontend/.env 자동 생성:
# VITE_API_URL=http://49.50.134.250:8001
```

#### 방법 2: 수동 설정

```bash
# frontend/.env 생성
cd frontend
cat > .env << EOF
VITE_API_URL=http://49.50.134.250:8001
EOF

# 재빌드
npm run build

# 재시작
cd ..
./start-server.sh
```

#### 방법 3: 소스 코드 직접 수정 (비권장)

`frontend/src/services/api.ts` 수정:
```typescript
// 변경 전
baseURL: 'http://localhost:8001/api',

// 변경 후
baseURL: 'http://49.50.134.250:8001/api',
```

---

## 📊 접속 URL 정리

### 백엔드 (필수)

```
http://49.50.134.250:8001       ← API 서버
http://49.50.134.250:8001/docs  ← API 문서 (Swagger) ⭐
```

### 프론트엔드 (선택)

```
http://49.50.134.250:3000       ← 웹 UI
```

**API 문서만으로도 모든 기능 사용 가능!**

---

## ✅ 최종 체크리스트

### 서버에서 실행

- [x] 디스크 정리: `./emergency-cleanup.sh`
- [x] 서버 설정: `./setup-server.sh`
- [x] 백엔드 시작: `./start-server.sh`
- [ ] 프론트엔드 빌드: `./build-frontend.sh 49.50.134.250` (선택)
- [ ] 비밀번호 변경: `python3 change-password.py`

### 네이버 클라우드 콘솔에서

- [ ] ACG 설정
- [ ] TCP 8001 포트 열기
- [ ] TCP 3000 포트 열기 (프론트엔드 사용 시)
- [ ] 저장 및 적용

### 로컬 PC에서 확인

- [ ] API 테스트: `curl http://49.50.134.250:8001/`
- [ ] 브라우저 접속: http://49.50.134.250:8001/docs
- [ ] 로그인 테스트: testuser / (변경한 비밀번호)

---

## 🎯 빠른 시작

### 백엔드만 사용 (권장)

```bash
# 서버에서
./emergency-cleanup.sh
./setup-server.sh
./start-server.sh
python3 change-password.py

# ACG 설정: TCP 8001

# 접속
http://49.50.134.250:8001/docs
```

### 프론트엔드 포함

```bash
# 서버에서
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
./build-frontend.sh 49.50.134.250
./start-server.sh

# ACG 설정: TCP 8001, 3000

# 접속
http://49.50.134.250:3000
```

---

## 🔥 문제 해결

### ERR_CONNECTION_REFUSED

**원인:** ACG에서 포트 차단

**해결:**
```
네이버 클라우드 콘솔
→ Server → ACG
→ 인바운드 규칙 추가
→ TCP 8001, 3000
```

### API 호출 실패 (프론트엔드)

**원인:** API URL이 localhost

**해결:**
```bash
./build-frontend.sh 49.50.134.250
./start-server.sh
```

---

## 🎉 완료!

**지금 실행:**

```bash
# 1. 비밀번호 변경
python3 change-password.py

# 2. 상태 확인
./check-server.sh

# 3. ACG 설정
# (네이버 클라우드 콘솔)

# 4. 접속
http://49.50.134.250:8001/docs
```

**모든 기능이 준비되었습니다!** 🚀

---

**로그인:**
```
사용자명: testuser
비밀번호: testpassword123 (변경 전)
```

**변경 후:**
```
사용자명: testuser
비밀번호: (새로 설정한 비밀번호)
```

