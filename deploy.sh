#!/bin/bash

# Naver Monitor 프로덕션 배포 스크립트

set -e

echo "🚀 Naver Monitor 프로덕션 배포 시작"
echo "=========================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 환경 변수 파일 확인
if [ ! -f .env.production ]; then
    echo -e "${RED}❌ .env.production 파일이 없습니다.${NC}"
    echo -e "${YELLOW}📝 env.production.example을 참고하여 생성하세요:${NC}"
    echo "   cp env.production.example .env.production"
    echo "   nano .env.production"
    exit 1
fi

echo -e "${GREEN}✅ 환경 변수 파일 확인 완료${NC}"

# Docker 및 Docker Compose 확인
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker가 설치되지 않았습니다.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose가 설치되지 않았습니다.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker 환경 확인 완료${NC}"

# 기존 컨테이너 정리 (선택사항)
read -p "기존 컨테이너를 정리하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 기존 컨테이너 정리 중..."
    docker-compose -f docker-compose.prod.yml --env-file .env.production down -v
    echo -e "${GREEN}✅ 정리 완료${NC}"
fi

# 로그 디렉토리 생성
mkdir -p logs/nginx

# Nginx SSL 디렉토리 생성 (필요시)
mkdir -p nginx/ssl

# 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
docker-compose -f docker-compose.prod.yml --env-file .env.production build

echo -e "${GREEN}✅ 이미지 빌드 완료${NC}"

# 컨테이너 시작
echo "🚀 컨테이너 시작 중..."
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d

echo -e "${GREEN}✅ 컨테이너 시작 완료${NC}"

# 헬스체크 대기
echo "⏳ 서비스 헬스체크 중..."
sleep 10

# 서비스 상태 확인
echo ""
echo "📊 서비스 상태:"
docker-compose -f docker-compose.prod.yml --env-file .env.production ps

# 접속 정보 출력
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 배포 완료!${NC}"
echo "=========================================="
echo ""
echo "📋 접속 정보:"
echo "   - 프론트엔드: http://localhost (또는 설정한 도메인)"
echo "   - 백엔드 API: http://localhost/api"
echo "   - API 문서: http://localhost/api/docs"
echo ""
echo "📊 로그 확인:"
echo "   - 전체 로그: docker-compose -f docker-compose.prod.yml logs -f"
echo "   - 백엔드 로그: docker-compose -f docker-compose.prod.yml logs -f backend"
echo "   - 프론트엔드 로그: docker-compose -f docker-compose.prod.yml logs -f frontend"
echo "   - 데이터베이스 로그: docker-compose -f docker-compose.prod.yml logs -f postgres"
echo ""
echo "🔧 관리 명령어:"
echo "   - 중지: docker-compose -f docker-compose.prod.yml down"
echo "   - 재시작: docker-compose -f docker-compose.prod.yml restart"
echo "   - 재배포: ./deploy.sh"
echo ""
echo "📝 기본 계정:"
echo "   - 사용자명: admin"
echo "   - 비밀번호: admin123"
echo "   ⚠️  첫 로그인 후 반드시 비밀번호를 변경하세요!"
echo ""
echo "=========================================="

