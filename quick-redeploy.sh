#!/bin/bash

PUBLIC_IP=${1:-"49.50.134.250"}

echo "🚀 빠른 재배포"
echo "=========================================="
echo ""

# 백엔드만 재시작
echo "🔄 백엔드 재시작 중..."

docker compose -f docker-compose.prod.yml restart backend

echo ""
echo "⏳ 재시작 대기 중..."
sleep 5

echo ""
echo "✅ 재시작 완료!"
echo ""

# 로그 확인
echo "📋 최근 로그:"
echo "---"
docker logs --tail 20 naver-monitor-backend

echo ""
echo "=========================================="
echo ""
echo "🔍 로그인 테스트:"
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpassword123"}' \
  http://${PUBLIC_IP}:8001/api/auth/login)

if echo "$RESPONSE" | grep -q "access_token"; then
  echo "✅ 로그인 성공!"
else
  echo "❌ 로그인 실패"
  echo "$RESPONSE"
fi

echo ""
echo "🌐 접속 URL:"
echo "   http://${PUBLIC_IP}:3000"
echo "   http://${PUBLIC_IP}:8001/docs"
echo ""

