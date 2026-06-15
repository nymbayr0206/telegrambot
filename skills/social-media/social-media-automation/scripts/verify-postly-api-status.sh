#!/bin/bash
# verify-postly-api-status.sh
# Checks all Postly-related domains and reports what's running where.
# Usage: bash verify-postly-api-status.sh [secret]
# If secret omitted, reads from HERMES_SECRET env var.

set -euo pipefail

SECRET="${1:-${HERMES_SECRET:-}}"
if [ -z "$SECRET" ]; then
  echo "ERROR: Provide x-hermes-secret as first arg or set HERMES_SECRET env var"
  exit 1
fi

echo "=== Postly Domain Status Check ==="
echo ""

check_domain() {
  local label="$1" url="$2" expected="$3"
  local resp
  resp=$(curl -s -o /dev/null -w "%{http_code}" -H "x-hermes-secret: $SECRET" "$url" 2>&1)
  printf "%-35s %s → %s" "[$label]" "$url" "$resp"
  if [ "$resp" = "$expected" ]; then
    echo " ✓ (expected)"
  elif [ "$resp" = "404" ]; then
    echo " ⚠ Not deployed / route missing"
  elif [ "$resp" = "401" ]; then
    echo " ✗ Wrong secret"
  elif [ "$resp" = "000" ]; then
    echo " ✗ DNS / connection failed"
  elif [ "$resp" = "307" ] || [ "$resp" = "301" ]; then
    echo " ↻ Redirect (follow with -L)"
  elif [ "$resp" = "400" ]; then
    echo " ✓ Route exists (400 = payload issue, auth ok)"
  else
    echo " ? Unexpected ($resp)"
  fi
}

echo "--- Brand endpoints ---"
check_domain "www.postly.mn" "https://www.postly.mn/api/hermes/postly/brands" "200"
check_domain "postly.mn (no www)" "https://postly.mn/api/hermes/postly/brands" "200"
check_domain "agenticforceweb.vercel.app" "https://agenticforceweb.vercel.app/api/hermes/postly/brands" "200"
check_domain "postly.vercel.app (Vue SPA)" "https://postly.vercel.app/api/hermes/postly/brands" "200"

echo ""
echo "--- Existing Hermes routes (should work) ---"
check_domain "import-news (POST)" "https://www.postly.mn/api/hermes/import-news" "400"

echo ""
echo "=== Inspecting www.postly.mn body ==="
body=$(curl -s -H "x-hermes-secret: $SECRET" \
  "https://www.postly.mn/api/hermes/postly/brands" 2>&1 | head -c 300)
if echo "$body" | grep -qi "brands\|brandName" 2>/dev/null; then
  echo "→ Postly backend IS deployed on www.postly.mn (JSON brand data returned)"
elif echo "$body" | grep -qi "AgenticForce\|<html" 2>/dev/null; then
  echo "→ www.postly.mn returns AgenticForce HTML (404 — route not deployed yet)"
  echo "  Check: git push succeeded? Vercel deployment may still be building."
elif echo "$body" | grep -qi "unauthorized\|Unauthorized\|401" 2>/dev/null; then
  echo "→ Route exists but x-hermes-secret is wrong"
else
  echo "→ Response: $(echo "$body" | head -c 150)"
fi

echo ""
echo "=== Quick health check ==="
echo "To test: curl -s -H 'x-hermes-secret: $SECRET' 'https://www.postly.mn/api/hermes/postly/brands' | python3 -m json.tool 2>/dev/null || echo '(waiting for Vercel deploy)'"
