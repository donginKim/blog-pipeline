#!/bin/bash

# 프론트엔드 빌드 스크립트 (공인 IP용)

PUBLIC_IP=${1:-"49.50.134.250"}

echo "🎨 프론트엔드 빌드 (공인 IP: $PUBLIC_IP)"
echo "=========================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Node.js 확인
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ Node.js가 설치되지 않았습니다.${NC}"
    echo ""
    echo "설치 방법:"
    echo "   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    echo "   sudo apt-get install -y nodejs"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Node.js 확인 완료${NC}"

# frontend 디렉토리로 이동
cd frontend

# .env 파일 생성
echo -e "${YELLOW}📝 환경 변수 설정...${NC}"
cat > .env << EOF
VITE_API_URL=http://${PUBLIC_IP}:8001
EOF

echo -e "${GREEN}✅ API URL 설정: http://${PUBLIC_IP}:8001${NC}"

# 의존성 설치
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 패키지 설치 중... (3-5분 소요)${NC}"
    npm install
    echo -e "${GREEN}✅ 패키지 설치 완료${NC}"
fi

# 빌드
echo -e "${YELLOW}🔨 프로덕션 빌드 중...${NC}"
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 빌드 완료!${NC}"
    echo ""
    echo -e "${BLUE}📂 빌드 파일 위치:${NC}"
    echo "   frontend/dist/"
    echo ""
    echo -e "${BLUE}🚀 서빙 방법:${NC}"
    echo "   cd frontend"
    echo "   npx serve -s dist -p 3000"
    echo ""
    echo "또는 간단히:"
    echo "   ./start-server.sh"
    echo ""
else
    echo -e "${RED}❌ 빌드 실패${NC}"
    exit 1
fi

cd ..

echo "=========================================="
echo -e "${GREEN}🎉 완료!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📋 다음 단계:${NC}"
echo "1. 프론트엔드 시작: ./start-server.sh"
echo "2. 브라우저 접속: http://${PUBLIC_IP}:3000"
echo "3. ACG 확인: TCP 3000 포트 열려있는지"
echo ""

