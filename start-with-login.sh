#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Naver Monitor 로그인 기능 테스트${NC}"

# Kill any existing processes
echo -e "${YELLOW}🔄 기존 프로세스 정리 중...${NC}"
pkill -f server-with-auth.py 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true

# Activate virtual environment
echo -e "${YELLOW}🐍 Virtual environment 활성화...${NC}"
source venv/bin/activate

# Check if database exists
if [ ! -f "naver_monitor.db" ]; then
    echo -e "${YELLOW}📊 데이터베이스 초기화...${NC}"
    python3 init-db.py
    python3 update-password.py
fi

# Start backend server
echo -e "${YELLOW}🔧 백엔드 서버 시작...${NC}"
python3 /Users/amiro/Workshop/naver-monitor/server-with-auth.py &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${YELLOW}⏳ 백엔드 서버 시작 대기...${NC}"
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8001/ > /dev/null; then
    echo -e "${RED}❌ 백엔드 서버 시작 실패${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✅ 백엔드 서버 시작 완료 (PID: $BACKEND_PID)${NC}"

# Start frontend
echo -e "${YELLOW}🎨 프론트엔드 시작...${NC}"
cd /Users/amiro/Workshop/naver-monitor/frontend
npm run dev &
FRONTEND_PID=$!
cd /Users/amiro/Workshop/naver-monitor

# Wait for frontend to start
echo -e "${YELLOW}⏳ 프론트엔드 시작 대기...${NC}"
sleep 5

echo -e "${GREEN}🎉 모든 서비스가 시작되었습니다!${NC}"
echo -e ""
echo -e "${BLUE}📋 접속 정보:${NC}"
echo -e "   ${YELLOW}프론트엔드: http://localhost:3001${NC}"
echo -e "   ${YELLOW}API 서버: http://localhost:8001${NC}"
echo -e "   ${YELLOW}API 문서: http://localhost:8001/docs${NC}"
echo -e ""
echo -e "${BLUE}🔧 테스트 계정:${NC}"
echo -e "   ${YELLOW}사용자명: testuser${NC}"
echo -e "   ${YELLOW}비밀번호: testpassword123${NC}"
echo -e ""
echo -e "${BLUE}🔐 로그인 플로우:${NC}"
echo -e "   1. ${YELLOW}브라우저에서 http://localhost:3001 접속${NC}"
echo -e "   2. ${YELLOW}로그인 페이지에서 testuser / testpassword123 입력${NC}"
echo -e "   3. ${YELLOW}로그인 성공 시 자동으로 대시보드로 이동${NC}"
echo -e "   4. ${YELLOW}대시보드에서 키워드, 블로그, 타겟 관리 가능${NC}"
echo -e ""
echo -e "${BLUE}🧪 API 테스트 명령어:${NC}"
echo -e "   ${YELLOW}# 로그인${NC}"
echo -e "   ${YELLOW}curl -X POST http://localhost:8001/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"testuser\",\"password\":\"testpassword123\"}'${NC}"
echo -e ""
echo -e "   ${YELLOW}# 인증이 필요한 API (TOKEN을 위에서 받은 토큰으로 교체)${NC}"
echo -e "   ${YELLOW}curl -H 'Authorization: Bearer TOKEN' http://localhost:8001/api/keywords${NC}"
echo -e "   ${YELLOW}curl -H 'Authorization: Bearer TOKEN' http://localhost:8001/api/dashboard/stats${NC}"
echo -e ""
echo -e "${GREEN}💡 브라우저에서 http://localhost:3001 에 접속하여 로그인 후 대시보드를 확인하세요!${NC}"
echo -e ""
echo -e "${RED}⚠️  종료하려면 Ctrl+C를 누르세요${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🔄 서비스 종료 중...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✅ 모든 서비스가 종료되었습니다.${NC}"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Keep script running
echo -e "${GREEN}🔄 서비스가 실행 중입니다... (Ctrl+C로 종료)${NC}"
wait

