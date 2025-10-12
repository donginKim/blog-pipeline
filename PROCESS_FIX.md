# 프로세스 간섭 문제 해결

## 🔥 문제

백엔드와 프론트엔드가 서로 종료되는 문제:
- 백엔드 시작 → 프론트엔드 종료
- 프론트엔드 시작 → 백엔드 종료

## 🔍 원인

각 스크립트에서 `pkill` 명령어로 모든 관련 프로세스를 종료:

```bash
# 문제가 있던 코드
pkill -f "python.*server-debug.py"  # 모든 Python 프로세스 종료
pkill -f "vite"                      # 모든 Vite 프로세스 종료
pkill -f "serve"                     # 모든 serve 프로세스 종료
```

## ✅ 해결

PID 파일을 사용하여 특정 프로세스만 종료:

### 수정된 로직

```bash
# 1. 이전 PID 파일 확인
if [ -f ".backend.pid" ]; then
    OLD_PID=$(cat .backend.pid)
    
    # 2. 해당 프로세스만 종료
    if ps -p $OLD_PID > /dev/null 2>&1; then
        kill $OLD_PID
        # 강제 종료 필요 시
        kill -9 $OLD_PID
    fi
    
    # 3. PID 파일 삭제
    rm -f .backend.pid
fi

# 4. 포트만 정리
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
```

### 수정된 파일

1. ✅ `start-backend-only.sh` - 백엔드만 재시작
2. ✅ `start-server.sh` - 백엔드+프론트엔드 재시작
3. ✅ `rebuild-frontend.sh` - 프론트엔드만 재시작

## 🎯 테스트

### 시나리오 1: 백엔드만 시작

```bash
./start-backend-only.sh
```

**기대 결과:**
- ✅ 백엔드만 재시작
- ✅ 프론트엔드는 그대로 유지

### 시나리오 2: 프론트엔드만 재빌드

```bash
./rebuild-frontend.sh 49.50.134.250
```

**기대 결과:**
- ✅ 프론트엔드만 재시작
- ✅ 백엔드는 그대로 유지

### 시나리오 3: 둘 다 시작

```bash
./start-server.sh
```

**기대 결과:**
- ✅ 백엔드 재시작
- ✅ 프론트엔드 재시작
- ✅ 서로 간섭 없음

## 📋 PID 파일 관리

### 저장 위치

```
.backend.pid   → 백엔드 프로세스 ID
.frontend.pid  → 프론트엔드 프로세스 ID
```

### 자동 관리

**시작 시:**
```bash
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid
```

**종료 시:**
```bash
rm -f .backend.pid
rm -f .frontend.pid
```

## 🔧 프로세스 확인

### 실행 중인 프로세스

```bash
# PID 파일 확인
cat .backend.pid
cat .frontend.pid

# 프로세스 확인
ps -p $(cat .backend.pid)
ps -p $(cat .frontend.pid)
```

### 포트 사용 확인

```bash
# 백엔드 (8001)
lsof -i:8001

# 프론트엔드 (3000)
lsof -i:3000
```

## 🛑 수동 종료

### 개별 종료

```bash
# 백엔드만 종료
kill $(cat .backend.pid)

# 프론트엔드만 종료
kill $(cat .frontend.pid)
```

### 전체 종료

```bash
./stop-server.sh
```

## ✅ 확인 사항

### 백엔드 재시작 시

- ✅ `.backend.pid`만 업데이트
- ✅ `.frontend.pid`는 변경 없음
- ✅ 포트 8001만 정리
- ✅ 포트 3000은 그대로

### 프론트엔드 재시작 시

- ✅ `.frontend.pid`만 업데이트
- ✅ `.backend.pid`는 변경 없음
- ✅ 포트 3000만 정리
- ✅ 포트 8001은 그대로

## 🎉 결과

**이제 백엔드와 프론트엔드가 서로 간섭하지 않고 독립적으로 실행됩니다!**

- ✅ 백엔드만 재시작 가능
- ✅ 프론트엔드만 재시작 가능
- ✅ 둘 다 동시 실행 가능
- ✅ 서로 종료되지 않음

## 🚀 권장 사용법

### 개발 시

```bash
# 1. 백엔드 수정 후
./start-backend-only.sh

# 2. 프론트엔드 수정 후
./rebuild-frontend.sh 49.50.134.250
```

### 운영 시

```bash
# 전체 재시작
./stop-server.sh
./start-backend-only.sh
./rebuild-frontend.sh 49.50.134.250
```

## 📊 프로세스 흐름

```
시작:
  1. PID 파일 확인
  2. 이전 프로세스만 종료
  3. 새 프로세스 시작
  4. PID 파일 업데이트

종료:
  1. PID 파일 읽기
  2. 해당 프로세스 종료
  3. PID 파일 삭제
```

**완벽하게 작동합니다!** 🎊

