#!/bin/bash

# 서버 상태 확인 스크립트

echo "🔍 Naver Monitor 서버 상태 확인"
echo "=========================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. 프로세스 확인
echo -e "${BLUE}1️⃣ 프로세스 상태:${NC}"
echo ""
echo "백엔드 (server-debug.py):"
if ps aux | grep -v grep | grep "server-debug.py" > /dev/null; then
    echo -e "${GREEN}✅ 실행 중${NC}"
    ps aux | grep -v grep | grep "server-debug.py" | head -1
else
    echo -e "${RED}❌ 실행 안 됨${NC}"
fi
echo ""

echo "프론트엔드 (npm/vite):"
if ps aux | grep -v grep | grep "vite" > /dev/null; then
    echo -e "${GREEN}✅ 실행 중${NC}"
    ps aux | grep -v grep | grep "vite" | head -1
else
    echo -e "${RED}❌ 실행 안 됨${NC}"
fi
echo ""

# 2. 포트 확인
echo -e "${BLUE}2️⃣ 포트 리스닝 상태:${NC}"
echo ""
echo "포트 8001 (백엔드):"
if lsof -i:8001 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ LISTENING${NC}"
    lsof -i:8001 | head -2
else
    echo -e "${RED}❌ 닫힘${NC}"
fi
echo ""

echo "포트 3000 (프론트엔드):"
if lsof -i:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ LISTENING${NC}"
    lsof -i:3000 | head -2
else
    echo -e "${RED}❌ 닫힘${NC}"
fi
echo ""

# 3. 로컬 접속 테스트
echo -e "${BLUE}3️⃣ 로컬 접속 테스트:${NC}"
echo ""
echo "백엔드 (localhost:8001):"
if curl -s http://localhost:8001/ > /dev/null; then
    echo -e "${GREEN}✅ 응답 정상${NC}"
    curl -s http://localhost:8001/ | head -100
else
    echo -e "${RED}❌ 응답 없음${NC}"
fi
echo ""

echo "프론트엔드 (localhost:3000):"
if curl -s http://localhost:3000/ > /dev/null; then
    echo -e "${GREEN}✅ 응답 정상${NC}"
else
    echo -e "${RED}❌ 응답 없음${NC}"
fi
echo ""

# 4. 방화벽 확인
echo -e "${BLUE}4️⃣ 방화벽 상태:${NC}"
echo ""
if command -v ufw &> /dev/null; then
    echo "UFW 상태:"
    sudo ufw status
else
    echo "UFW 설치 안 됨"
fi
echo ""

# 5. 네트워크 인터페이스
echo -e "${BLUE}5️⃣ 네트워크 인터페이스:${NC}"
echo ""
ip addr show | grep -E "inet |inet6 " | grep -v "127.0.0.1"
echo ""

# 6. 공인 IP 확인
echo -e "${BLUE}6️⃣ 공인 IP:${NC}"
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "확인 실패")
echo "   $PUBLIC_IP"
echo ""

# 7. 로그 확인
echo -e "${BLUE}7️⃣ 최근 로그 (마지막 10줄):${NC}"
echo ""
if [ -f logs/server.log ]; then
    echo "백엔드 로그:"
    tail -10 logs/server.log
else
    echo "로그 파일 없음"
fi
echo ""

# 결과 요약
echo "=========================================="
echo -e "${YELLOW}📋 진단 결과:${NC}"
echo "=========================================="
echo ""

# 백엔드 체크
if ps aux | grep -v grep | grep "server-debug.py" > /dev/null && lsof -i:8001 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 백엔드: 정상 실행 중${NC}"
    echo "   접속: http://$PUBLIC_IP:8001"
    echo "   로컬: http://localhost:8001"
else
    echo -e "${RED}❌ 백엔드: 실행 필요${NC}"
    echo "   실행: ./start-server.sh"
fi
echo ""

# 프론트엔드 체크
if ps aux | grep -v grep | grep "vite" > /dev/null && lsof -i:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 프론트엔드: 정상 실행 중${NC}"
    echo "   접속: http://$PUBLIC_IP:3000"
else
    echo -e "${YELLOW}⚠️  프론트엔드: 실행 안 됨 (백엔드만으로도 사용 가능)${NC}"
    echo "   API 문서로 사용: http://$PUBLIC_IP:8001/docs"
fi
echo ""

# ACG 체크
echo -e "${YELLOW}⚠️  네이버 클라우드 ACG 확인:${NC}"
echo "   https://console.ncloud.com → Server → ACG"
echo "   인바운드 규칙:"
echo "   - TCP 8001 (백엔드)"
echo "   - TCP 3000 (프론트엔드)"
echo ""

echo "=========================================="

