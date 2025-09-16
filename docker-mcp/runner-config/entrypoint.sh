#!/bin/bash
set -e

echo "==> Starting Claude Code Runner"

# Ensure PATH includes Claude Code
export PATH="/root/.local/bin:$PATH"

# Verify Claude Code is available
echo "==> Checking Claude Code installation..."
if command -v claude &> /dev/null; then
    echo "✅ Claude Code CLI is available"
    claude --version || echo "Claude Code installed but may need authentication"
else
    echo "⚠️  Claude Code CLI not found in PATH"
fi

# Wait for MCP server to be ready (optional)
echo "==> Checking MCP server connectivity..."
if curl -s http://mcp:8080/health > /dev/null 2>&1; then
    echo "✅ MCP server is accessible"
else
    echo "⚠️  MCP server not accessible (will work without it)"
fi

echo "==> Starting Actions runner daemon..."
# Start the original act_runner entrypoint
exec /sbin/tini -- run.sh