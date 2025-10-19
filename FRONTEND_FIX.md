# 프론트엔드 API 연결 문제 해결

## 🚨 문제

프론트엔드에서 설정 저장 시 다음 오류 발생:

```
POST http://localhost:8001/api/settings/notifications net::ERR_CONNECTION_REFUSED
설정 저장 오류: TypeError: Failed to fetch
```

### 원인

Docker 환경에서 프론트엔드가 빌드될 때 `localhost:8001`로 하드코딩되어, 실제 백엔드에 연결할 수 없음.

---

## ✅ 해결 방법

### 🔧 자동 수정 (권장) ⭐

**서버에서 실행:**
```bash
./quick-fix-frontend.sh 49.50.134.250
```

---

## 🔍 수정 내용

### 1. Nginx API 프록시 추가

**`frontend/nginx.conf`에 추가:**

```nginx
# API 프록시 (백엔드로 전달)
location /api/ {
    proxy_pass http://backend:8001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
}
```

**동작 방식:**
- 프론트엔드: `/api/settings/notifications` 호출
- Nginx: `http://backend:8001/api/settings/notifications`로 프록시
- Docker 내부 네트워크로 백엔드 접근

---

### 2. 프론트엔드 API 클라이언트 수정

**`frontend/src/services/api.ts` 변경:**

**변경 전:**
```typescript
const apiUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8001';
```

**변경 후:**
```typescript
const apiUrl = (import.meta as any).env?.VITE_API_URL || 
               (import.meta.env.MODE === 'production' ? '' : 'http://localhost:8001');
```

**동작:**
- **로컬 개발**: `http://localhost:8001/api/...`
- **프로덕션**: `/api/...` (상대 경로, Nginx가 프록시)

---

## 🚀 적용 방법

### 방법 1: 빠른 수정 스크립트

```bash
# 서버에서
./quick-fix-frontend.sh 49.50.134.250
```

### 방법 2: 수동 재배포

```bash
# 1. 코드 업로드/pull
# git pull

# 2. 프론트엔드만 재빌드
docker compose -f docker-compose.prod.yml build frontend

# 3. 재시작
docker compose -f docker-compose.prod.yml up -d frontend
```

### 방법 3: 전체 재배포

```bash
./deploy-docker.sh 49.50.134.250
```

---

## 🔍 확인 방법

### 브라우저 개발자 도구

1. **F12** 또는 **Cmd+Option+I** (Mac)
2. **Network** 탭 선택
3. 설정 페이지에서 저장 버튼 클릭
4. API 요청 확인:

**수정 전:**
```
❌ POST http://localhost:8001/api/settings/notifications
   Status: (failed) net::ERR_CONNECTION_REFUSED
```

**수정 후:**
```
✅ POST /api/settings/notifications
   Status: 200 OK
```

---

## 📋 네트워크 구조

### 수정 전

```
브라우저 (49.50.134.250:3000)
  ↓
  ❌ localhost:8001 (연결 불가)
```

### 수정 후

```
브라우저 (49.50.134.250:3000)
  ↓
  /api/... (상대 경로)
  ↓
Nginx (프론트엔드 컨테이너)
  ↓
  http://backend:8001 (Docker 내부 네트워크)
  ↓
Backend (백엔드 컨테이너)
  ↓
  ✅ 200 OK
```

---

## 💡 장점

1. **IP 변경 불필요**
   - 프론트엔드 재빌드 없이 서버 이동 가능

2. **CORS 문제 없음**
   - 같은 origin에서 요청 (Same-Origin)

3. **보안 향상**
   - 백엔드 포트(8001)를 외부에 노출 안 해도 됨

4. **로컬 개발 유지**
   - `npm run dev` 시 여전히 `localhost:8001` 사용

---

## 🔧 브라우저 캐시 삭제

수정 후에도 문제가 있다면 캐시 삭제:

**Windows/Linux:**
```
Ctrl + Shift + R
```

**Mac:**
```
Cmd + Shift + R
```

또는 개발자 도구에서:
1. **Network** 탭
2. **Disable cache** 체크
3. 새로고침

---

## ✅ 예상 결과

**설정 저장 성공:**
```json
{
  "message": "설정이 저장되었습니다",
  "settings": {
    "enabled": true,
    "phone_number": "01012345678",
    ...
  }
}
```

**브라우저 알림:**
```
✅ 설정이 저장되었습니다
```

---

## 📚 관련 파일

- `frontend/nginx.conf` - Nginx 설정
- `frontend/src/services/api.ts` - API 클라이언트
- `quick-fix-frontend.sh` - 자동 수정 스크립트
- `docker-compose.prod.yml` - Docker 설정

---

**서버에서 `./quick-fix-frontend.sh 49.50.134.250` 실행하면 문제가 해결됩니다!** 🎉

