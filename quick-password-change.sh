#!/bin/bash

# 빠른 비밀번호 변경 스크립트 (가상환경 자동 활성화)

echo "🔒 비밀번호 변경"
echo "=========================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 가상환경 확인 및 활성화
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 가상환경이 없습니다.${NC}"
    echo "먼저 설정을 실행하세요:"
    echo "   ./setup-server.sh"
    exit 1
fi

echo -e "${YELLOW}🐍 가상환경 활성화...${NC}"
source venv/bin/activate

# 계정 관리 스크립트 실행
python3 update-account.py

deactivate

