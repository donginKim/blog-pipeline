#!/bin/bash

PUBLIC_IP=${1:-"49.50.134.250"}

echo "🔄 프론트엔드 빌드 재시도"
echo "=========================================="
echo ""

echo "📝 수정 사항:"
echo "  - api.ts 간소화 (TypeScript 오류 수정)"
echo "  - vite-env.d.ts 타입 정의 추가"
echo "  - Nginx 프록시 사용 (/api)"
echo ""

# 빌드 재시도
echo "🔨 Docker 빌드 시작..."
echo ""

docker compose -f docker-compose.prod.yml build frontend 2>&1 | tee /tmp/frontend-build.log

BUILD_EXIT_CODE=${PIPESTATUS[0]}

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ 빌드 성공!"
    echo ""
    echo "🔄 프론트엔드 재시작 중..."
    docker compose -f docker-compose.prod.yml up -d frontend
    
    echo ""
    echo "⏳ 서비스 시작 대기 중..."
    sleep 5
    
    echo ""
    echo "=========================================="
    echo "✅ 완료!"
    echo "=========================================="
    echo ""
    echo "🌐 접속 URL:"
    echo "   http://${PUBLIC_IP}:3000"
    echo ""
    echo "💡 브라우저에서 Ctrl+Shift+R (캐시 삭제)"
    echo ""
else
    echo ""
    echo "❌ 빌드 실패 (exit code: $BUILD_EXIT_CODE)"
    echo ""
    echo "📋 오류 로그:"
    echo "---"
    grep -E "error|Error|ERROR" /tmp/frontend-build.log | tail -20
    echo ""
    echo "🔍 전체 로그:"
    echo "   cat /tmp/frontend-build.log"
    echo ""
    echo "💡 해결 방법:"
    echo "   1. TypeScript 오류: frontend/src/services/api.ts 확인"
    echo "   2. 의존성 오류: cd frontend && npm install"
    echo "   3. 캐시 문제: docker compose build --no-cache frontend"
    echo "   4. 디스크 공간: df -h"
    echo ""
    exit 1
fi

