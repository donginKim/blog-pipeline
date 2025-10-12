#!/bin/bash

# 간단한 비밀번호 변경 스크립트 (가상환경 불필요)

echo "🔒 비밀번호 변경"
echo "=========================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 데이터베이스 확인
if [ ! -f "naver_monitor.db" ]; then
    echo -e "${RED}❌ 데이터베이스를 찾을 수 없습니다.${NC}"
    exit 1
fi

# 현재 사용자 목록
echo -e "${BLUE}📋 현재 등록된 사용자:${NC}"
sqlite3 naver_monitor.db "SELECT id, username, email FROM users;" | while IFS='|' read -r id username email; do
    echo "   ID: $id | $username | $email"
done
echo ""

# 사용자 선택
read -p "사용자 ID를 입력하세요: " USER_ID

if [ -z "$USER_ID" ]; then
    echo -e "${RED}❌ 사용자 ID를 입력하세요.${NC}"
    exit 1
fi

# 사용자 확인
USERNAME=$(sqlite3 naver_monitor.db "SELECT username FROM users WHERE id = $USER_ID;")

if [ -z "$USERNAME" ]; then
    echo -e "${RED}❌ 존재하지 않는 사용자 ID입니다.${NC}"
    exit 1
fi

echo -e "${BLUE}선택한 사용자: $USERNAME${NC}"
echo ""

# 새 비밀번호 입력
read -sp "새 비밀번호: " NEW_PASSWORD
echo ""

if [ -z "$NEW_PASSWORD" ]; then
    echo -e "${RED}❌ 비밀번호를 입력하세요.${NC}"
    exit 1
fi

# 비밀번호 확인
read -sp "비밀번호 확인: " CONFIRM_PASSWORD
echo ""

if [ "$NEW_PASSWORD" != "$CONFIRM_PASSWORD" ]; then
    echo -e "${RED}❌ 비밀번호가 일치하지 않습니다.${NC}"
    exit 1
fi

# 비밀번호 업데이트 (평문으로 저장)
sqlite3 naver_monitor.db "UPDATE users SET hashed_password = '$NEW_PASSWORD' WHERE id = $USER_ID;"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 비밀번호가 변경되었습니다!${NC}"
    echo ""
    echo -e "${BLUE}새 로그인 정보:${NC}"
    echo "   사용자명: $USERNAME"
    echo "   비밀번호: $NEW_PASSWORD"
    echo ""
    echo -e "${YELLOW}⚠️  새 비밀번호를 기억해두세요!${NC}"
else
    echo -e "${RED}❌ 비밀번호 변경에 실패했습니다.${NC}"
    exit 1
fi

echo ""
echo "=========================================="

