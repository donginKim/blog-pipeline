#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${GREEN}🚀 Naver Monitor 로컬 테스트 시작${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run setup-local.sh first.${NC}"
    exit 1
fi

# Kill any existing processes more thoroughly
echo -e "${YELLOW}🔄 기존 프로세스 정리 중...${NC}"
pkill -f server-with-auth.py 2>/dev/null || true
pkill -f server-debug.py 2>/dev/null || true
pkill -f simple-server.py 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

# Wait for processes to fully terminate
sleep 2

# Check if ports are available
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        echo -e "${RED}❌ Port $port is already in use. Please kill the process using this port.${NC}"
        lsof -i :$port
        exit 1
    fi
}

echo -e "${YELLOW}🔍 포트 사용 가능 여부 확인...${NC}"
check_port 8001
check_port 3000

# Activate virtual environment
echo -e "${YELLOW}🐍 Virtual environment 활성화...${NC}"
source venv/bin/activate

# Install/update bcrypt if needed
echo -e "${YELLOW}📦 필요한 패키지 확인...${NC}"
pip install bcrypt >/dev/null 2>&1

# Check if database exists and is valid
if [ ! -f "naver_monitor.db" ]; then
    echo -e "${YELLOW}📊 데이터베이스 초기화...${NC}"
    python3 "$SCRIPT_DIR/init-db.py"
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 데이터베이스 초기화 실패${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}📊 데이터베이스 상태 확인...${NC}"
    # Check if database has valid user
    USER_COUNT=$(sqlite3 naver_monitor.db "SELECT COUNT(*) FROM users WHERE username = 'testuser';" 2>/dev/null || echo "0")
    if [ "$USER_COUNT" -eq 0 ]; then
        echo -e "${YELLOW}📊 사용자 데이터 재생성...${NC}"
        python3 "$SCRIPT_DIR/init-db.py"
    fi
fi

# Verify database has correct hash format
echo -e "${YELLOW}🔍 데이터베이스 해시 형식 확인...${NC}"
HASH_FORMAT=$(sqlite3 naver_monitor.db "SELECT substr(hashed_password, 1, 4) FROM users WHERE username = 'testuser';" 2>/dev/null || echo "")
if [ "$HASH_FORMAT" != "\$2b\$" ]; then
    echo -e "${YELLOW}🔧 해시 형식을 bcrypt로 업데이트...${NC}"
    python3 "$SCRIPT_DIR/update-password.py"
fi

# Start backend server
echo -e "${YELLOW}🔧 백엔드 서버 시작...${NC}"
python3 "$SCRIPT_DIR/server-debug.py" > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start with better checking
echo -e "${YELLOW}⏳ 백엔드 서버 시작 대기...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:8001/ >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 백엔드 서버 시작 완료 (PID: $BACKEND_PID)${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ 백엔드 서버 시작 실패${NC}"
        echo -e "${RED}백엔드 로그:${NC}"
        cat backend.log
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

# Test login API
echo -e "${YELLOW}🧪 로그인 API 테스트...${NC}"
LOGIN_TEST=$(curl -s -X POST http://localhost:8001/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"testuser","password":"testpassword123"}' \
    -w "%{http_code}" -o /dev/null)

if [ "$LOGIN_TEST" != "200" ]; then
    echo -e "${RED}❌ 로그인 API 테스트 실패 (HTTP $LOGIN_TEST)${NC}"
    echo -e "${RED}백엔드 로그:${NC}"
    tail -20 backend.log
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✅ 로그인 API 테스트 성공${NC}"

# Start frontend
echo -e "${YELLOW}🎨 프론트엔드 시작...${NC}"
cd "$SCRIPT_DIR/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 프론트엔드 의존성 설치...${NC}"
    npm install
fi

npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

# Wait for frontend to start
echo -e "${YELLOW}⏳ 프론트엔드 시작 대기...${NC}"
for i in {1..15}; do
    if curl -s http://localhost:3000/ >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 프론트엔드 시작 완료 (PID: $FRONTEND_PID)${NC}"
        break
    fi
    if [ $i -eq 15 ]; then
        echo -e "${RED}❌ 프론트엔드 시작 실패${NC}"
        echo -e "${RED}프론트엔드 로그:${NC}"
        cat frontend.log
        kill $FRONTEND_PID 2>/dev/null || true
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

echo -e "${GREEN}🎉 모든 서비스가 시작되었습니다!${NC}"
echo -e ""
echo -e "${BLUE}📋 접속 정보:${NC}"
echo -e "   ${YELLOW}프론트엔드: http://localhost:3000${NC}"
echo -e "   ${YELLOW}API 서버: http://localhost:8001${NC}"
echo -e "   ${YELLOW}API 문서: http://localhost:8001/docs${NC}"
echo -e ""
echo -e "${BLUE}🔧 테스트 계정:${NC}"
echo -e "   ${YELLOW}사용자명: testuser${NC}"
echo -e "   ${YELLOW}비밀번호: testpassword123${NC}"
echo -e ""
echo -e "${BLUE}📊 테스트 데이터:${NC}"
echo -e "   ${YELLOW}키워드: 4개 (파이썬, 자바스크립트, 리액트, 데이터베이스)${NC}"
echo -e "   ${YELLOW}블로그: 3개 (내 블로그, 기술 블로그, 일상 블로그)${NC}"
echo -e "   ${YELLOW}타겟: 5개 (키워드-블로그 조합)${NC}"
echo -e ""
echo -e "${BLUE}🧪 API 테스트 명령어:${NC}"
echo -e "   ${YELLOW}# 로그인${NC}"
echo -e "   ${YELLOW}curl -X POST http://localhost:8001/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"testuser\",\"password\":\"testpassword123\"}'${NC}"
echo -e ""
echo -e "   ${YELLOW}# 인증이 필요한 API (TOKEN을 위에서 받은 토큰으로 교체)${NC}"
echo -e "   ${YELLOW}curl -H 'Authorization: Bearer TOKEN' http://localhost:8001/api/keywords${NC}"
echo -e "   ${YELLOW}curl -H 'Authorization: Bearer TOKEN' http://localhost:8001/api/blogs${NC}"
echo -e "   ${YELLOW}curl -H 'Authorization: Bearer TOKEN' http://localhost:8001/api/targets${NC}"
echo -e "   ${YELLOW}curl -H 'Authorization: Bearer TOKEN' http://localhost:8001/api/dashboard/stats${NC}"
echo -e ""
echo -e "${GREEN}💡 브라우저에서 http://localhost:3000 에 접속하여 테스트하세요!${NC}"
echo -e ""
echo -e "${RED}⚠️  종료하려면 Ctrl+C를 누르세요${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🔄 서비스 종료 중...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    
    # Wait for processes to terminate
    sleep 2
    
    # Force kill if still running
    pkill -f server-debug.py 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    echo -e "${GREEN}✅ 모든 서비스가 종료되었습니다.${NC}"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Keep script running and monitor services
echo -e "${GREEN}🔄 서비스가 실행 중입니다... (Ctrl+C로 종료)${NC}"

# Monitor services
while true; do
    # Check if backend is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ 백엔드 서버가 예기치 않게 종료되었습니다.${NC}"
        cleanup
    fi
    
    # Check if frontend is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ 프론트엔드 서버가 예기치 않게 종료되었습니다.${NC}"
        cleanup
    fi
    
    sleep 5
done