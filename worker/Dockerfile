FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

USER root
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends cron tzdata \
 && rm -rf /var/lib/apt/lists/*

# 크론/백그라운드에서도 동일 경로 사용
ENV TZ=Asia/Seoul \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 타임존 적용
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime \
 && dpkg-reconfigure -f noninteractive tzdata

WORKDIR /app

# 워커에 필요한 최소 패키지 설치 (backend/requirements.txt 못 복사하므로 직접 명시)
# - playwright는 베이스 이미지에 포함되어 있지만 버전 호환을 위해 명시
RUN pip install --no-cache-dir \
      "SQLAlchemy==2.0.35" \
      "pymysql==1.1.1" \
      "python-dotenv==1.0.1" \
      "playwright==1.47.0" \
      "openai>=1.30.0" \
      "requests>=2.32.3"

# (옵션) 혹시라도 브라우저 캐시 경로 이슈 대비해 강제 설치하고 싶다면 주석 해제
# RUN python -m playwright install --with-deps chromium

# entrypoint.sh 사용 (유저 crontab 동적 생성)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]