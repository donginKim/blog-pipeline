#!/bin/bash

echo "🔍 프론트엔드 빌드 오류 확인"
echo "=========================================="
echo ""

# 1. 로컬에서 빌드 테스트 (Node.js 설치된 경우)
if command -v npm &> /dev/null; then
    echo "1️⃣  로컬 빌드 테스트:"
    echo "---"
    cd frontend
    
    # 의존성 확인
    if [ ! -d "node_modules" ]; then
        echo "📦 의존성 설치 중..."
        npm install
    fi
    
    # 빌드 시도
    echo ""
    echo "🔨 빌드 시작..."
    npm run build 2>&1 | tee build.log
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo ""
        echo "✅ 로컬 빌드 성공!"
    else
        echo ""
        echo "❌ 로컬 빌드 실패"
        echo ""
        echo "📋 주요 오류:"
        grep -E "error|Error|ERROR" build.log | head -10
    fi
    
    cd ..
else
    echo "⚠️  Node.js가 설치되지 않았습니다."
    echo "   Docker 빌드 로그를 확인하세요."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 2. Docker 빌드 로그 확인
echo "2️⃣  Docker 빌드 로그:"
echo "---"
docker compose -f docker-compose.prod.yml build frontend 2>&1 | tee docker-build.log

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 3. 일반적인 해결 방법
echo "3️⃣  일반적인 해결 방법:"
echo "---"
echo ""
echo "📝 TypeScript 오류:"
echo "   - frontend/src/services/api.ts 확인"
echo "   - frontend/src/types/index.ts 확인"
echo "   - 'any' 타입 사용으로 임시 해결"
echo ""
echo "📦 의존성 오류:"
echo "   cd frontend && npm install"
echo ""
echo "🔧 캐시 문제:"
echo "   docker compose -f docker-compose.prod.yml build --no-cache frontend"
echo ""
echo "💾 디스크 공간:"
echo "   df -h"
echo ""

echo "=========================================="
echo ""
echo "📚 관련 문서:"
echo "   - FRONTEND_FIX.md"
echo "   - DOCKER_TROUBLESHOOTING.md"
echo ""

