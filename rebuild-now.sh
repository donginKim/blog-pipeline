#!/bin/bash
# 가장 간단한 재빌드 스크립트

echo "🔄 프론트엔드 즉시 재빌드"
echo ""

# 기존 제거
echo "1. 기존 제거..."
docker compose -f docker-compose.prod.yml stop frontend
docker compose -f docker-compose.prod.yml rm -f frontend
docker rmi naver-monitor-frontend 2>/dev/null

# 재빌드
echo ""
echo "2. 재빌드 중... (5-10분)"
docker compose -f docker-compose.prod.yml build --no-cache frontend

# 시작
echo ""
echo "3. 시작..."
docker compose -f docker-compose.prod.yml up -d frontend

echo ""
echo "✅ 완료!"
echo ""
echo "⚠️  브라우저에서 Ctrl+Shift+R 누르세요!"

