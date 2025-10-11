#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Naver Monitor 로컬 테스트 환경 구축${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Starting PostgreSQL and Redis with Docker Compose...${NC}"

# Start only database services
docker-compose up -d postgres redis

echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Check if services are healthy
echo -e "${YELLOW}🔍 Checking service health...${NC}"

# Wait for PostgreSQL
echo -e "${YELLOW}Waiting for PostgreSQL...${NC}"
until docker-compose exec postgres pg_isready -U postgres; do
    echo -e "${YELLOW}PostgreSQL is unavailable - sleeping${NC}"
    sleep 2
done

# Wait for Redis
echo -e "${YELLOW}Waiting for Redis...${NC}"
until docker-compose exec redis redis-cli ping; do
    echo -e "${YELLOW}Redis is unavailable - sleeping${NC}"
    sleep 2
done

echo -e "${GREEN}✅ Database services are ready!${NC}"

# Setup Python environment
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

# Copy environment file
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}📝 Creating backend environment file...${NC}"
    cp backend/env.example backend/.env
fi

# Run database migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
cd backend
alembic upgrade head
cd ..

# Setup frontend
echo -e "${YELLOW}🎨 Setting up frontend...${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi

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
echo -e "${BLUE}2. Start Celery worker (in another terminal):${NC}"
echo -e "   ${YELLOW}source venv/bin/activate${NC}"
echo -e "   ${YELLOW}cd backend && celery -A app.core.celery worker --loglevel=info${NC}"
echo -e ""
echo -e "${BLUE}3. Start Celery beat (in another terminal):${NC}"
echo -e "   ${YELLOW}source venv/bin/activate${NC}"
echo -e "   ${YELLOW}cd backend && celery -A app.core.celery beat --loglevel=info${NC}"
echo -e ""
echo -e "${BLUE}4. Start the frontend (in another terminal):${NC}"
echo -e "   ${YELLOW}cd frontend && npm run dev${NC}"
echo -e ""
echo -e "${BLUE}5. Access the application:${NC}"
echo -e "   ${YELLOW}Frontend: http://localhost:3000${NC}"
echo -e "   ${YELLOW}API Docs: http://localhost:8000/docs${NC}"
echo -e "   ${YELLOW}Flower: http://localhost:5555${NC}"
echo -e ""
echo -e "${GREEN}💡 Tip: Use 'docker-compose logs -f' to monitor service logs${NC}"

