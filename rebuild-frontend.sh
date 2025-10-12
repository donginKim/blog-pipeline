#!/bin/bash

# 프론트엔드 재빌드 및 재시작 스크립트

PUBLIC_IP=${1:-"49.50.134.250"}

echo "🔄 프론트엔드 재빌드 (API URL: http://$PUBLIC_IP:8001)"
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
    echo -e "${YELLOW}💡 또는 백엔드만 사용하세요:${NC}"
    echo "   http://$PUBLIC_IP:8001/docs"
    echo ""
    exit 1
fi

# 프론트엔드 디렉토리 확인
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ frontend 디렉토리를 찾을 수 없습니다.${NC}"
    exit 1
fi

cd frontend

# 1. 환경 변수 설정
echo -e "${YELLOW}1️⃣ API URL 설정...${NC}"
cat > .env << EOF
VITE_API_URL=http://${PUBLIC_IP}:8001
EOF

echo -e "${GREEN}✅ .env 파일 생성: VITE_API_URL=http://${PUBLIC_IP}:8001${NC}"

# 2. 기존 빌드 삭제
echo -e "${YELLOW}2️⃣ 기존 빌드 삭제...${NC}"
rm -rf dist node_modules/.vite

# 3. 재빌드
echo -e "${YELLOW}3️⃣ 프로덕션 빌드 중... (1-2분 소요)${NC}"
npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 빌드 실패${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 빌드 완료!${NC}"

cd ..

# 4. 프론트엔드 재시작
echo -e "${YELLOW}4️⃣ 프론트엔드 재시작...${NC}"

# 기존 프론트엔드 프로세스만 종료
if [ -f ".frontend.pid" ]; then
    OLD_PID=$(cat .frontend.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "기존 프론트엔드 프로세스 종료 (PID: $OLD_PID)"
        kill $OLD_PID 2>/dev/null || true
        sleep 2
        # 강제 종료가 필요하면
        if ps -p $OLD_PID > /dev/null 2>&1; then
            kill -9 $OLD_PID 2>/dev/null || true
        fi
    fi
    rm -f .frontend.pid
fi

# 포트만 정리 (3000)
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 1

# 프로덕션 빌드 서빙 (Python HTTP Server 사용)
cd frontend/dist
nohup python3 -m http.server 3000 > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

sleep 2

if ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 프론트엔드 시작 완료 (PID: $FRONTEND_PID)${NC}"
    echo $FRONTEND_PID > .frontend.pid
else
    echo -e "${RED}❌ 프론트엔드 시작 실패${NC}"
    echo "로그 확인: tail -f logs/frontend.log"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 완료!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📋 접속 URL:${NC}"
echo "   프론트엔드: http://${PUBLIC_IP}:3000"
echo "   백엔드 API: http://${PUBLIC_IP}:8001"
echo "   API 문서: http://${PUBLIC_IP}:8001/docs"
echo ""
echo -e "${BLUE}🔐 로그인:${NC}"
echo "   사용자명: testuser"
echo "   비밀번호: testpassword123 (또는 변경한 비밀번호)"
echo ""
echo -e "${YELLOW}⚠️  중요:${NC}"
echo "   네이버 클라우드 ACG에서 TCP 3000 포트를 열어야 합니다!"
echo ""
echo -e "${BLUE}🔍 테스트:${NC}"
echo "   curl http://${PUBLIC_IP}:3000"
echo ""

