#!/usr/bin/env bash
set -euo pipefail

# Run as root on Amazon Linux 2023 from the repository directory.
if [[ $(id -u) -ne 0 ]]; then
  echo "Run this script with sudo" >&2
  exit 1
fi

dnf install -y docker git openssl
systemctl enable --now docker

install -d -m 0755 /usr/local/lib/docker/cli-plugins
curl -fL --retry 3 https://github.com/docker/compose/releases/download/v5.6.0/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod 0755 /usr/local/lib/docker/cli-plugins/docker-compose
docker compose version

curl -fL --retry 3 https://github.com/docker/buildx/releases/download/v0.21.2/buildx-v0.21.2.linux-amd64 -o /usr/local/lib/docker/cli-plugins/docker-buildx
chmod 0755 /usr/local/lib/docker/cli-plugins/docker-buildx
docker buildx version

cd "$(dirname "$(dirname "$(readlink -f "$0")")")"
if [[ ! -f .env ]]; then
  umask 077
  cat > .env <<EOF
POSTGRES_DB=taskboard
POSTGRES_USER=taskboard
POSTGRES_PASSWORD=$(openssl rand -hex 24)
EOF
fi
chmod 600 .env
docker compose up -d --build
docker compose ps
