#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Naver Monitor 로컬 테스트 시작${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run setup-local.sh first.${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}🐍 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if database is running
echo -e "${YELLOW}🔍 Checking database connection...${NC}"
if ! docker-compose exec postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${RED}❌ PostgreSQL is not running. Please start it first:${NC}"
    echo -e "   ${YELLOW}docker-compose up -d postgres redis${NC}"
    exit 1
fi

if ! docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}❌ Redis is not running. Please start it first:${NC}"
    echo -e "   ${YELLOW}docker-compose up -d postgres redis${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Database services are running${NC}"

# Create test user if not exists
echo -e "${YELLOW}👤 Creating test user...${NC}"
python3 create-test-user.py

# Create test data if not exists
echo -e "${YELLOW}📊 Creating test data...${NC}"
python3 create-test-data.py

echo -e "${GREEN}🎉 Setup complete!${NC}"
echo -e ""
echo -e "${BLUE}📋 다음 단계:${NC}"
echo -e ""
echo -e "${BLUE}1. 백엔드 API 시작 (터미널 1):${NC}"
echo -e "   ${YELLOW}source venv/bin/activate${NC}"
echo -e "   ${YELLOW}cd backend && uvicorn app.main:app --reload${NC}"
echo -e ""
echo -e "${BLUE}2. Celery 워커 시작 (터미널 2):${NC}"
echo -e "   ${YELLOW}source venv/bin/activate${NC}"
echo -e "   ${YELLOW}cd backend && celery -A app.core.celery worker --loglevel=info${NC}"
echo -e ""
echo -e "${BLUE}3. 프론트엔드 시작 (터미널 3):${NC}"
echo -e "   ${YELLOW}cd frontend && npm run dev${NC}"
echo -e ""
echo -e "${BLUE}4. 접속 URL:${NC}"
echo -e "   ${YELLOW}프론트엔드: http://localhost:3000${NC}"
echo -e "   ${YELLOW}API 문서: http://localhost:8000/docs${NC}"
echo -e ""
echo -e "${BLUE}5. 테스트 계정:${NC}"
echo -e "   ${YELLOW}사용자명: testuser${NC}"
echo -e "   ${YELLOW}비밀번호: testpassword123${NC}"
echo -e ""
echo -e "${GREEN}💡 Tip: 각 서비스를 별도 터미널에서 실행하세요${NC}"

