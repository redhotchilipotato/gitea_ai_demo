#!/usr/bin/env bash
set -euo pipefail


ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"


if [ ! -f .env ]; then
echo "Create .env based on .env.example before running"; exit 1
fi
source .env


# 1) Make sure gitea is running (if this script was run directly)
if ! docker compose ps gitea >/dev/null 2>&1; then
echo "==> Starting db+gitea..."
docker compose up -d db gitea
fi


# 2) Wait for Gitea to be ready
GITEA_WEB="http://localhost:${HTTP_PORT:-3000}/"
echo "==> Waiting for Gitea readiness at ${GITEA_WEB} ..."
until curl -fsS "$GITEA_WEB" >/dev/null 2>&1; do
sleep 2
printf "."
done
echo


# 3) Create/check administrator
echo "==> Creating/checking administrator '${GITEA_ADMIN_USER}'..."
docker exec -u 1000:1000 gitea gitea admin user create \
--username "${GITEA_ADMIN_USER}" \
--password "${GITEA_ADMIN_PASS}" \
--email "${GITEA_ADMIN_EMAIL}" \
--admin \
--must-change-password=false \
-c /data/gitea/conf/app.ini \
|| echo "(skipping: user probably already exists)"


# 4) Create token via REST API
echo "==> Generating personal token via API..."
BASIC_AUTH="$(printf '%s:%s' "$GITEA_ADMIN_USER" "$GITEA_ADMIN_PASS" | base64)"
TOKEN_NAME="mcp-local-$(date +%s)"
API_URL="${GITEA_ROOT_URL%/}/api/v1/users/${GITEA_ADMIN_USER}/tokens"


NEW_TOKEN="$(curl -fsS -X POST "$API_URL" \
-H "Authorization: Basic $BASIC_AUTH" \
-H "Content-Type: application/json" \
-d "{\"name\":\"$TOKEN_NAME\",\"scopes\":[\"all\"]}" \
| sed -n 's/.*\"sha1\":\"\([^\"]*\)\".*/\1/p')"


if [ -z "$NEW_TOKEN" ]; then
echo "Failed to get token via API. Check login/password and API availability." >&2
exit 1
fi


# 5) Write token to .env
if grep -q '^GITEA_TOKEN=' .env; then
sed -i.bak "s|^GITEA_TOKEN=.*$|GITEA_TOKEN=${NEW_TOKEN}|" .env
else
echo "GITEA_TOKEN=${NEW_TOKEN}" >> .env
fi


# 5.1) Generate registration token for Actions Runner
echo "==> Generating registration token for Actions Runner..."
RUNNER_TOKEN_NAME="runner-token-$(date +%s)"
RUNNER_API_URL="${GITEA_ROOT_URL%/}/api/v1/repos/admin/actions/runners/registration-token"

# Create repository via API if it doesn't exist
curl -fsS -X POST "${GITEA_ROOT_URL%/}/api/v1/user/repos" \
-H "Authorization: token $NEW_TOKEN" \
-H "Content-Type: application/json" \
-d '{"name":"test-repo","private":false,"description":"Test repository for Actions"}' \
>/dev/null 2>&1 || echo "(skipping: repository possibly already exists)"

# Get runner registration token (try different endpoints)
RUNNER_REG_TOKEN=""

# Try different API endpoints to get registration token
for endpoint in "admin/runners/registration-token" "user/actions/runners/registration-token" "orgs/${GITEA_ADMIN_USER}/actions/runners/registration-token"; do
  RUNNER_REG_TOKEN="$(curl -fsS -X POST "${GITEA_ROOT_URL%/}/api/v1/${endpoint}" \
    -H "Authorization: token $NEW_TOKEN" \
    -H "Content-Type: application/json" \
    2>/dev/null | sed -n 's/.*\"token\":\"\([^\"]*\)\".*/\1/p')"
  
  if [ -n "$RUNNER_REG_TOKEN" ]; then
    echo "Got registration token via: $endpoint"
    break
  fi
done

if [ -n "$RUNNER_REG_TOKEN" ]; then
if grep -q '^GITEA_RUNNER_TOKEN=' .env; then
sed -i.bak2 "s|^GITEA_RUNNER_TOKEN=.*$|GITEA_RUNNER_TOKEN=${RUNNER_REG_TOKEN}|" .env
else
echo "GITEA_RUNNER_TOKEN=${RUNNER_REG_TOKEN}" >> .env
fi
echo "Runner token: ${RUNNER_REG_TOKEN}"
else
echo "Failed to get runner registration token" >&2
fi


# 6) Start/restart MCP and Runner
echo "==> Starting MCP..."
docker compose up -d mcp

echo "==> Starting Actions Runner..."
docker compose up -d runner


echo "==> Ready!"
echo "Admin: ${GITEA_ADMIN_USER} / ${GITEA_ADMIN_PASS}"
echo "Token: ${NEW_TOKEN}"
echo "MCP SSE endpoint: http://localhost:${MCP_PORT:-8081}/sse"
echo "Gitea Actions enabled and runner configured"
