#!/bin/bash

echo "🔍 포트 8001 사용 중인 프로세스 확인..."

# Docker 컨테이너 확인
echo ""
echo "📦 Docker 컨테이너:"
docker ps -a | grep naver-monitor || echo "  (없음)"

# 포트 사용 프로세스 확인
echo ""
echo "🔌 포트 8001 사용 프로세스:"
lsof -i:8001 || echo "  (없음)"

# 정리 옵션 제공
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "정리 옵션을 선택하세요:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  Docker 컨테이너만 정리"
echo "2️⃣  포트 8001 프로세스만 정리"
echo "3️⃣  둘 다 정리 (권장)"
echo "4️⃣  취소"
echo ""
read -p "선택 (1-4): " choice

case $choice in
  1)
    echo ""
    echo "🗑️  Docker 컨테이너 정리 중..."
    docker stop naver-monitor-backend 2>/dev/null
    docker rm naver-monitor-backend 2>/dev/null
    docker stop naver-monitor-db 2>/dev/null
    docker rm naver-monitor-db 2>/dev/null
    docker stop naver-monitor-frontend 2>/dev/null
    docker rm naver-monitor-frontend 2>/dev/null
    echo "✅ Docker 컨테이너 정리 완료"
    ;;
  2)
    echo ""
    echo "🗑️  포트 8001 프로세스 정리 중..."
    lsof -ti:8001 | xargs kill -9 2>/dev/null
    echo "✅ 포트 8001 정리 완료"
    ;;
  3)
    echo ""
    echo "🗑️  전체 정리 중..."
    # Docker 정리
    docker stop naver-monitor-backend 2>/dev/null
    docker rm naver-monitor-backend 2>/dev/null
    docker stop naver-monitor-db 2>/dev/null
    docker rm naver-monitor-db 2>/dev/null
    docker stop naver-monitor-frontend 2>/dev/null
    docker rm naver-monitor-frontend 2>/dev/null
    # 포트 정리
    lsof -ti:8001 | xargs kill -9 2>/dev/null
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    echo "✅ 전체 정리 완료"
    ;;
  4)
    echo ""
    echo "❌ 취소됨"
    exit 0
    ;;
  *)
    echo ""
    echo "❌ 잘못된 선택"
    exit 1
    ;;
esac

# 정리 후 확인
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "정리 후 상태:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📦 Docker 컨테이너:"
docker ps -a | grep naver-monitor || echo "  (없음)"
echo ""
echo "🔌 포트 8001:"
lsof -i:8001 || echo "  (사용 안 함)"
echo ""
echo "🔌 포트 3000:"
lsof -i:3000 || echo "  (사용 안 함)"
echo ""

echo "✅ 이제 다시 배포할 수 있습니다!"
echo ""
echo "다음 명령어로 배포하세요:"
echo "  ./deploy-docker.sh 49.50.134.250"

