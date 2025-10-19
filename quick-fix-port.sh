#!/bin/bash
# 빠른 포트 정리 및 재배포

echo "🗑️  기존 서비스 정리 중..."

# Docker 컨테이너 정리
docker compose -f docker-compose.prod.yml down 2>/dev/null

# 수동 실행 중인 프로세스 정리
echo "🔌 포트 정리 중..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:5432 | xargs kill -9 2>/dev/null || true

# 잠시 대기
sleep 2

echo ""
echo "✅ 정리 완료!"
echo ""

# 배포
if [ -n "$1" ]; then
  echo "🚀 배포 시작: $1"
  ./deploy-docker.sh "$1"
else
  echo "📋 사용법: ./quick-fix-port.sh <PUBLIC_IP>"
  echo "   예시: ./quick-fix-port.sh 49.50.134.250"
fi

