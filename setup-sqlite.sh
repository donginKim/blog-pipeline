#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Naver Monitor 로컬 테스트 환경 구축 (SQLite 버전)${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.11+ first.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi

echo -e "${YELLOW}🐍 Setting up Python environment...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install backend dependencies
echo -e "${YELLOW}📚 Installing backend dependencies...${NC}"
pip install -r backend/requirements.txt

# Install Playwright browsers
echo -e "${YELLOW}🎭 Installing Playwright browsers...${NC}"
playwright install chromium

# Create SQLite environment file
echo -e "${YELLOW}📝 Creating SQLite environment file...${NC}"
cat > backend/.env << EOF
# App settings
APP_NAME="Naver Monitor API"
APP_VERSION="2.0.0"
DEBUG=true

# SQLite Database settings
DATABASE_URL="sqlite+aiosqlite:///./naver_monitor.db"
DATABASE_URL_SYNC="sqlite:///./naver_monitor.db"

# Redis settings (optional for local testing)
REDIS_URL="redis://localhost:6379/0"

# Celery settings (optional for local testing)
CELERY_BROKER_URL="redis://localhost:6379/1"
CELERY_RESULT_BACKEND="redis://localhost:6379/1"

# Security settings
SECRET_KEY="your-secret-key-change-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Crawler settings
CRAWL_TIMEOUT_MS=60000
MAX_CONCURRENT_CRAWLS=5
USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"

# Monitoring settings
ENABLE_METRICS=true
METRICS_PORT=8001
EOF

# Run database migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
cd backend
alembic upgrade head
cd ..

# Setup frontend
echo -e "${YELLOW}🎨 Setting up frontend...${NC}"

# Install frontend dependencies
cd frontend
npm install
cd ..

echo -e "${GREEN}🎉 Setup complete!${NC}"
echo -e "${GREEN}📋 Next steps:${NC}"
echo -e ""
echo -e "${BLUE}1. Start the backend API:${NC}"
echo -e "   ${YELLOW}source venv/bin/activate${NC}"
echo -e "   ${YELLOW}cd backend && uvicorn app.main:app --reload${NC}"
echo -e ""
echo -e "${BLUE}2. Start the frontend (in another terminal):${NC}"
echo -e "   ${YELLOW}cd frontend && npm run dev${NC}"
echo -e ""
echo -e "${BLUE}3. Access the application:${NC}"
echo -e "   ${YELLOW}Frontend: http://localhost:3000${NC}"
echo -e "   ${YELLOW}API Docs: http://localhost:8000/docs${NC}"
echo -e ""
echo -e "${GREEN}💡 Note: This setup uses SQLite instead of PostgreSQL for easier local testing${NC}"

