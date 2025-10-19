#!/bin/bash

PUBLIC_IP=${1:-"49.50.134.250"}

echo "🔧 프론트엔드 빠른 수정"
echo "=========================================="
echo ""

echo "📝 변경 사항:"
echo "  - Nginx API 프록시 추가"
echo "  - 프론트엔드에서 /api/ 요청을 백엔드로 전달"
echo "  - localhost:8001 문제 해결"
echo ""

# 프론트엔드만 재빌드 및 재시작
echo "🔨 프론트엔드 재빌드 중..."
docker compose -f docker-compose.prod.yml build frontend

if [ $? -ne 0 ]; then
    echo "❌ 빌드 실패"
    exit 1
fi

echo "✅ 빌드 완료"
echo ""

echo "🔄 프론트엔드 재시작 중..."
docker compose -f docker-compose.prod.yml up -d frontend

echo "✅ 재시작 완료"
echo ""

# 대기
echo "⏳ 서비스 시작 대기 중..."
sleep 5

echo ""
echo "=========================================="
echo "✅ 수정 완료!"
echo "=========================================="
echo ""
echo "🌐 접속 URL:"
echo "   http://${PUBLIC_IP}:3000"
echo ""
echo "💡 브라우저에서:"
echo "   1. Ctrl+Shift+R (캐시 삭제 후 새로고침)"
echo "   2. 설정 페이지에서 저장 테스트"
echo ""
echo "🔍 API 요청 확인:"
echo "   브라우저 개발자 도구 > Network 탭"
echo "   - 이전: http://localhost:8001/api/..."
echo "   - 현재: /api/... (상대 경로, Nginx가 프록시)"
echo ""

