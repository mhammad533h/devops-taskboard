#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$(dirname "$(readlink -f "$0")")")"
url="${APP_URL:-http://127.0.0.1:8080}"
marker="persistence-$(date +%s)-$RANDOM"

echo "Creating task: $marker"
curl -fsS -X POST --data-urlencode "title=$marker" "$url/tasks" >/dev/null
curl -fsS "$url/" | grep -Fq "$marker"

docker compose down
docker compose up -d --build

for attempt in $(seq 1 30); do
  if curl -fsS "$url/" 2>/dev/null | grep -Fq "$marker"; then
    echo "PASS: $marker survived container recreation in the named volume"
    docker compose ps
    docker volume ls
    exit 0
  fi
  sleep 2
done
echo "FAIL: task was not found after container recreation" >&2
exit 1
