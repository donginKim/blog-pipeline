#!/bin/bash

echo "🔍 관리자 계정 확인"
echo "=========================================="
echo ""

# Docker 컨테이너에서 확인
echo "1️⃣  데이터베이스에서 사용자 확인:"
echo "---"
docker exec naver-monitor-backend python3 -c "
import sys
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://naver_monitor:changeme@db:5432/naver_monitor')

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT id, username, email, hashed_password, is_active FROM users'))
        rows = result.fetchall()
        
        if rows:
            print('📋 등록된 사용자:')
            print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            for row in rows:
                status = '✅ 활성' if row[4] else '❌ 비활성'
                print(f'  ID: {row[0]} | {row[1]} | {row[2]} | {status}')
                print(f'  비밀번호: {row[3]}')
            print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        else:
            print('⚠️  등록된 사용자가 없습니다.')
            print('')
            print('데이터베이스를 초기화하세요:')
            print('  docker exec naver-monitor-backend python3 init-db-postgres.py')
except Exception as e:
    print(f'❌ 오류: {e}')
    sys.exit(1)
" 2>/dev/null || echo "❌ 백엔드 컨테이너가 실행 중이지 않습니다."

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 로그인 테스트
echo "2️⃣  로그인 테스트:"
echo "---"

PUBLIC_IP=${1:-"49.50.134.250"}

echo "📝 testuser로 로그인 시도..."
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpassword123"}' \
  http://${PUBLIC_IP}:8001/api/auth/login)

if echo "$RESPONSE" | grep -q "access_token"; then
  echo "✅ testuser 로그인 성공!"
  echo "   $RESPONSE" | python3 -m json.tool 2>/dev/null || echo "   $RESPONSE"
else
  echo "❌ testuser 로그인 실패"
  echo "   $RESPONSE"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 비밀번호 변경 방법
echo "3️⃣  비밀번호 변경 방법:"
echo "---"
echo ""
echo "방법 1: 계정 관리 스크립트 (권장)"
echo "  docker exec -it naver-monitor-backend python3 update-account.py"
echo ""
echo "방법 2: 수동 변경"
echo "  docker exec -it naver-monitor-backend python3 -c \\"
echo "    \"from sqlalchemy import create_engine, text; import os; \\"
echo "    engine = create_engine(os.getenv('DATABASE_URL')); \\"
echo "    conn = engine.connect(); \\"
echo "    conn.execute(text(\\\"UPDATE users SET hashed_password = 'new_password' WHERE username = 'testuser'\\\")); \\"
echo "    conn.commit(); \\"
echo "    print('✅ 비밀번호 변경 완료')\""
echo ""
echo "방법 3: 데이터베이스 재초기화"
echo "  docker exec naver-monitor-backend python3 init-db-postgres.py"
echo ""

echo "=========================================="
echo ""
echo "💡 기본 로그인 정보:"
echo "   - 사용자명: testuser"
echo "   - 비밀번호: testpassword123"
echo ""
echo "📍 로그인 URL:"
echo "   - API 문서: http://${PUBLIC_IP}:8001/docs"
echo "   - 프론트엔드: http://${PUBLIC_IP}:3000"
echo ""

