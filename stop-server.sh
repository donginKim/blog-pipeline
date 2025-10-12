#!/bin/bash

# Naver Monitor 서버 중지 스크립트

echo "🛑 Naver Monitor 서버 중지"
echo "=========================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# PID 파일에서 프로세스 종료
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}🛑 백엔드 서버 종료 중... (PID: $BACKEND_PID)${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        rm .backend.pid
        echo -e "${GREEN}✅ 백엔드 서버 종료 완료${NC}"
    fi
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}🛑 프론트엔드 서버 종료 중... (PID: $FRONTEND_PID)${NC}"
        kill $FRONTEND_PID 2>/dev/null || true
        rm .frontend.pid
        echo -e "${GREEN}✅ 프론트엔드 서버 종료 완료${NC}"
    fi
fi

# 프로세스 이름으로 강제 종료
echo -e "${YELLOW}🔍 남은 프로세스 확인 및 종료...${NC}"
pkill -f "server-debug.py" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

# 포트 확인
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  포트 8001 강제 해제...${NC}"
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  포트 3000 강제 해제...${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}🎉 모든 서버가 중지되었습니다.${NC}"
echo ""

