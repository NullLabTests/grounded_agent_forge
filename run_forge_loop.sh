#!/usr/bin/env bash
# =============================================================================
#  Grounded Agent Forge — Evolution Loop Automation
# =============================================================================
#  This script starts the infinite agent evolution loop with environment
#  validation, proper signal handling, and logging.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

FORGE_PID=""

cleanup() {
    echo -e "\n${YELLOW}Shutting down forge...${NC}"
    if [ -n "$FORGE_PID" ]; then
        kill "$FORGE_PID" 2>/dev/null || true
        wait "$FORGE_PID" 2>/dev/null || true
    fi
    echo -e "${GREEN}Forge stopped.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

print_banner() {
    echo -e "${BLUE}"
    echo "  ╔══════════════════════════════════════════╗"
    echo "  ║        Grounded Agent Forge              ║"
    echo "  ║   Evolving agent blueprints with 🧬      ║"
    echo "  ╚══════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_env() {
    local missing=0

    if [ -z "${LLM_API_KEY:-}" ]; then
        if [ -f .env ]; then
            echo -e "${YELLOW}Loading .env file...${NC}"
            set -a
            source .env
            set +a
        fi
    fi

    if [ -z "${LLM_API_KEY:-}" ]; then
        echo -e "${RED}ERROR: LLM_API_KEY is not set${NC}"
        echo "  Set it in your environment or create a .env file."
        echo "  Example: echo 'LLM_API_KEY=your_key_here' >> .env"
        missing=1
    fi

    if ! command -v python3 &>/dev/null; then
        echo -e "${RED}ERROR: python3 not found${NC}"
        missing=1
    fi

    if ! python3 -c "import agent_forge" 2>/dev/null; then
        echo -e "${YELLOW}WARNING: agent_forge module not installed. Running pip install...${NC}"
        pip install -e ".[forge]" 2>/dev/null || {
            echo -e "${RED}ERROR: Failed to install dependencies${NC}"
            missing=1
        }
    fi

    return "$missing"
}

print_banner

echo -e "${BLUE}Validating environment...${NC}"
if ! check_env; then
    echo -e "${RED}Environment validation failed. Exiting.${NC}"
    exit 1
fi
echo -e "${GREEN}Environment OK${NC}"

echo -e "${BLUE}Starting evolution loop...${NC}"
python -m agent_forge.orchestrator &
FORGE_PID=$!

echo -e "${GREEN}Forge is running (PID: $FORGE_PID)${NC}"
echo -e "  Dashboard: ${BLUE}http://localhost:${DASHBOARD_PORT:-8000}${NC}"
echo -e "  Press Ctrl+C to stop.\n"

wait "$FORGE_PID"
