#!/bin/bash

# Docker 디스크 공간 정리 스크립트

echo "🧹 Docker 디스크 공간 정리 시작"
echo "=========================================="

# 색상
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 현재 디스크 사용량 확인
echo -e "${BLUE}📊 현재 디스크 사용량:${NC}"
df -h | grep -E "Filesystem|/$"
echo ""

echo -e "${BLUE}📊 Docker 디스크 사용량:${NC}"
docker system df
echo ""

# 정리 확인
read -p "Docker 데이터를 정리하시겠습니까? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 취소되었습니다."
    exit 0
fi

echo -e "${YELLOW}🧹 정리 시작...${NC}"
echo ""

# 1. 중지된 컨테이너 삭제
echo -e "${YELLOW}1️⃣ 중지된 컨테이너 삭제...${NC}"
STOPPED=$(docker ps -aq -f status=exited | wc -l)
if [ "$STOPPED" -gt 0 ]; then
    docker rm $(docker ps -aq -f status=exited) 2>/dev/null || true
    echo -e "${GREEN}✅ ${STOPPED}개 컨테이너 삭제${NC}"
else
    echo "   (중지된 컨테이너 없음)"
fi
echo ""

# 2. 사용하지 않는 이미지 삭제
echo -e "${YELLOW}2️⃣ 사용하지 않는 이미지 삭제...${NC}"
docker image prune -a -f
echo -e "${GREEN}✅ 이미지 정리 완료${NC}"
echo ""

# 3. 빌드 캐시 삭제
echo -e "${YELLOW}3️⃣ 빌드 캐시 삭제...${NC}"
docker builder prune -a -f
echo -e "${GREEN}✅ 빌드 캐시 정리 완료${NC}"
echo ""

# 4. 사용하지 않는 볼륨 삭제
echo -e "${YELLOW}4️⃣ 사용하지 않는 볼륨 삭제...${NC}"
docker volume prune -f
echo -e "${GREEN}✅ 볼륨 정리 완료${NC}"
echo ""

# 5. 사용하지 않는 네트워크 삭제
echo -e "${YELLOW}5️⃣ 네트워크 정리...${NC}"
docker network prune -f
echo -e "${GREEN}✅ 네트워크 정리 완료${NC}"
echo ""

# 정리 후 상태
echo "=========================================="
echo -e "${GREEN}🎉 정리 완료!${NC}"
echo "=========================================="
echo ""

echo -e "${BLUE}📊 정리 후 디스크 사용량:${NC}"
df -h | grep -E "Filesystem|/$"
echo ""

echo -e "${BLUE}📊 Docker 디스크 사용량:${NC}"
docker system df
echo ""

echo -e "${GREEN}💡 이제 다시 배포를 시도하세요:${NC}"
echo "   ./deploy-stable.sh"
echo ""

