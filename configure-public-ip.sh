#!/bin/bash

# 공인 IP 설정 스크립트 (네이버 클라우드용)

PUBLIC_IP=${1:-"49.50.134.250"}

echo "🌐 공인 IP 설정: $PUBLIC_IP"
echo "=========================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. CORS 설정 확인
echo -e "${YELLOW}1️⃣ CORS 설정 업데이트...${NC}"

# .env 파일 업데이트
if [ -f .env ]; then
    # 기존 CORS_ORIGINS 제거
    sed -i '/CORS_ORIGINS=/d' .env
fi

# 새 CORS 설정 추가
echo "CORS_ORIGINS=http://$PUBLIC_IP:3000,http://$PUBLIC_IP,http://localhost:3000" >> .env

echo -e "${GREEN}✅ CORS 설정 완료${NC}"

# 2. 방화벽 확인
echo ""
echo -e "${YELLOW}2️⃣ 방화벽 설정 확인...${NC}"
echo -e "${BLUE}네이버 클라우드 콘솔에서 다음 포트를 열어야 합니다:${NC}"
echo ""
echo "   📋 ACG (Access Control Group) 설정:"
echo "   - 프로토콜: TCP"
echo "   - 포트: 8001 (백엔드 API)"
echo "   - 포트: 3000 (프론트엔드, 선택사항)"
echo "   - 접근 소스: 0.0.0.0/0 (모든 IP) 또는 특정 IP"
echo ""
echo -e "${BLUE}💡 설정 방법:${NC}"
echo "   1. 네이버 클라우드 콘솔 접속"
echo "   2. Server > ACG 메뉴"
echo "   3. 인바운드 규칙 추가"
echo "   4. 위 포트 추가"
echo ""

# 3. 서버 재시작
echo -e "${YELLOW}3️⃣ 서버 재시작이 필요합니다.${NC}"
echo ""

read -p "지금 서버를 재시작하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./stop-server.sh 2>/dev/null || true
    sleep 2
    ./start-server.sh
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 설정 완료!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📋 접속 URL:${NC}"
echo "   - API 서버: http://$PUBLIC_IP:8001"
echo "   - API 문서: http://$PUBLIC_IP:8001/docs"
echo "   - 프론트엔드: http://$PUBLIC_IP:3000 (Node.js 설치 시)"
echo ""
echo -e "${BLUE}🔧 테스트:${NC}"
echo "   curl http://$PUBLIC_IP:8001/"
echo ""
echo -e "${YELLOW}⚠️  중요:${NC}"
echo "   네이버 클라우드 ACG에서 포트 8001, 3000을 열어야 합니다!"
echo ""

