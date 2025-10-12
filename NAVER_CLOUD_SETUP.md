# 네이버 클라우드 설정 가이드

네이버 클라우드 플랫폼에서 Naver Monitor를 실행하는 방법입니다.

## 🌐 공인 IP 정보

```
공인 IP: 49.50.134.250
```

---

## 🚀 빠른 시작

### 1️⃣ 서버 접속

```bash
# SSH 접속
ssh root@49.50.134.250

# 또는
ssh -i your-key.pem root@49.50.134.250
```

### 2️⃣ 프로젝트 업로드

```bash
# 방법 A: Git 클론
git clone https://github.com/yourusername/naver-monitor.git
cd naver-monitor

# 방법 B: SCP로 업로드 (로컬에서)
scp -r naver-monitor/ root@49.50.134.250:/root/
```

### 3️⃣ 자동 설정 및 시작

```bash
# 공인 IP 설정 및 서버 시작
./configure-public-ip.sh 49.50.134.250
```

또는 수동:

```bash
# 정리
./emergency-cleanup.sh

# 설정
./setup-server.sh

# 시작
./start-server.sh
```

---

## 🔒 방화벽 설정 (중요!)

### 네이버 클라우드 ACG 설정

#### 1. 콘솔 접속
```
https://console.ncloud.com
→ Server
→ ACG (Access Control Group)
```

#### 2. 인바운드 규칙 추가

| 프로토콜 | 포트 | 접근 소스 | 설명 |
|----------|------|-----------|------|
| TCP | 22 | My IP | SSH (이미 설정됨) |
| TCP | 8001 | 0.0.0.0/0 | 백엔드 API |
| TCP | 3000 | 0.0.0.0/0 | 프론트엔드 (선택) |

#### 3. 적용

```
규칙 추가 → 저장 → 적용
```

---

## 📋 접속 URL

### API 서버

```
http://49.50.134.250:8001
http://49.50.134.250:8001/docs (Swagger UI)
```

### 프론트엔드 (Node.js 설치 시)

```
http://49.50.134.250:3000
```

### 테스트

```bash
# 로컬에서 테스트
curl http://49.50.134.250:8001/

# 브라우저
http://49.50.134.250:8001/docs
```

---

## 🎯 완전 자동 설정

### 스크립트 실행

```bash
# 서버에서 실행
./configure-public-ip.sh 49.50.134.250
```

**자동 수행:**
1. ✅ CORS 설정 업데이트
2. ✅ 환경 변수 설정
3. ✅ 서버 재시작
4. ✅ 접속 URL 표시

---

## 🔧 프론트엔드 추가 (선택사항)

### Node.js 설치

```bash
# Node.js 18 설치
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 버전 확인
node --version
npm --version
```

### 프론트엔드 설치 및 시작

```bash
# 패키지 설치
cd frontend
npm install

# 빌드 (프로덕션)
npm run build

# 서빙
npx serve -s dist -p 3000 &

# 또는 개발 모드
npm run dev -- --host 0.0.0.0 &
```

---

## 🛡️ 보안 설정

### 방화벽 (UFW)

```bash
# UFW 활성화
sudo ufw enable

# 필요한 포트만 열기
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8001/tcp  # API
sudo ufw allow 3000/tcp  # Frontend (선택)

# 상태 확인
sudo ufw status
```

### 비밀번호 변경

```bash
# 기본 계정 비밀번호 변경 (필수!)
python3 update-account.py

# 선택: 3 (비밀번호 변경)
# 사용자 ID: 1
# 새 비밀번호 입력
```

### SSL/HTTPS 설정 (권장)

```bash
# Certbot 설치
sudo apt-get install certbot

# 도메인이 있는 경우
sudo certbot certonly --standalone -d yourdomain.com

# Nginx 설치 및 설정
sudo apt-get install nginx

# Nginx 설정 파일
sudo nano /etc/nginx/sites-available/naver-monitor

# 내용:
server {
    listen 80;
    server_name 49.50.134.250;
    
    location /api/ {
        proxy_pass http://localhost:8001/;
    }
    
    location / {
        proxy_pass http://localhost:3000/;
    }
}

# 활성화
sudo ln -s /etc/nginx/sites-available/naver-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📊 모니터링

### 서버 상태 확인

```bash
# 프로세스
ps aux | grep server-debug.py

