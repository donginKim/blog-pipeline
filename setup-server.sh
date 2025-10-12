#!/bin/bash

# 우분투 서버 초기 설정 스크립트

set -e

echo "🚀 Naver Monitor 서버 설정 시작"
echo "=========================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3가 설치되지 않았습니다.${NC}"
    echo "설치: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi

echo -e "${GREEN}✅ Python3 확인 완료${NC}"

# 가상환경 생성
echo -e "${YELLOW}📦 가상환경 생성 중...${NC}"
python3 -m venv venv

echo -e "${GREEN}✅ 가상환경 생성 완료${NC}"

# 가상환경 활성화 및 패키지 설치
echo -e "${YELLOW}📦 패키지 설치 중... (3-5분 소요)${NC}"
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip setuptools wheel

# requirements.txt 설치
pip install -r requirements.txt

echo -e "${GREEN}✅ 패키지 설치 완료${NC}"

# Playwright 브라우저 설치
echo -e "${YELLOW}🌐 Playwright 브라우저 설치 중...${NC}"
playwright install chromium
playwright install-deps chromium 2>/dev/null || echo "⚠️ 시스템 의존성 설치 실패 (sudo 권한 필요)"

echo -e "${GREEN}✅ Playwright 설치 완료${NC}"

# 데이터베이스 초기화
if [ ! -f naver_monitor.db ]; then
    echo -e "${YELLOW}💾 데이터베이스 초기화 중...${NC}"
    python3 init-db.py
    echo -e "${GREEN}✅ 데이터베이스 초기화 완료${NC}"
fi

# 필요한 테이블 추가
echo -e "${YELLOW}📊 추가 테이블 생성 중...${NC}"
python3 add-settings-table.py 2>/dev/null || echo "   (이미 존재함)"
python3 add-generated-posts-table.py 2>/dev/null || echo "   (이미 존재함)"

# 디렉토리 생성
mkdir -p logs blog_posts

# .env 파일 확인
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env 파일이 없습니다.${NC}"
    echo "   기본값을 사용합니다. 필요시 .env 파일을 생성하세요:"
    echo "   cp env.aligo.example .env"
    echo "   nano .env"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 설정 완료!${NC}"
echo "=========================================="
echo ""
echo -e "${YELLOW}📋 다음 명령어로 서버를 시작하세요:${NC}"
echo ""
echo "   ./start-server.sh"
echo ""
echo "또는 수동으로:"
echo "   source venv/bin/activate"
echo "   python3 server-debug.py"
echo ""

