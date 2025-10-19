#!/bin/bash

echo "🔧 데이터베이스 즉시 수정"
echo "=========================================="
echo ""

# 백엔드 컨테이너 확인
if ! docker ps | grep -q naver-monitor-backend; then
    echo "❌ naver-monitor-backend 컨테이너가 실행 중이지 않습니다."
    echo ""
    echo "컨테이너를 시작하세요:"
    echo "  docker compose -f docker-compose.prod.yml up -d"
    exit 1
fi

echo "✅ 백엔드 컨테이너 확인"
echo ""

# 1. 현재 상태 확인
echo "1️⃣  현재 데이터베이스 상태:"
echo "---"
docker exec naver-monitor-backend python3 -c "
import os
from sqlalchemy import create_engine, text, inspect

DATABASE_URL = os.getenv('DATABASE_URL')
print(f'데이터베이스: {DATABASE_URL}')
print()

try:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if tables:
        print(f'✅ 테이블 목록 ({len(tables)}개):')
        for table in tables:
            print(f'  - {table}')
    else:
        print('❌ 테이블이 없습니다.')
        
    print()
    
    # users 테이블 확인
    if 'users' in tables:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT COUNT(*) FROM users'))
            count = result.fetchone()[0]
            print(f'👥 users 테이블: {count}명의 사용자')
    else:
        print('❌ users 테이블이 없습니다.')
        
except Exception as e:
    print(f'❌ 오류: {e}')
" 2>&1

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 2. 초기화 실행
echo "2️⃣  데이터베이스 초기화 실행:"
echo "---"
docker exec naver-monitor-backend python3 init-db-postgres.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 3. 초기화 후 상태
echo "3️⃣  초기화 후 상태:"
echo "---"
docker exec naver-monitor-backend python3 -c "
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL')

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT id, username, email, is_active FROM users'))
        rows = result.fetchall()
        
        if rows:
            print('✅ 사용자 목록:')
            for row in rows:
                status = '✅' if row[3] else '❌'
                print(f'  {status} ID: {row[0]} | {row[1]} | {row[2]}')
        else:
            print('❌ 사용자가 없습니다.')
            
except Exception as e:
    print(f'❌ 오류: {e}')
" 2>&1

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 4. 로그인 테스트
echo "4️⃣  로그인 테스트:"
echo "---"
PUBLIC_IP=${1:-"49.50.134.250"}

RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpassword123"}' \
  http://${PUBLIC_IP}:8001/api/auth/login)

if echo "$RESPONSE" | grep -q "access_token"; then
  echo "✅ 로그인 성공!"
  echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -10
else
  echo "❌ 로그인 실패"
  echo "$RESPONSE"
fi

echo ""
echo "=========================================="
echo "✅ 수정 완료!"
echo "=========================================="
echo ""
echo "🔐 로그인 정보:"
echo "   사용자명: testuser"
echo "   비밀번호: testpassword123"
echo ""
echo "🌐 접속 URL:"
echo "   http://${PUBLIC_IP}:3000"
echo "   http://${PUBLIC_IP}:8001/docs"
echo ""

