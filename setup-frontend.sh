#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎨 Setting up Naver Monitor Frontend Development Environment${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}❌ Node.js version 18+ is required. Current version: $(node -v)${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
cd frontend

# Install dependencies
npm install

echo -e "${GREEN}✅ Frontend setup complete!${NC}"
echo -e "${GREEN}📋 Next steps:${NC}"
echo -e "  1. Start the backend API: ${YELLOW}cd ../backend && uvicorn app.main:app --reload${NC}"
echo -e "  2. Start the frontend: ${YELLOW}npm run dev${NC}"
echo -e "  3. Access the app: ${YELLOW}http://localhost:3000${NC}"
echo -e "  4. Access API docs: ${YELLOW}http://localhost:8000/docs${NC}"

