# 계정 관리 가이드

Naver Monitor 시스템의 사용자 계정 관리 방법을 안내합니다.

## 목차

- [개요](#개요)
- [계정 관리 스크립트](#계정-관리-스크립트)
- [주요 기능](#주요-기능)
- [사용 방법](#사용-방법)
- [직접 데이터베이스 조작](#직접-데이터베이스-조작)
- [문제 해결](#문제-해결)

---

## 개요

Naver Monitor는 간단한 인증 시스템을 사용합니다:
- **회원가입 기능 없음**: 관리자가 직접 계정을 생성
- **평문 비밀번호**: 단순성을 위해 평문으로 저장 (내부 사용 권장)
- **다중 사용자**: 여러 계정 생성 가능

### 보안 고려사항

⚠️ **주의**: 이 시스템은 내부망/개인 사용을 위해 설계되었습니다.
- 비밀번호가 평문으로 저장됨
- 외부 인터넷에 노출하지 마세요
- VPN이나 방화벽 뒤에서 사용 권장

---

## 계정 관리 스크립트

### 실행 방법

```bash
python3 update-account.py
```

### 스크립트 기능 메뉴

```
============================================================
🔧 Naver Monitor - 계정 관리
============================================================

📋 현재 등록된 사용자:
------------------------------------------------------------
  ID: 1 | testuser | test@example.com | ✅ 활성
------------------------------------------------------------

📝 작업 선택:
  1. 사용자명 변경
  2. 이메일 변경
  3. 비밀번호 변경
  4. 계정 활성화/비활성화
  5. 새 사용자 생성
  6. 사용자 삭제
  0. 종료

선택 (0-6):
```

---

## 주요 기능

### 1. 사용자명 변경

기존 사용자의 로그인 ID를 변경합니다.

**절차:**
```bash
선택: 1
사용자 ID: 1
새 사용자명: admin
```

**주의사항:**
- 중복된 사용자명 불가
- 빈 값 불가
- 변경 즉시 적용 (서버 재시작 불필요)

---

### 2. 이메일 변경

사용자의 이메일 주소를 변경합니다.

**절차:**
```bash
선택: 2
사용자 ID: 1
새 이메일: admin@example.com
```

**주의사항:**
- 이메일 형식 검증 없음
- 알림 기능에서 사용 예정 (현재 미사용)

---

### 3. 비밀번호 변경 ⭐

가장 많이 사용하는 기능입니다.

**절차:**
```bash
선택: 3
사용자 ID: 1
새 비밀번호: ******** (입력 시 화면에 표시 안 됨)
비밀번호 확인: ******** (입력 시 화면에 표시 안 됨)
✅ 비밀번호가 변경되었습니다.
```

**보안 기능:**
- 입력 시 화면에 표시 안 됨 (`getpass` 사용)
- 비밀번호 확인으로 오타 방지
- 빈 비밀번호 불가

**즉시 적용:**
- 변경 후 바로 새 비밀번호로 로그인 가능
- 기존 로그인 세션은 유지됨

---

### 4. 계정 활성화/비활성화

계정을 일시적으로 비활성화하거나 다시 활성화합니다.

**절차:**
```bash
선택: 4
사용자 ID: 1
✅ 계정이 비활성화되었습니다.
```

**효과:**
- **비활성화**: 로그인 불가 (데이터는 유지)
- **활성화**: 다시 로그인 가능

**사용 시나리오:**
- 임시로 접근 차단
- 퇴사자 계정 일시 정지
- 다시 활성화로 복구 가능

---

### 5. 새 사용자 생성 ⭐

추가 사용자 계정을 생성합니다.

**절차:**
```bash
선택: 5

🆕 새 사용자 생성
------------------------------------------------------------
사용자명: john
이메일: john@example.com
비밀번호: ********
비밀번호 확인: ********
✅ 사용자 'john'이 생성되었습니다.
```

**필수 정보:**
- 사용자명 (로그인 ID)
- 이메일
- 비밀번호

**기본 설정:**
- 계정 활성화 상태로 생성
- 바로 로그인 가능

---

### 6. 사용자 삭제

계정을 완전히 삭제합니다.

**절차:**
```bash
선택: 6
사용자 ID: 2

⚠️  정말로 사용자 'john'을 삭제하시겠습니까? (yes/no): yes
✅ 사용자 'john'이 삭제되었습니다.
```

**주의사항:**
- ⚠️ **복구 불가**: 삭제된 계정은 복구할 수 없음
- 키워드/블로그/타겟 데이터는 유지됨
- 확인 절차 필수 (`yes` 입력)

**권장 사항:**
- 삭제 대신 비활성화 권장
- 완전히 삭제가 필요한 경우만 사용

---

## 사용 방법

### 기본 사용 흐름

1. **스크립트 실행**
   ```bash
   cd /Users/amiro/Workshop/naver-monitor
   python3 update-account.py
   ```

2. **현재 사용자 목록 확인**
   - 자동으로 표시됨

3. **작업 선택**
   - 숫자 입력 (0-6)

4. **대상 사용자 선택**
   - 사용자 ID 입력

5. **정보 입력**
   - 새로운 값 입력

6. **완료**
   - 성공 메시지 확인

### 예제 시나리오

#### 예제 1: 초기 비밀번호 변경

```bash
$ python3 update-account.py

선택 (0-6): 3
사용자 ID: 1
새 비밀번호: MySecurePass123!
비밀번호 확인: MySecurePass123!
✅ 비밀번호가 변경되었습니다.
```

#### 예제 2: 팀원 계정 추가

```bash
$ python3 update-account.py

선택 (0-6): 5
사용자명: developer
이메일: dev@company.com
비밀번호: DevPass123
비밀번호 확인: DevPass123
✅ 사용자 'developer'이 생성되었습니다.
```

#### 예제 3: 퇴사자 계정 비활성화

```bash
$ python3 update-account.py

선택 (0-6): 4
사용자 ID: 3
✅ 계정이 비활성화되었습니다.
```

---

## 직접 데이터베이스 조작

### 사용자 목록 조회

```bash
sqlite3 naver_monitor.db "SELECT id, username, email, is_active FROM users;"
```

**출력 예시:**
```
1|testuser|test@example.com|1
2|admin|admin@example.com|1
3|john|john@example.com|0
```

### 비밀번호 직접 변경

```bash
sqlite3 naver_monitor.db "UPDATE users SET hashed_password = 'newpassword' WHERE username = 'testuser';"
```

⚠️ **주의**: 열 이름이 `hashed_password`이지만 실제로는 평문이 저장됩니다.

### 새 사용자 생성

```bash
sqlite3 naver_monitor.db "INSERT INTO users (username, email, hashed_password, is_active) VALUES ('newuser', 'new@example.com', 'password123', 1);"
```

### 계정 활성화/비활성화

```bash
# 비활성화
sqlite3 naver_monitor.db "UPDATE users SET is_active = 0 WHERE username = 'testuser';"

# 활성화
sqlite3 naver_monitor.db "UPDATE users SET is_active = 1 WHERE username = 'testuser';"
```

### 사용자 삭제

```bash
sqlite3 naver_monitor.db "DELETE FROM users WHERE username = 'testuser';"
```

---

## 문제 해결

### Q1: 로그인이 안 돼요

**확인 사항:**
1. 사용자명이 정확한가?
   ```bash
   sqlite3 naver_monitor.db "SELECT username FROM users WHERE is_active = 1;"
   ```

2. 계정이 활성화되어 있나?
   ```bash
   sqlite3 naver_monitor.db "SELECT username, is_active FROM users WHERE username = 'testuser';"
   ```

3. 비밀번호가 정확한가?
   ```bash
   sqlite3 naver_monitor.db "SELECT hashed_password FROM users WHERE username = 'testuser';"
   ```

**해결:**
```bash
python3 update-account.py
# 선택: 3 (비밀번호 변경)
# 또는
# 선택: 4 (계정 활성화)
```

---

### Q2: 비밀번호를 잊어버렸어요

**해결 방법 1: 스크립트 사용**
```bash
python3 update-account.py
# 선택: 3 (비밀번호 변경)
```

**해결 방법 2: 데이터베이스 직접 수정**
```bash
sqlite3 naver_monitor.db "UPDATE users SET hashed_password = 'newpassword' WHERE username = 'testuser';"
```

**해결 방법 3: 초기화 스크립트 실행**
```bash
python3 init-db.py
```
⚠️ 주의: 모든 데이터가 초기화됩니다!

---

### Q3: 스크립트 실행이 안 돼요

**오류: `ModuleNotFoundError`**
```bash
# 가상환경 활성화
source venv/bin/activate

# 다시 실행
python3 update-account.py
```

**오류: `no such table: users`**
```bash
# 데이터베이스 초기화
python3 init-db.py
```

**오류: `Permission denied`**
```bash
# 실행 권한 부여
chmod +x update-account.py
```

---

### Q4: 여러 사람이 동시에 사용할 수 있나요?

**네, 가능합니다.**

1. **각 사용자마다 계정 생성**
   ```bash
   python3 update-account.py
   # 선택: 5 (새 사용자 생성)
   ```

2. **각자의 계정으로 로그인**
   - 데이터는 모두 공유됨
   - 동시 접속 가능

**주의:**
- 모든 사용자가 모든 데이터를 볼 수 있음
- 권한 분리 기능 없음 (모두 관리자)

---

### Q5: 계정을 백업하고 싶어요

**데이터베이스 백업:**
```bash
# 전체 백업
cp naver_monitor.db naver_monitor.db.backup

# 사용자만 백업
sqlite3 naver_monitor.db ".dump users" > users_backup.sql
```

**복원:**
```bash
# 전체 복원
cp naver_monitor.db.backup naver_monitor.db

# 사용자만 복원
sqlite3 naver_monitor.db < users_backup.sql
```

---

## 보안 권장사항

### ✅ 권장 사항

1. **강력한 비밀번호 사용**
   - 최소 8자 이상
   - 대소문자, 숫자, 특수문자 조합

2. **정기적 비밀번호 변경**
   - 3-6개월마다 변경 권장

3. **사용하지 않는 계정 비활성화**
   - 삭제 대신 비활성화 권장

4. **내부망에서만 사용**
   - VPN 또는 방화벽 뒤에서 운영
   - 외부 인터넷 노출 금지

### ❌ 피해야 할 사항

1. **쉬운 비밀번호 사용**
   - `123456`, `password`, `admin` 등

2. **비밀번호 공유**
   - 각 사용자마다 별도 계정 생성

3. **퇴사자 계정 방치**
   - 즉시 비활성화 또는 삭제

4. **공용 비밀번호 사용**
   - 모든 계정에 다른 비밀번호

---

## 데이터베이스 스키마

### users 테이블 구조

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    hashed_password TEXT NOT NULL,  -- 실제로는 평문
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | INTEGER | 고유 식별자 (자동 증가) |
| `username` | TEXT | 로그인 ID (중복 불가) |
| `email` | TEXT | 이메일 주소 |
| `hashed_password` | TEXT | 비밀번호 (평문 저장) |
| `is_active` | INTEGER | 활성화 상태 (1: 활성, 0: 비활성) |
| `created_at` | TIMESTAMP | 생성 시간 (자동) |

---

## 빠른 참조

### 자주 사용하는 명령어

```bash
# 계정 관리 스크립트 실행
python3 update-account.py

# 사용자 목록 확인
sqlite3 naver_monitor.db "SELECT id, username, email, is_active FROM users;"

# 비밀번호 직접 변경
sqlite3 naver_monitor.db "UPDATE users SET hashed_password = 'newpass' WHERE username = 'testuser';"

# 계정 활성화
sqlite3 naver_monitor.db "UPDATE users SET is_active = 1 WHERE username = 'testuser';"

# 계정 비활성화
sqlite3 naver_monitor.db "UPDATE users SET is_active = 0 WHERE username = 'testuser';"

# 데이터베이스 백업
cp naver_monitor.db naver_monitor.db.backup
```

---

## 관련 문서

- [README.md](README.md) - 프로젝트 전체 가이드
- [start-test.sh](start-test.sh) - 로컬 테스트 환경 시작
- [init-db.py](init-db.py) - 데이터베이스 초기화

---

## 문의 및 지원

문제가 발생하거나 추가 기능이 필요한 경우:
1. 데이터베이스 백업 생성
2. 오류 메시지 기록
3. 관리자에게 문의

---

**마지막 업데이트:** 2025-10-10  
**버전:** 1.0.0


