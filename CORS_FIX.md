# CORS 에러 해결 가이드

## 🔥 문제

```
Access to XMLHttpRequest at 'http://49.50.134.250:8001/api/auth/login' 
from origin 'http://49.50.134.250:3000' 
has been blocked by CORS policy
```

## 🔍 원인

백엔드의 CORS 설정에 공인 IP가 포함되지 않음:

```python
# 문제가 있던 코드
allow_origins=["http://localhost:3001", "http://localhost:3000"]
```

프론트엔드는 `http://49.50.134.250:3000`에서 실행되지만,  
백엔드는 `localhost`만 허용하고 있음!

## ✅ 해결

### 자동 해결 (권장) ⭐

```bash
# 서버에서 실행
./setup-cors.sh 49.50.134.250
./start-backend-only.sh
```

**완료!**

---

### 수동 해결

#### 1단계: .env 파일 생성/수정

```bash
# .env 파일에 추가
PUBLIC_IP=49.50.134.250
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://49.50.134.250:3000,http://49.50.134.250:8001
```

#### 2단계: 백엔드 재시작

```bash
./start-backend-only.sh
```

---

## 🔧 설정 확인

### .env 파일 확인

```bash
cat .env | grep -E "PUBLIC_IP|CORS_ORIGINS"
```

**출력 예시:**
```
PUBLIC_IP=49.50.134.250
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://49.50.134.250:3000,http://49.50.134.250:8001
```

### 백엔드 로그 확인

```bash
tail -f logs/server.log | grep CORS
```

**출력 예시:**
```
🔍 CORS 허용 도메인: ['http://localhost:3000', 'http://localhost:3001', 'http://49.50.134.250:3000', 'http://49.50.134.250:8001']
```

---

## 🎯 테스트

### 브라우저 콘솔 확인

```
http://49.50.134.250:3000
```

**F12 → Console 탭:**
- ❌ 이전: CORS 에러
- ✅ 이후: 정상 요청

### 네트워크 탭 확인

**F12 → Network 탭:**

**Preflight Request (OPTIONS):**
```
Request:
  Origin: http://49.50.134.250:3000

Response Headers:
  Access-Control-Allow-Origin: http://49.50.134.250:3000 ✅
  Access-Control-Allow-Methods: * ✅
  Access-Control-Allow-Headers: * ✅
```

**Actual Request (POST):**
```
Status: 200 OK ✅
```

---

## 📋 코드 변경 내역

### server-debug.py

**변경 전:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**변경 후:**
```python
# 환경 변수에서 허용 도메인 가져오기
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

# 공인 IP도 추가
PUBLIC_IP = os.getenv("PUBLIC_IP", "")
if PUBLIC_IP:
    ALLOWED_ORIGINS.extend([
        f"http://{PUBLIC_IP}:3000",
        f"http://{PUBLIC_IP}:8001",
    ])

print(f"🔍 CORS 허용 도메인: {ALLOWED_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🚀 전체 실행 순서

### 서버에서 실행

```bash
# 1. CORS 설정
./setup-cors.sh 49.50.134.250

# 2. 백엔드 재시작
./start-backend-only.sh

# 3. 프론트엔드 확인 (이미 실행 중이면 스킵)
# ./rebuild-frontend.sh 49.50.134.250
```

### 브라우저에서 확인

```
http://49.50.134.250:3000
```

**로그인 테스트:**
- 사용자명: `testuser`
- 비밀번호: `testpassword123`

---

## 🔍 문제 해결

### CORS 에러가 계속 발생하면?

#### 1. 백엔드 로그 확인

```bash
tail -f logs/server.log | grep CORS
```

**확인 사항:**
- ✅ 공인 IP가 포함되어 있는가?
- ✅ 프론트엔드 URL이 정확한가?

#### 2. .env 파일 확인

```bash
cat .env
```

**확인 사항:**
- ✅ `PUBLIC_IP` 설정이 있는가?
- ✅ `CORS_ORIGINS`에 공인 IP가 포함되어 있는가?

#### 3. 백엔드 재시작

```bash
./stop-server.sh
./start-backend-only.sh
```

#### 4. 브라우저 캐시 삭제

```
F12 → Application → Clear storage → Clear site data
```

---

## 🎨 다른 도메인 추가

### HTTPS 사용 시

```bash
# .env에 추가
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### 여러 도메인

```bash
# .env에 추가
CORS_ORIGINS=http://localhost:3000,http://49.50.134.250:3000,https://yourdomain.com,https://www.yourdomain.com
```

### 모든 도메인 허용 (개발용, 비권장)

```python
# server-debug.py
allow_origins=["*"]
```

---

## ⚠️ 보안 주의사항

### 프로덕션 환경

```bash
# 특정 도메인만 허용
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 개발 환경

```bash
# localhost + 공인 IP
CORS_ORIGINS=http://localhost:3000,http://49.50.134.250:3000
```

---

## 🎉 완료!

**이제 CORS 에러 없이 정상적으로 작동합니다!**

- ✅ 프론트엔드에서 백엔드 API 호출 가능
- ✅ 로그인 정상 작동
- ✅ 모든 API 요청 정상 처리

---

## 📊 체크리스트

서버에서:
- [ ] `./setup-cors.sh 49.50.134.250` 실행
- [ ] `./start-backend-only.sh` 실행
- [ ] 로그에서 CORS 설정 확인

브라우저에서:
- [ ] `http://49.50.134.250:3000` 접속
- [ ] F12 → Console 탭에서 CORS 에러 없음 확인
- [ ] 로그인 테스트
- [ ] API 요청 정상 작동 확인

**모든 단계 완료!** 🎊

