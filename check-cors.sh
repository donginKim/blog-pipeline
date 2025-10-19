#!/bin/bash

PUBLIC_IP=${1:-"49.50.134.250"}

echo "🔍 CORS 설정 확인"
echo "=========================================="
echo ""

# 1. 환경 변수 확인
echo "1️⃣  환경 변수 (.env):"
echo "---"
if [ -f ".env" ]; then
    grep -E "PUBLIC_IP|CORS_ORIGINS" .env || echo "  (설정 없음)"
else
    echo "  ❌ .env 파일이 없습니다"
fi
echo ""

# 2. 백엔드 로그 확인
echo "2️⃣  백엔드 CORS 로그:"
echo "---"
docker logs naver-monitor-backend 2>&1 | grep "CORS" | tail -5 || echo "  (로그 없음)"
echo ""

# 3. OPTIONS 요청 테스트
echo "3️⃣  CORS Preflight 테스트:"
echo "---"
curl -X OPTIONS \
  -H "Origin: http://${PUBLIC_IP}:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v \
  http://${PUBLIC_IP}:8001/api/auth/login 2>&1 | grep -E "< HTTP|< Access-Control|< Allow"
echo ""

# 4. 실제 로그인 요청 테스트
echo "4️⃣  로그인 API 테스트:"
echo "---"
curl -X POST \
  -H "Origin: http://${PUBLIC_IP}:3000" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpassword123"}' \
  -v \
  http://${PUBLIC_IP}:8001/api/auth/login 2>&1 | grep -E "< HTTP|< Access-Control"
echo ""

echo "=========================================="
echo ""
echo "💡 문제 해결 방법:"
echo ""
echo "1. .env 파일에 PUBLIC_IP 설정:"
echo "   echo 'PUBLIC_IP=${PUBLIC_IP}' >> .env"
echo ""
echo "2. CORS_ORIGINS 설정:"
echo "   echo 'CORS_ORIGINS=http://${PUBLIC_IP}:3000,http://localhost:3000' >> .env"
echo ""
echo "3. 컨테이너 재시작:"
echo "   docker compose -f docker-compose.prod.yml restart backend"
echo ""
echo "4. 전체 재배포:"
echo "   ./deploy-docker.sh ${PUBLIC_IP}"
echo ""

