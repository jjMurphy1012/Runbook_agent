#!/usr/bin/env bash
# End-to-end smoke: register -> login -> create alert -> trigger -> SSE -> runbook
#
# Prereqs (verify yourself before running):
#   - Docker Desktop running, `docker compose up -d` succeeded
#   - backend-java reachable on $JAVA_URL (default http://localhost:8080)
#   - backend-python reachable on $PY_URL (default http://localhost:8000)
#   - Real OPENAI_API_KEY in .env (placeholder will land alert in ESCALATED)
#
# Exit code 0 iff the full chain works. Each step prints PASS/FAIL.

set -u
JAVA_URL="${JAVA_URL:-http://localhost:8080}"
PY_URL="${PY_URL:-http://localhost:8000}"
SUFFIX="$(date +%s)"
USER="smoke_${SUFFIX}"
PASS="smoke-pw-${SUFFIX}"
RULE="mysql_pool_exhausted"

step() { echo; echo "==> $1"; }
need() { command -v "$1" >/dev/null || { echo "missing $1"; exit 1; }; }
need curl
need jq

step "health checks"
curl -fsS "$JAVA_URL/api/auth/health" >/dev/null || { echo "java unhealthy"; exit 1; }
curl -fsS "$PY_URL/health"           >/dev/null || { echo "python unhealthy"; exit 1; }
echo "PASS"

step "register $USER"
curl -fsS -X POST "$JAVA_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USER\",\"password\":\"$PASS\"}" >/dev/null || { echo "register FAIL"; exit 1; }
echo "PASS"

step "login"
TOKEN=$(curl -fsS -X POST "$JAVA_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USER\",\"password\":\"$PASS\"}" | jq -r .token)
[[ -n "$TOKEN" && "$TOKEN" != "null" ]] || { echo "login FAIL"; exit 1; }
echo "PASS  token=${TOKEN:0:24}..."

step "create alert (with labels)"
ALERT_JSON=$(curl -fsS -X POST "$JAVA_URL/api/alerts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"ruleName\":\"$RULE\",\"category\":\"database\",\"severity\":\"HIGH\",\"message\":\"smoke test connection pool exhausted\",\"labels\":{\"service\":\"payment-api\",\"host\":\"db-01\"}}")
ALERT_ID=$(echo "$ALERT_JSON" | jq -r .id)
FP=$(echo "$ALERT_JSON" | jq -r .fingerprint)
[[ -n "$ALERT_ID" && "$ALERT_ID" != "null" ]] || { echo "create FAIL: $ALERT_JSON"; exit 1; }
echo "PASS  id=$ALERT_ID fingerprint=$FP"

step "obtain stream token (5-min TTL, scoped to this alertId)"
STREAM_TOKEN=$(curl -fsS -X POST "$JAVA_URL/api/stream/token/$ALERT_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -r .token)
[[ -n "$STREAM_TOKEN" && "$STREAM_TOKEN" != "null" ]] || { echo "stream token FAIL"; exit 1; }
echo "PASS  stream_token=${STREAM_TOKEN:0:24}..."

step "open SSE (no Authorization; token in query string)"
SSE_OUT=$(mktemp)
curl -fsS -N --max-time 8 "$JAVA_URL/api/stream/$ALERT_ID?token=$STREAM_TOKEN" > "$SSE_OUT" &
SSE_PID=$!
sleep 1

step "trigger workflow"
curl -fsS -X POST "$JAVA_URL/api/alerts/$ALERT_ID/trigger" \
  -H "Authorization: Bearer $TOKEN" >/dev/null || { echo "trigger FAIL"; kill $SSE_PID 2>/dev/null; exit 1; }
echo "PASS"

step "wait for runbook (poll alert status up to 90s)"
STATUS=""
for _ in $(seq 1 45); do
  STATUS=$(curl -fsS "$JAVA_URL/api/alerts/$ALERT_ID" -H "Authorization: Bearer $TOKEN" | jq -r .status)
  case "$STATUS" in
    RESOLVED|ESCALATED) break ;;
  esac
  sleep 2
done
wait $SSE_PID 2>/dev/null

step "SSE event sample"
head -20 "$SSE_OUT"
rm -f "$SSE_OUT"

step "final status: $STATUS"
if [[ "$STATUS" == "RESOLVED" ]]; then
  echo "ALL PASS"
  exit 0
else
  echo "FAIL — alert ended in $STATUS (expected RESOLVED). Check OPENAI_API_KEY and python logs."
  exit 1
fi
