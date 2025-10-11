# Dockerfile
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

# System deps
USER root
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       cron tzdata \
    && rm -rf /var/lib/apt/lists/*

# Timezone
ENV TZ=Asia/Seoul
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata

WORKDIR /app

# Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# App code
COPY app /app/app
COPY batch /app/batch
COPY scheduler/crawl.cron /etc/cron.d/crawl
COPY README.md /app/README.md

# Cron setup (time will be patched at runtime by envs)
RUN chmod 0644 /etc/cron.d/crawl && crontab /etc/cron.d/crawl

# Make sure both cron & uvicorn run
CMD bash -lc "\
  sed -i \"s/^30 8 \* \* \*/${CRON_MINUTE:-30} ${CRON_HOUR:-8} * * */\" /etc/cron.d/crawl || true && \
  crontab /etc/cron.d/crawl && \
  service cron start && \
  uvicorn app.main:app --host ${UVICORN_HOST:-0.0.0.0} --port ${UVICORN_PORT:-8000} --workers 1"