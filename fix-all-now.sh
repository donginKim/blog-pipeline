#!/bin/bash

PUBLIC_IP=${1:-"49.50.134.250"}

echo "🚀 완전 수정 (올인원)"
echo "=========================================="
echo ""
echo "📝 수정 내용:"
echo "  1. api.ts → 상대 경로 (/api) 강제"
echo "  2. nginx.conf → API 프록시 추가"
echo "  3. docker-compose.prod.yml → VITE_API_URL 제거"
echo "  4. 프론트엔드 완전히 새로 빌드"
echo ""

read -p "계속하시겠습니까? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "취소됨"
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. 기존 프론트엔드 정리
echo "1️⃣  기존 프론트엔드 정리..."
docker compose -f docker-compose.prod.yml stop frontend
docker compose -f docker-compose.prod.yml rm -f frontend
docker rmi naver-monitor-frontend 2>/dev/null || true
echo "✅ 정리 완료"
echo ""

# 2. .env 정리
echo "2️⃣  환경 변수 정리..."
if [ -f ".env" ]; then
    # VITE_API_URL 제거
    sed -i.bak '/^VITE_API_URL=/d' .env && rm -f .env.bak
    echo "✅ VITE_API_URL 제거"
fi
echo ""

# 3. 완전히 새로 빌드
echo "3️⃣  프론트엔드 재빌드 (캐시 없이)..."
echo "---"
echo "⏳ 빌드 중... (5-10분 소요)"
echo ""

docker compose -f docker-compose.prod.yml build --no-cache frontend

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 빌드 실패"
    exit 1
fi

echo ""
echo "✅ 빌드 성공"
echo ""

# 4. 시작
echo "4️⃣  프론트엔드 시작..."
docker compose -f docker-compose.prod.yml up -d frontend

echo ""
echo "⏳ 서비스 시작 대기 중..."
sleep 8

# 5. 확인
echo ""
echo "5️⃣  빌드 결과 확인:"
echo "---"

echo "📦 Nginx 설정:"
docker exec naver-monitor-frontend cat /etc/nginx/conf.d/default.conf | grep -A 5 "location /api"

echo ""
echo "🔍 JavaScript 번들 확인:"
JS_FILE=$(docker exec naver-monitor-frontend ls /usr/share/nginx/html/assets/*.js 2>/dev/null | head -1)
if [ -n "$JS_FILE" ]; then
    docker exec naver-monitor-frontend grep -o "baseURL[^,]*" "$JS_FILE" | head -1
else
    echo "  (JS 파일 확인 불가)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ 모든 수정 완료!"
echo "=========================================="
echo ""
echo "🌐 접속 URL:"
echo "   http://${PUBLIC_IP}:3000"
echo ""
echo "⚠️  매우 중요: 브라우저 캐시를 삭제하세요!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   캐시 삭제 방법:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   1️⃣  Hard Refresh (가장 쉬움)"
echo "      - Windows/Linux: Ctrl + Shift + R"
echo "      - Mac: Cmd + Shift + R"
echo ""
echo "   2️⃣  개발자 도구 (확실함)"
echo "      - F12 (개발자 도구 열기)"
echo "      - Network 탭 선택"
echo "      - 'Disable cache' 체크"
echo "      - 페이지 새로고침"
echo ""
echo "   3️⃣  시크릿/비공개 모드 (완전 새로)"
echo "      - Chrome: Ctrl + Shift + N"
echo "      - Firefox: Ctrl + Shift + P"
echo "      - Safari: Cmd + Shift + N"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔍 설정 저장 테스트:"
echo "   1. http://${PUBLIC_IP}:3000 접속"
echo "   2. 로그인"
echo "   3. 설정 페이지"
echo "   4. F12 → Network 탭 열기"
echo "   5. 설정 저장 버튼 클릭"
echo "   6. Network 탭에서 확인:"
echo ""
echo "      ✅ 올바른 요청:"
echo "         POST /api/settings/notifications"
echo "         Status: 200 OK"
echo ""
echo "      ❌ 잘못된 요청 (더 이상 나오면 안 됨):"
echo "         POST http://localhost:8001/api/..."
echo "         Status: ERR_CONNECTION_REFUSED"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

