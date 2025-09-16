# gitea-mcp-local (PostgreSQL)


Local "sandbox" stack for experiments: **Gitea** + **Gitea MCP Server** in Docker, database — **PostgreSQL**. Ready for SSE connections from MCP clients (Cursor, Claude Desktop, etc.).


## Components
- **Gitea** (web interface on :3000, SSH on :2222)
- **PostgreSQL** (data in volume `pgdata`)
- **Gitea MCP Server** (SSE endpoint on :8081)


## Quick Start
```bash
cp .env.example .env
# if necessary, adjust values in .env
make up # will start db+gitea, then init.sh will create admin and token and start MCP
