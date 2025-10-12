#!/bin/bash

# Nginx IPv6 문제 해결 스크립트

echo "🔧 Nginx 설정 수정"
echo "=========================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. dpkg 오류 수정
echo -e "${YELLOW}1️⃣ dpkg 오류 수정...${NC}"
sudo dpkg --configure -a

# 2. Nginx 제거 (깔끔하게)
echo -e "${YELLOW}2️⃣ Nginx 제거...${NC}"
sudo apt-get remove --purge nginx nginx-common -y 2>/dev/null || true
sudo apt-get autoremove -y

# 3. Nginx 재설치 (IPv6 비활성화 버전)
echo -e "${YELLOW}3️⃣ Nginx 재설치...${NC}"
sudo apt-get update
sudo apt-get install -y nginx

# 4. Nginx 기본 설정 수정 (IPv6 비활성화)
echo -e "${YELLOW}4️⃣ IPv6 비활성화...${NC}"
sudo sed -i 's/listen \[::\]:80/# listen [::]:80/g' /etc/nginx/sites-available/default
sudo sed -i 's/listen \[::\]:443/# listen [::]:443/g' /etc/nginx/sites-available/default 2>/dev/null || true

# 5. Nginx 설정 테스트
echo -e "${YELLOW}5️⃣ 설정 테스트...${NC}"
sudo nginx -t

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Nginx 설정 정상${NC}"
    
    # Nginx 시작
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    echo -e "${GREEN}✅ Nginx 시작 완료${NC}"
else
    echo -e "${RED}❌ Nginx 설정 오류${NC}"
    echo ""
    echo -e "${YELLOW}💡 Nginx 없이도 서버는 정상 작동합니다:${NC}"
    echo "   - 백엔드: http://49.50.134.250:8001"
    echo "   - 프론트엔드: http://49.50.134.250:3000"
    echo ""
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 완료!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📋 Nginx 상태:${NC}"
sudo systemctl status nginx --no-pager | head -10
echo ""

