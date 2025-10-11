# Development setup script
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Setting up Naver Monitor Backend Development Environment${NC}"

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

echo -e "${YELLOW}📦 Starting services with Docker Compose...${NC}"

# Start services
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

echo -e "${GREEN}✅ All services are ready!${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}🐍 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}📚 Installing Python dependencies...${NC}"
pip install -r backend/requirements.txt

# Install Playwright browsers
echo -e "${YELLOW}🎭 Installing Playwright browsers...${NC}"
playwright install chromium

# Copy environment file
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}📝 Creating environment file...${NC}"
    cp backend/env.example backend/.env
    echo -e "${YELLOW}⚠️  Please edit backend/.env with your configuration${NC}"
fi

# Run database migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
cd backend
alembic upgrade head
cd ..

echo -e "${GREEN}🎉 Setup complete!${NC}"
echo -e "${GREEN}📋 Next steps:${NC}"
echo -e "  1. Edit backend/.env with your configuration"
echo -e "  2. Start the backend: ${YELLOW}cd backend && uvicorn app.main:app --reload${NC}"
echo -e "  3. Start Celery worker: ${YELLOW}cd backend && celery -A app.core.celery worker --loglevel=info${NC}"
echo -e "  4. Start Celery beat: ${YELLOW}cd backend && celery -A app.core.celery beat --loglevel=info${NC}"
echo -e "  5. Access API docs: ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "  6. Access Flower: ${YELLOW}http://localhost:5555${NC}"