# 포트
netstat -tuln | grep -E "8001|3000"

# 리소스
top
htop

# 디스크
df -h
```

### 로그 모니터링

```bash
# 실시간 로그
tail -f logs/server.log

# 에러만
grep ERROR logs/server.log

# 최근 100줄
tail -100 logs/server.log
```

---

## 🎯 접속 테스트

### API 서버 테스트

```bash
# 헬스체크
curl http://49.50.134.250:8001/

# 로그인
curl -X POST http://49.50.134.250:8001/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"testuser","password":"testpassword123"}'

# API 문서 (브라우저)
http://49.50.134.250:8001/docs
```

### 프론트엔드 테스트

```bash
# 브라우저에서
http://49.50.134.250:3000

# 로그인
사용자명: testuser
비밀번호: testpassword123
```

---

## 💡 유용한 팁

### 1. 도메인 연결

```bash
# 네이버 클라우드 DNS 설정
yourdomain.com → 49.50.134.250

# hosts 파일 (테스트용)
sudo nano /etc/hosts
49.50.134.250 naver-monitor.local

# 접속
http://naver-monitor.local:8001
```

### 2. 자동 시작

```bash
# systemd 서비스 등록
sudo cp naver-monitor.service /etc/systemd/system/
sudo systemctl enable naver-monitor
sudo systemctl start naver-monitor

# 서버 재부팅 시 자동 시작
```

### 3. 백업 자동화

```bash
# Cron 작업
crontab -e

# 매일 새벽 2시 백업
0 2 * * * cp /root/blog-pipeline/naver_monitor.db /root/backups/naver_monitor_$(date +\%Y\%m\%d).db
```

---

## 🔥 문제 해결

### Q1: 외부에서 접속 안 됨

**확인:**
```bash
# 서버 내부에서는 접속 가능한가?
curl http://localhost:8001/

# 방화벽 확인
sudo ufw status

# ACG 확인 (네이버 클라우드 콘솔)
```

**해결:**
1. 네이버 클라우드 ACG에서 포트 8001, 3000 열기
2. UFW에서 포트 허용
3. 서버 재시작

---

### Q2: CORS 오류

**증상:**
```
Access to fetch at 'http://49.50.134.250:8001' from origin 'http://49.50.134.250:3000' has been blocked by CORS policy
```

**해결:**
```bash
# CORS 설정 확인
cat .env | grep CORS

# 다시 설정
./configure-public-ip.sh 49.50.134.250

# 서버 재시작
./stop-server.sh && ./start-server.sh
```

---

### Q3: 프론트엔드 API 연결 안 됨

**해결:**

프론트엔드 API URL 설정:

```bash
# frontend/.env 생성
echo "VITE_API_URL=http://49.50.134.250:8001" > frontend/.env

# 재빌드
cd frontend
npm run build

# 재시작
./stop-server.sh && ./start-server.sh
```

---

## ✅ 최종 체크리스트

배포 완료 확인:

- [ ] 서버 실행 중: `ps aux | grep server-debug.py`
- [ ] 포트 열림: `netstat -tuln | grep 8001`
- [ ] ACG 설정: 네이버 클라우드 콘솔 확인
- [ ] API 접속: `curl http://49.50.134.250:8001/`
- [ ] 브라우저 접속: http://49.50.134.250:8001/docs
- [ ] 로그인 테스트: testuser / testpassword123
- [ ] 비밀번호 변경: `python3 update-account.py`

---

## 🎉 완료!

**접속 URL:**

```
🌐 API 서버: http://49.50.134.250:8001
📖 API 문서: http://49.50.134.250:8001/docs
🎨 프론트엔드: http://49.50.134.250:3000 (Node.js 설치 시)

🔐 로그인:
   사용자명: testuser
   비밀번호: testpassword123
```

**서버에서 실행:**

```bash
# 공인 IP 설정 및 시작
./configure-public-ip.sh 49.50.134.250
```

**완료!** 🚀

---

**주의사항:**

1. ⚠️ **ACG 설정 필수**: 네이버 클라우드 콘솔에서 포트 열기
2. ⚠️ **비밀번호 변경**: 보안을 위해 기본 비밀번호 변경
3. ⚠️ **HTTPS 권장**: 실제 운영 시 SSL 인증서 설정

---

**네이버 클라우드에서 완벽하게 작동합니다!** ✨

