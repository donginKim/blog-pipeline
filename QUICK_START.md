# 빠른 시작 가이드

서버에서 Naver Monitor를 빠르게 시작하는 방법입니다.

## 🎯 백엔드만 사용 (가장 빠름) ⭐

### 1단계: 디스크 정리 (최초 1회)

```bash
./emergency-cleanup.sh
```

### 2단계: 서버 설정 (최초 1회)

```bash
./setup-server.sh
```

### 3단계: 백엔드 시작

```bash
./start-backend-only.sh
```

### 4단계: 비밀번호 변경

```bash
python3 change-password.py
```

### 5단계: 네이버 클라우드 ACG 설정

```
https://console.ncloud.com
→ Server → Server
→ 서버 선택
→ ACG 탭
→ 인바운드 규칙 추가:
   프로토콜: TCP
   포트: 8001
   소스: 0.0.0.0/0
→ 저장 및 적용
```

### 6단계: 접속

```
http://49.50.134.250:8001/docs
```

**로그인:**
- 사용자명: `testuser`
- 비밀번호: (변경한 비밀번호)

---

## 🎨 프론트엔드 포함 (선택사항)

### 추가 단계 1: Node.js 설치 (최초 1회)

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 추가 단계 2: 프론트엔드 빌드

```bash
./rebuild-frontend.sh 49.50.134.250
```

### 추가 단계 3: ACG 포트 추가

```
네이버 클라우드 콘솔
→ ACG 설정
→ TCP 3000 포트 추가
```

### 추가 단계 4: 접속

```
http://49.50.134.250:3000
```

---

## 🔧 서버 관리

### 상태 확인

```bash
./check-server.sh
```

### 로그 확인

```bash
# 백엔드
tail -f logs/server.log

# 프론트엔드 (사용 시)
tail -f logs/frontend.log
```

### 서버 중지

```bash
./stop-server.sh
```

### 서버 재시작

```bash
./stop-server.sh
./start-backend-only.sh
```

---

## 📋 모든 스크립트

| 스크립트 | 용도 | 실행 시점 |
|----------|------|-----------|
| `emergency-cleanup.sh` | 디스크 정리 | 디스크 부족 시 |
| `setup-server.sh` | 서버 초기 설정 | 최초 1회 |
| `start-backend-only.sh` | 백엔드만 시작 | 매번 시작 시 ⭐ |
| `start-server.sh` | 백엔드+프론트 시작 | 개발 모드 |
| `rebuild-frontend.sh` | 프론트엔드 빌드 | 프론트 사용 시 |
| `stop-server.sh` | 서버 중지 | 중지 필요 시 |
| `check-server.sh` | 상태 확인 | 문제 발생 시 |
| `change-password.py` | 비밀번호 변경 | 최초 로그인 후 |
| `update-account.py` | 계정 관리 | 고급 설정 |

---

## 🌐 접속 URL

### 백엔드 (필수)

```
http://49.50.134.250:8001       ← API 서버
http://49.50.134.250:8001/docs  ← API 문서 (Swagger) ⭐
```

### 프론트엔드 (선택)

```
http://49.50.134.250:3000       ← 웹 UI
```

---

## 🔐 로그인 정보

**기본 계정:**
```
사용자명: testuser
비밀번호: testpassword123
```

**변경 방법:**
```bash
python3 change-password.py
```

---

## ⚡ 한 줄 명령어

### 백엔드만 (권장)

```bash
./emergency-cleanup.sh && ./setup-server.sh && ./start-backend-only.sh && python3 change-password.py
```

### 프론트엔드 포함

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && \
sudo apt-get install -y nodejs && \
./rebuild-frontend.sh 49.50.134.250
```

---

## ❓ 문제 해결

### 포트 접속 안 됨

**원인:** ACG 설정 안 됨

**해결:**
```
네이버 클라우드 콘솔
→ ACG 설정
→ TCP 8001 (백엔드)
→ TCP 3000 (프론트엔드, 선택)
```

### 로그인 실패

**원인:** 비밀번호 불일치

**해결:**
```bash
python3 change-password.py
```

### 디스크 부족

**원인:** 100% 사용 중

**해결:**
```bash
./emergency-cleanup.sh
```

---

## 🎉 완료!

**백엔드만 사용:**
```
http://49.50.134.250:8001/docs
```

**프론트엔드 포함:**
```
http://49.50.134.250:3000
```

**API 문서에서 모든 기능 사용 가능!** 🚀

