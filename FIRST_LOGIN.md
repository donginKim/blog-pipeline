# 첫 로그인 가이드

Naver Monitor 첫 접속 및 초기 설정 방법입니다.

## 🔐 기본 계정

### 로그인 정보

```
사용자명: testuser
비밀번호: testpassword123
```

또는 (init-db.py로 초기화한 경우):

```
사용자명: admin
비밀번호: admin123
```

---

## 🌐 접속 방법

### 방법 1: API 문서 (Swagger UI)

```
http://49.50.134.250:8001/docs
```

#### 로그인 절차:
1. **POST /api/auth/login** 엔드포인트 클릭
2. **Try it out** 버튼 클릭
3. Request body 입력:
   ```json
   {
     "username": "testuser",
     "password": "testpassword123"
   }
   ```
4. **Execute** 버튼 클릭
5. **access_token** 복사
6. 페이지 상단 **Authorize** 버튼 클릭
7. `Bearer {access_token}` 입력
8. **Authorize** 클릭
9. 이제 모든 API 사용 가능!

---

### 방법 2: 프론트엔드 (Node.js 설치 시)

```
http://49.50.134.250:3000
```

1. 로그인 페이지 자동 표시
2. 사용자명: `testuser`
3. 비밀번호: `testpassword123`
4. **로그인** 버튼 클릭

---

### 방법 3: curl 명령어

```bash
# 로그인하여 토큰 받기
curl -X POST http://49.50.134.250:8001/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"testuser","password":"testpassword123"}'

# 응답:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {...}
}

# 토큰으로 API 호출
curl -H "Authorization: Bearer eyJ..." \
  http://49.50.134.250:8001/api/keywords
```

---

## 🔒 비밀번호 변경 (필수!)

### 보안을 위해 첫 로그인 후 반드시 비밀번호를 변경하세요!

#### 방법 1: CLI (서버에서)

```bash
# 계정 관리 스크립트 실행
python3 update-account.py

# 메뉴:
# 📝 작업 선택:
#   1. 사용자명 변경
#   2. 이메일 변경
#   3. 비밀번호 변경  ← 선택
#   ...

# 선택 (0-6): 3
# 사용자 ID: 1
# 새 비밀번호: ******** (입력 시 화면에 표시 안 됨)
# 비밀번호 확인: ********
# ✅ 비밀번호가 변경되었습니다.
```

---

#### 방법 2: 데이터베이스 직접 수정

```bash
# SQLite로 비밀번호 변경
sqlite3 naver_monitor.db "UPDATE users SET hashed_password = 'new_password_here' WHERE username = 'testuser';"

# 확인
sqlite3 naver_monitor.db "SELECT username, hashed_password FROM users;"
```

---

#### 방법 3: API로 변경 (구현 필요)

현재는 CLI 또는 DB 직접 수정만 가능합니다.

---

## 👥 계정 확인

### 현재 등록된 계정 확인

```bash
# 사용자 목록
sqlite3 naver_monitor.db "SELECT id, username, email, is_active FROM users;"

# 출력 예시:
# 1|testuser|test@example.com|1
```

### 계정 정보

```bash
# 상세 정보
python3 update-account.py

# 📋 현재 등록된 사용자:
# ------------------------------------------------------------
#   ID: 1 | testuser | test@example.com | ✅ 활성
# ------------------------------------------------------------
```

---

## 🎯 첫 사용 체크리스트

### 로그인 후 해야 할 일

- [ ] **비밀번호 변경** (필수!)
  ```bash
  python3 update-account.py
  # 선택: 3 (비밀번호 변경)
  ```

- [ ] **키워드 추가**
  - API 문서 또는 프론트엔드에서 추가
  - 예: "파이썬 강의", "머신러닝"

- [ ] **블로그 추가**
  - 모니터링할 타겟 블로그 등록
  - URL 패턴: `blog.naver.com/myid`

- [ ] **타겟 연결**
  - 키워드 + 블로그 연결

- [ ] **크롤링 테스트**
  - 개별 크롤링 실행
  - 결과 확인

- [ ] **설정 확인**
  - 알림 설정 (SMS)
  - 스케줄 설정 (자동 크롤링)
  - AI 블로그 설정

---

## 🔧 추가 계정 생성

### 팀원 계정 추가

```bash
python3 update-account.py

# 선택 (0-6): 5  ← 새 사용자 생성
# 사용자명: john
# 이메일: john@company.com
# 비밀번호: ********
# 비밀번호 확인: ********
# ✅ 사용자 'john'이 생성되었습니다.
```

---

## 📊 접속 URL 정리

### 백엔드 (필수)

```
http://49.50.134.250:8001       ← API 서버
http://49.50.134.250:8001/docs  ← API 문서 (Swagger UI) ⭐
```

### 프론트엔드 (선택)

```
http://49.50.134.250:3000       ← 웹 UI
```

---

## 💡 빠른 테스트

### API 문서로 모든 기능 테스트

```
http://49.50.134.250:8001/docs
```

**순서:**
1. **POST /api/auth/login** - 로그인하여 토큰 받기
2. **Authorize** - 토큰 입력
3. **GET /api/keywords** - 키워드 목록
4. **POST /api/keywords** - 키워드 추가
5. **POST /api/crawl/trigger** - 크롤링 실행
6. **GET /api/crawl/results** - 결과 확인

---

## 🎉 완료!

**첫 로그인:**
```
1. http://49.50.134.250:8001/docs 접속
2. POST /api/auth/login 실행
3. username: testuser
4. password: testpassword123
5. 토큰 받기
6. Authorize 클릭하여 토큰 입력
```

**비밀번호 변경:**
```bash
python3 update-account.py
# 선택: 3
```

**시작!** 🚀

---

## 📞 도움말

- [NAVER_CLOUD_SETUP.md](NAVER_CLOUD_SETUP.md) - 네이버 클라우드 설정
- [ACCOUNT_MANAGEMENT.md](ACCOUNT_MANAGEMENT.md) - 계정 관리
- [SERVER_SETUP.md](SERVER_SETUP.md) - 서버 설정

---

**기본 계정으로 로그인하고 비밀번호를 변경하세요!** 🔐

