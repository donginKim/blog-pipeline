#!/bin/bash

# Naver Monitor 서버 시작 스크립트 (우분투용)

set -e

echo "🚀 Naver Monitor 서버 시작"
echo "=========================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 가상환경이 없습니다.${NC}"
    echo "먼저 설정을 실행하세요:"
    echo "   ./setup-server.sh"
    exit 1
fi

# 기존 프로세스 정리
echo -e "${YELLOW}🔄 기존 프로세스 정리...${NC}"
pkill -f "server-debug.py" 2>/dev/null || true
sleep 2

# 포트 확인
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  포트 8001이 사용 중입니다. 강제 종료합니다.${NC}"
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# 가상환경 활성화
echo -e "${YELLOW}🐍 가상환경 활성화...${NC}"
source venv/bin/activate

# 데이터베이스 확인
if [ ! -f naver_monitor.db ]; then
    echo -e "${YELLOW}💾 데이터베이스 초기화...${NC}"
    python3 init-db.py
fi

# 서버 시작
echo -e "${YELLOW}🚀 백엔드 서버 시작...${NC}"
nohup python3 server-debug.py > logs/server.log 2>&1 &
BACKEND_PID=$!

# 서버 시작 대기
echo -e "${YELLOW}⏳ 서버 시작 대기...${NC}"
sleep 5

# 서버 확인
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 백엔드 서버 시작 완료 (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}❌ 백엔드 서버 시작 실패${NC}"
    echo "로그 확인:"
    tail -50 logs/server.log
    exit 1
fi

# 프론트엔드 확인
if [ -d "frontend" ]; then
    echo -e "${YELLOW}🎨 프론트엔드 확인...${NC}"
    
    if [ ! -d "frontend/node_modules" ]; then
        echo -e "${YELLOW}📦 프론트엔드 패키지 설치 중...${NC}"
        cd frontend
        npm install
        cd ..
    fi
    
    # 프론트엔드 시작
    echo -e "${YELLOW}🚀 프론트엔드 시작...${NC}"
    cd frontend
    nohup npm run dev -- --host 0.0.0.0 > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    sleep 3
    
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 프론트엔드 시작 완료 (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  프론트엔드 시작 실패 (백엔드만 실행 중)${NC}"
    fi
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 서버 시작 완료!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📋 접속 정보:${NC}"
echo "   - API 서버: http://$(hostname -I | awk '{print $1}'):8001"
echo "   - API 문서: http://$(hostname -I | awk '{print $1}'):8001/docs"

if ps -p ${FRONTEND_PID:-0} > /dev/null 2>&1; then
    echo "   - 프론트엔드: http://$(hostname -I | awk '{print $1}'):3000"
fi

echo ""
echo -e "${BLUE}🔧 기본 계정:${NC}"
echo "   - 사용자명: testuser"
echo "   - 비밀번호: testpassword123"
echo ""
echo -e "${BLUE}📊 로그 확인:${NC}"
echo "   - 백엔드: tail -f logs/server.log"
echo "   - 프론트엔드: tail -f logs/frontend.log"
echo ""
echo -e "${BLUE}🛑 서버 중지:${NC}"
echo "   ./stop-server.sh"
echo ""
echo -e "${BLUE}💾 프로세스 ID:${NC}"
echo "   - 백엔드: $BACKEND_PID"
if ps -p ${FRONTEND_PID:-0} > /dev/null 2>&1; then
    echo "   - 프론트엔드: $FRONTEND_PID"
fi
echo ""
echo "PID를 저장합니다..."
echo $BACKEND_PID > .backend.pid
[ ! -z "${FRONTEND_PID}" ] && echo $FRONTEND_PID > .frontend.pid

echo "=========================================="

