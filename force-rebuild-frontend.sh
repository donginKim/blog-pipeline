#!/bin/bash

PUBLIC_IP=${1:-"49.50.134.250"}

echo "🔥 프론트엔드 강제 재빌드"
echo "=========================================="
echo ""

# 1. 기존 컨테이너 및 이미지 제거
echo "1️⃣  기존 프론트엔드 정리..."
echo "---"

docker stop naver-monitor-frontend 2>/dev/null
docker rm naver-monitor-frontend 2>/dev/null
docker rmi naver-monitor-frontend 2>/dev/null

echo "✅ 정리 완료"
echo ""

# 2. 빌드 캐시 없이 완전히 새로 빌드
echo "2️⃣  캐시 없이 새로 빌드..."
echo "---"

# .env 파일에서 VITE_API_URL 제거 (상대 경로 강제)
if [ -f ".env" ]; then
    sed -i.bak '/^VITE_API_URL=/d' .env && rm -f .env.bak
    echo "✅ VITE_API_URL 제거 (상대 경로 사용)"
fi

echo ""
echo "🔨 Docker 빌드 중... (5-10분 소요)"
echo ""

docker compose -f docker-compose.prod.yml build --no-cache frontend 2>&1 | tee /tmp/frontend-rebuild.log

BUILD_EXIT_CODE=${PIPESTATUS[0]}

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ 빌드 성공!"
    echo ""
    
    # 3. 컨테이너 시작
    echo "3️⃣  컨테이너 시작..."
    docker compose -f docker-compose.prod.yml up -d frontend
    
    echo ""
    echo "⏳ 서비스 시작 대기 중..."
    sleep 8
    
    # 4. 빌드된 파일 확인
    echo ""
    echo "4️⃣  빌드된 파일 확인:"
    echo "---"
    
    echo "📦 컨테이너 내부 파일:"
    docker exec naver-monitor-frontend ls -la /usr/share/nginx/html/ | head -10
    
    echo ""
    echo "🔍 API URL 확인:"
    docker exec naver-monitor-frontend grep -o "baseURL[^,]*" /usr/share/nginx/html/assets/*.js 2>/dev/null | head -3 || echo "  (확인 불가)"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "✅ 완료!"
    echo "=========================================="
    echo ""
    echo "🌐 접속 URL:"
    echo "   http://${PUBLIC_IP}:3000"
    echo ""
    echo "⚠️  중요: 브라우저 캐시를 반드시 삭제하세요!"
    echo ""
    echo "   방법 1: Hard Refresh"
    echo "     - Windows/Linux: Ctrl + Shift + R"
    echo "     - Mac: Cmd + Shift + R"
    echo ""
    echo "   방법 2: 개발자 도구"
    echo "     - F12 → Network 탭"
    echo "     - 'Disable cache' 체크"
    echo "     - 새로고침"
    echo ""
    echo "   방법 3: 시크릿 모드"
    echo "     - Ctrl + Shift + N (Chrome)"
    echo "     - Ctrl + Shift + P (Firefox)"
    echo ""
    echo "🔍 API 요청 확인:"
    echo "   개발자 도구 → Network 탭에서"
    echo "   /api/settings/notifications 확인"
    echo "   (localhost:8001이 아닌 상대 경로)"
    echo ""
else
    echo ""
    echo "❌ 빌드 실패 (exit code: $BUILD_EXIT_CODE)"
    echo ""
    echo "📋 오류 로그:"
    tail -50 /tmp/frontend-rebuild.log
    echo ""
    exit 1
fi

