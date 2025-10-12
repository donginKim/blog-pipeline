#!/bin/bash

# 백엔드만 시작하는 스크립트

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "🚀 백엔드 서버 시작"
echo "=========================================="
echo ""

# 로그 디렉토리 생성
mkdir -p logs

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 가상환경이 없습니다. setup-server.sh를 먼저 실행하세요.${NC}"
    exit 1
fi

# 기존 프로세스 종료
echo -e "${YELLOW}🛑 기존 백엔드 프로세스 종료 중...${NC}"
pkill -f "python.*server-debug.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
sleep 2

# 가상환경 활성화 및 백엔드 시작
echo -e "${YELLOW}🚀 백엔드 시작 중...${NC}"
source venv/bin/activate

# 백엔드 시작
nohup python3 server-debug.py > logs/server.log 2>&1 &
BACKEND_PID=$!

sleep 3

# 백엔드 확인
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 백엔드 시작 완료 (PID: $BACKEND_PID)${NC}"
    echo $BACKEND_PID > .backend.pid
else
    echo -e "${RED}❌ 백엔드 시작 실패${NC}"
    echo "로그 확인:"
    tail -50 logs/server.log
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 백엔드 시작 완료!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📋 접속 정보:${NC}"
echo "   - API 서버: http://$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost'):8001"
echo "   - API 문서: http://$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost'):8001/docs"
echo ""
echo -e "${BLUE}🔧 기본 계정:${NC}"
echo "   - 사용자명: testuser"
echo "   - 비밀번호: testpassword123"
echo ""
echo -e "${BLUE}📊 로그 확인:${NC}"
echo "   - tail -f logs/server.log"
echo ""
echo -e "${BLUE}🛑 서버 중지:${NC}"
echo "   ./stop-server.sh"
echo ""
echo -e "${BLUE}💾 프로세스 ID:${NC}"
echo "   - 백엔드: $BACKEND_PID"
echo ""
echo "=========================================="
echo ""
echo -e "${BLUE}💡 API 문서로 모든 기능 사용 가능:${NC}"
echo "   http://$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost'):8001/docs"
echo ""

