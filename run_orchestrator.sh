#!/usr/bin/env bash

# RanSafe SRE Orchestrator - End-to-End Pipeline Coordinator
# Continuous piping: Dynatrace MCP Client -> AI Validator -> Execution Gateway.

set -euo pipefail

# Default parameters
MODE="ransomware"
NODE_ID="node-us-east-412"

# Usage help
show_help() {
    echo "Usage: ./run_orchestrator.sh [options]"
    echo "Options:"
    echo "  --mode <normal|reallocate|ransomware>   Telemetry scenario mode (Default: ransomware)"
    echo "  --node-id <id>                          Target compute node ID (Default: node-us-east-412)"
    echo "  -h, --help                              Show this help menu"
    exit 0
}

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --node-id)
            NODE_ID="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run pipeline execution
echo "=========================================================="
echo "🛡️  RanSafe Continuous Pipeline Orchestration Starting..."
echo "Mode: ${MODE}"
echo "Node ID: ${NODE_ID}"
echo "=========================================================="

node "${SCRIPT_DIR}/agent/mcp_client.js" --mock --mode="${MODE}" --node-id="${NODE_ID}" --json-only | \
python3 "${SCRIPT_DIR}/agent/validator.py" --prompt "${SCRIPT_DIR}/agent/system_prompt.txt" --input - --json-only | \
python3 "${SCRIPT_DIR}/execution/handler.py"
