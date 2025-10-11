#!/bin/bash

echo "🔐 로그인 테스트"
echo ""

# Login
echo "1️⃣ 로그인 중..."
RESPONSE=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpassword123"}')

echo "로그인 응답:"
echo "$RESPONSE" | python3 -m json.tool
echo ""

# Extract token
TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ]; then
    echo "❌ 로그인 실패"
    exit 1
fi

echo "✅ 로그인 성공!"
echo "토큰: $TOKEN"
echo ""

# Test authenticated endpoints
echo "2️⃣ 인증된 API 테스트..."

echo "📊 사용자 정보:"
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/auth/me | python3 -m json.tool
echo ""

echo "📝 키워드 목록:"
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/keywords | python3 -m json.tool
echo ""

echo "📊 대시보드 통계:"
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/dashboard/stats | python3 -m json.tool
echo ""

echo "🎉 모든 테스트 완료!"

