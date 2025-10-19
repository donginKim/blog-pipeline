#!/bin/bash

PUBLIC_IP=${1:-"49.50.134.250"}

echo "🔧 프론트엔드 API URL 수정"
echo "=========================================="
echo ""

# 1. 현재 프론트엔드 설정 확인
echo "1️⃣  현재 프론트엔드 API URL 확인:"
echo "---"
docker exec naver-monitor-frontend cat /usr/share/nginx/html/index.html 2>/dev/null | grep -o "http://[^\"]*:8001" | head -1 || echo "  확인 불가"
echo ""

# 2. .env 파일 확인
echo "2️⃣  .env 파일 확인:"
echo "---"
if [ -f ".env" ]; then
    grep -E "PUBLIC_IP|VITE_API_URL" .env || echo "  설정 없음"
else
    echo "  ❌ .env 파일이 없습니다"
fi
echo ""

# 3. 프론트엔드 재빌드
echo "3️⃣  프론트엔드 재빌드 중..."
echo "---"

# .env 파일 업데이트
if ! grep -q "^VITE_API_URL=" .env 2>/dev/null; then
    echo "VITE_API_URL=http://${PUBLIC_IP}:8001" >> .env
    echo "✅ VITE_API_URL 추가"
else
    sed -i.bak "s|^VITE_API_URL=.*|VITE_API_URL=http://${PUBLIC_IP}:8001|" .env && rm -f .env.bak
    echo "✅ VITE_API_URL 업데이트"
fi

echo ""
echo "🔨 Docker 빌드 중... (5분 소요)"

# 프론트엔드만 재빌드
docker compose -f docker-compose.prod.yml build frontend

if [ $? -eq 0 ]; then
    echo "✅ 빌드 완료"
    echo ""
    echo "🔄 프론트엔드 재시작 중..."
    docker compose -f docker-compose.prod.yml up -d frontend
    echo "✅ 재시작 완료"
else
    echo "❌ 빌드 실패"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 4. 확인
echo "4️⃣  재빌드 후 확인:"
echo "---"
sleep 5

NEW_URL=$(docker exec naver-monitor-frontend cat /usr/share/nginx/html/index.html 2>/dev/null | grep -o "http://[^\"]*:8001" | head -1)
echo "API URL: $NEW_URL"

if echo "$NEW_URL" | grep -q "$PUBLIC_IP"; then
    echo "✅ API URL이 올바르게 설정되었습니다!"
else
    echo "❌ API URL이 여전히 localhost를 가리키고 있습니다."
fi

echo ""
echo "=========================================="
echo "✅ 수정 완료!"
echo "=========================================="
echo ""
echo "🌐 프론트엔드: http://${PUBLIC_IP}:3000"
echo "🔧 API: http://${PUBLIC_IP}:8001"
echo ""
echo "💡 브라우저 캐시를 삭제하고 다시 접속하세요:"
echo "   - Ctrl+Shift+R (Windows/Linux)"
echo "   - Cmd+Shift+R (Mac)"
echo ""

