#!/bin/bash

# Script to trigger code review via HTTP call to the code review service
# Usage: ./trigger_review.sh <repo_url> <branch> [base_branch]

set -e

REPO_URL="$1"
BRANCH="${2:-main}"
BASE_BRANCH="${3:-main}"
REVIEW_SERVICE="http://code-review-service:5000"

if [ -z "$REPO_URL" ]; then
    echo "Usage: $0 <repo_url> <branch> [base_branch]"
    echo "Example: $0 http://gitea:3000/admin/myrepo.git feature-branch main"
    exit 1
fi

echo "🔍 Requesting code review..."
echo "Repository: $REPO_URL"
echo "Branch: $BRANCH"
echo "Base Branch: $BASE_BRANCH"
echo ""

# Make HTTP request to code review service
response=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "{\"repo_url\":\"$REPO_URL\",\"branch\":\"$BRANCH\",\"base_branch\":\"$BASE_BRANCH\"}" \
    "$REVIEW_SERVICE/review")

# Check if request was successful
if [ $? -eq 0 ]; then
    echo "✅ Code review completed!"
    echo ""
    # Try to format JSON, fallback to raw output
    if command -v jq >/dev/null 2>&1; then
        echo "$response" | jq .
    elif command -v python3 >/dev/null 2>&1; then
        echo "$response" | python3 -m json.tool
    else
        echo "$response"
    fi
else
    echo "❌ Code review request failed"
    echo "$response"
    exit 1
fi