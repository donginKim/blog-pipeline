#!/bin/bash

# 긴급 디스크 공간 확보 스크립트
# 루트 파티션이 100% 꽉 찬 경우 사용

set -e

echo "🚨 긴급 디스크 공간 확보 시작"
echo "=========================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 현재 상태
echo -e "${RED}⚠️  현재 디스크 사용률: 100%${NC}"
df -h / | grep -E "Filesystem|/dev"
echo ""

echo -e "${YELLOW}다음 작업을 수행합니다:${NC}"
echo "1. Docker 컨테이너 전체 삭제"
echo "2. Docker 이미지 전체 삭제"
echo "3. Docker 볼륨 전체 삭제"
echo "4. Docker 빌드 캐시 삭제"
echo "5. 시스템 로그 정리"
echo "6. APT 캐시 정리"
echo "7. 임시 파일 정리"
echo ""

read -p "계속하시겠습니까? (yes/no): " -r
if [[ ! $REPLY == "yes" ]]; then
    echo "❌ 취소되었습니다."
    exit 0
fi

echo ""
echo -e "${YELLOW}🧹 정리 시작...${NC}"
echo ""

# 1. Docker 완전 정리
echo "1️⃣ Docker 컨테이너 중지 및 삭제..."
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true
echo -e "${GREEN}✅ 완료${NC}"

echo "2️⃣ Docker 이미지 전체 삭제..."
docker rmi -f $(docker images -aq) 2>/dev/null || true
echo -e "${GREEN}✅ 완료${NC}"

echo "3️⃣ Docker 볼륨 전체 삭제..."
docker volume rm -f $(docker volume ls -q) 2>/dev/null || true
echo -e "${GREEN}✅ 완료${NC}"

echo "4️⃣ Docker 빌드 캐시 삭제..."
docker builder prune -a -f 2>/dev/null || true
echo -e "${GREEN}✅ 완료${NC}"

echo "5️⃣ Docker 시스템 전체 정리..."
docker system prune -a --volumes -f 2>/dev/null || true
echo -e "${GREEN}✅ 완료${NC}"

# 2. 시스템 로그 정리
echo "6️⃣ 시스템 로그 정리..."
sudo journalctl --rotate 2>/dev/null || true
sudo journalctl --vacuum-time=1d 2>/dev/null || true
sudo journalctl --vacuum-size=50M 2>/dev/null || true
sudo rm -rf /var/log/*.log.* 2>/dev/null || true
sudo rm -rf /var/log/*/*.log.* 2>/dev/null || true
sudo truncate -s 0 /var/log/*.log 2>/dev/null || true
echo -e "${GREEN}✅ 완료${NC}"

# 3. APT 캐시 정리
echo "7️⃣ APT 캐시 정리..."
sudo apt-get clean 2>/dev/null || true
sudo apt-get autoclean 2>/dev/null || true
sudo rm -rf /var/cache/apt/archives/* 2>/dev/null || true
sudo rm -rf /var/lib/apt/lists/* 2>/dev/null || true
echo -e "${GREEN}✅ 완료${NC}"

# 4. 임시 파일 정리
echo "8️⃣ 임시 파일 정리..."
sudo rm -rf /tmp/* 2>/dev/null || true
sudo rm -rf /var/tmp/* 2>/dev/null || true
echo -e "${GREEN}✅ 완료${NC}"

# 5. pip 캐시 정리
echo "9️⃣ pip 캐시 정리..."
rm -rf ~/.cache/pip 2>/dev/null || true
echo -e "${GREEN}✅ 완료${NC}"

# 6. npm 캐시 정리
echo "🔟 npm 캐시 정리..."
rm -rf ~/.npm 2>/dev/null || true
rm -rf node_modules 2>/dev/null || true
rm -rf frontend/node_modules 2>/dev/null || true
echo -e "${GREEN}✅ 완료${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 정리 완료!${NC}"
echo "=========================================="
echo ""

# 결과 확인
echo -e "${BLUE}📊 정리 후 디스크 사용량:${NC}"
df -h / | grep -E "Filesystem|/dev"
echo ""

# 큰 파일/디렉토리 확인
echo -e "${BLUE}📂 큰 디렉토리 TOP 10:${NC}"
sudo du -sh /* 2>/dev/null | sort -rh | head -10
echo ""

echo -e "${GREEN}💡 다음 단계:${NC}"
echo "1. 디스크 여유 공간 확인 (최소 2GB 필요)"
echo "2. 로컬 실행 권장: ./start-test.sh"
echo "3. 또는 디스크 확장 후 Docker 배포"
echo ""

