#!/bin/bash

# CORS 설정 스크립트

PUBLIC_IP=${1:-"49.50.134.250"}

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "🔧 CORS 설정"
echo "=========================================="
echo ""
echo -e "${BLUE}공인 IP: $PUBLIC_IP${NC}"
echo ""

# .env 파일 확인 및 생성
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 .env 파일 생성 중...${NC}"
    touch .env
fi

# PUBLIC_IP 설정 추가/업데이트
if grep -q "^PUBLIC_IP=" .env; then
    # 이미 있으면 업데이트
    sed -i.bak "s/^PUBLIC_IP=.*/PUBLIC_IP=$PUBLIC_IP/" .env
    rm -f .env.bak
    echo -e "${GREEN}✅ PUBLIC_IP 업데이트 완료${NC}"
else
    # 없으면 추가
    echo "PUBLIC_IP=$PUBLIC_IP" >> .env
    echo -e "${GREEN}✅ PUBLIC_IP 추가 완료${NC}"
fi

# CORS_ORIGINS 설정 추가/업데이트
CORS_ORIGINS="http://localhost:3000,http://localhost:3001,http://${PUBLIC_IP}:3000,http://${PUBLIC_IP}:8001"
if grep -q "^CORS_ORIGINS=" .env; then
    sed -i.bak "s|^CORS_ORIGINS=.*|CORS_ORIGINS=$CORS_ORIGINS|" .env
    rm -f .env.bak
    echo -e "${GREEN}✅ CORS_ORIGINS 업데이트 완료${NC}"
else
    echo "CORS_ORIGINS=$CORS_ORIGINS" >> .env
    echo -e "${GREEN}✅ CORS_ORIGINS 추가 완료${NC}"
fi

echo ""
echo -e "${BLUE}📋 .env 파일 내용:${NC}"
echo "---"
grep -E "^(PUBLIC_IP|CORS_ORIGINS)=" .env
echo "---"
echo ""

echo -e "${YELLOW}⚠️  백엔드를 재시작해야 설정이 적용됩니다:${NC}"
echo "   ./start-backend-only.sh"
echo ""

echo "=========================================="
echo -e "${GREEN}✅ 완료!${NC}"
echo "=========================================="

