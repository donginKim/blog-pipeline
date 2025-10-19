# 🚨 긴급 수정 - localhost:8001 문제

## 문제
프론트엔드가 계속 `localhost:8001`을 호출

## ⚡ 즉시 해결 (서버에서)

### 1단계: 완전히 새로 빌드
```bash
# 기존 제거
docker compose -f docker-compose.prod.yml stop frontend
docker compose -f docker-compose.prod.yml rm -f frontend
docker rmi naver-monitor-frontend

# 캐시 없이 재빌드
docker compose -f docker-compose.prod.yml build --no-cache frontend

# 시작
docker compose -f docker-compose.prod.yml up -d frontend
```

### 2단계: 브라우저에서 (중요!)
```
1. Ctrl + Shift + R (하드 리프레시)
2. 또는 시크릿 모드로 접속
```

---

## 🔍 확인

개발자 도구(F12) → Network 탭에서:

✅ **정상**: `POST /api/settings/notifications`
❌ **비정상**: `POST http://localhost:8001/api/...`

---

## 💡 왜 계속 localhost가 나오나요?

**이유**: 이미 빌드된 프론트엔드 컨테이너가 실행 중
- 코드를 수정해도 빌드를 다시 해야 반영됨
- 브라우저 캐시에도 이전 코드가 저장됨

**해결**: 위 명령어로 완전히 재빌드

---

## 🚀 자동화 스크립트 (더 쉬움)

```bash
./fix-all-now.sh 49.50.134.250
```

이 스크립트가 자동으로:
1. 기존 컨테이너/이미지 삭제
2. 캐시 없이 재빌드
3. 재시작
4. 확인

---

## ⏰ 예상 소요 시간
- 빌드: 5-10분
- 브라우저 캐시 삭제: 1초

---

**지금 바로 서버에서 실행하세요!**

