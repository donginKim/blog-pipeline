#!/usr/bin/env bash
set -euo pipefail

: "${CRON_SCHEDULE:=*/30 * * * *}"   # 기본: 30분마다
: "${TZ:=Asia/Seoul}"

cat >/tmp/cronfile <<EOF
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
TZ=${TZ}
PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
PYTHONUNBUFFERED=1
PYTHONPATH=/app

${CRON_SCHEDULE} cd /app && /usr/local/bin/python -m app.jobs.run_crawl >> /var/log/cron.log 2>&1
EOF

crontab /tmp/cronfile
touch /var/log/cron.log
service cron start
tail -n +1 -F /var/log/cron.log