#!/bin/bash
# demo-mcp.sh - Explainor MCP Server Demo Script
# MCP's 1st Birthday Hackathon - kaiser-data

set -e

MCP_URL="https://kaiser-data-mcp-1st-birthday-explainor.hf.space/gradio_api"
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🎭 Explainor MCP Server Demo${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 1. Health Check
echo -e "${YELLOW}[1/3] Checking MCP Server Health...${NC}"
SCHEMA=$(curl -s "${MCP_URL}/mcp/schema" 2>/dev/null)

if [ -z "$SCHEMA" ]; then
    echo -e "${RED}✗ Server not responding. It may be sleeping.${NC}"
    echo -e "  Visit: https://kaiser-data-mcp-1st-birthday-explainor.hf.space"
    exit 1
fi

TOOL_COUNT=$(echo "$SCHEMA" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
echo -e "${GREEN}✓ Connected! Found ${TOOL_COUNT} tools${NC}"
echo ""

# 2. List Available Tools
echo -e "${YELLOW}[2/3] Available MCP Tools:${NC}"
echo "$SCHEMA" | python3 -c "
import sys, json
tools = json.load(sys.stdin)
for t in tools:
    name = t['name'].replace('MCP_1st_Birthday_explainor_', '')
    print(f'  • {name}')
" 2>/dev/null
echo ""

# 3. Demo Call
echo -e "${YELLOW}[3/3] Demo: Explain 'AI' as a 5-Year-Old...${NC}"
echo ""

# Make async call
RESPONSE=$(curl -s -X POST "${MCP_URL}/call/process_and_explain" \
    -H "Content-Type: application/json" \
    -d '{"data": ["Artificial Intelligence", "👶 5-Year-Old", "👤 Just me"]}')

EVENT_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('event_id',''))" 2>/dev/null)

if [ -z "$EVENT_ID" ]; then
    echo -e "${RED}✗ Failed to start request${NC}"
    exit 1
fi

echo -e "  Request ID: ${EVENT_ID}"
echo -e "  Waiting for response..."

# Poll for result (with timeout)
for i in {1..30}; do
    sleep 2
    RESULT=$(curl -s "${MCP_URL}/call/process_and_explain/${EVENT_ID}" 2>/dev/null)

    if echo "$RESULT" | grep -q "event: complete"; then
        EXPLANATION=$(echo "$RESULT" | grep "^data:" | head -1 | sed 's/^data: //' | python3 -c "import sys,json; print(json.load(sys.stdin)[0])" 2>/dev/null)
        echo ""
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}  👶 5-Year-Old says:${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "  $EXPLANATION"
        echo ""
        echo -e "${GREEN}✓ Demo complete!${NC}"
        exit 0
    fi
done

echo -e "${RED}✗ Timeout waiting for response${NC}"
exit 1
