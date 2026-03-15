#!/bin/bash

# Concurrency test for Assignment Hub API
# Run this from your local machine

set -e

# Configuration
BASE_URL="https://assignment-hub.duckdns.org/api"
CONCURRENCY=5          # number of simultaneous users
REQUESTS=5             # total requests (must be >= concurrency)
DEPARTMENT="cs"        # any valid department

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting concurrency test with $CONCURRENCY concurrent users...${NC}"

# 1. Get a fresh token
echo -e "${YELLOW}\n[1] Getting a new token...${NC}"
TOKEN=$(curl -s -X POST "$BASE_URL/tokens/" -H "Content-Type: application/json" -d "{}" | jq -r '.token')
if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo -e "${RED}Failed to get token. Check your network and server.${NC}"
    exit 1
fi
echo -e "${GREEN}Token: $TOKEN${NC}"

# 2. Prepare payload for generate endpoint
PAYLOAD="{\"token\":\"$TOKEN\",\"name\":\"Test User\",\"matric_number\":\"12345\",\"email\":\"test@example.com\",\"department\":\"$DEPARTMENT\"}"
echo "$PAYLOAD" > /tmp/payload.json

# 3. Test token endpoint (lightweight)
echo -e "${YELLOW}\n[2] Testing token endpoint with $CONCURRENCY concurrent requests...${NC}"
if command -v ab &> /dev/null; then
    ab -n $REQUESTS -c $CONCURRENCY "$BASE_URL/tokens/"
else
    # Fallback using curl in background
    pids=()
    for i in $(seq 1 $REQUESTS); do
        curl -s -X POST "$BASE_URL/tokens/" -H "Content-Type: application/json" -d "{}" > /dev/null &
        pids+=($!)
        if [ ${#pids[@]} -ge $CONCURRENCY ]; then
            wait ${pids[@]}
            pids=()
        fi
    done
    wait ${pids[@]}
    echo -e "${GREEN}Token endpoint test completed (fallback method).${NC}"
fi

# 4. Test generate endpoint (heavy)
echo -e "${YELLOW}\n[3] Testing generate endpoint with $CONCURRENCY concurrent requests (may take a few minutes)...${NC}"
if command -v ab &> /dev/null; then
    ab -n $REQUESTS -c $CONCURRENCY -p /tmp/payload.json -T application/json "$BASE_URL/generate/"
else
    # Fallback with background curl
    pids=()
    for i in $(seq 1 $REQUESTS); do
        curl -s -X POST "$BASE_URL/generate/" -H "Content-Type: application/json" -d @"$PAYLOAD_FILE" > /dev/null &
        pids+=($!)
        if [ ${#pids[@]} -ge $CONCURRENCY ]; then
            wait ${pids[@]}
            pids=()
        fi
    done
    wait ${pids[@]}
    echo -e "${GREEN}Generate endpoint test completed (fallback method).${NC}"
fi

# 5. Cleanup
rm -f /tmp/payload.json

echo -e "${GREEN}\nAll tests finished. Check the results above.${NC}"