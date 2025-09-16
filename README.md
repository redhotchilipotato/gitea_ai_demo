# Gitea + AI (Claude Code) Demo
Repository contains a Docker-based demo setup showcasing an experimental code-review workflow.
It spins up several containers:
- Gitea – self-hosted Git service.
- Gitea MCP server – provides the Model Context Protocol bridge.
- Ubuntu Runner – runs Gitea Actions.
- Claude Code CLI server – listens for HTTP requests and performs automated code reviews on Pull Requests.

A dedicated server for the Claude Code CLI is used because the runner had connectivity issues accessing either the CLI or the Gitea server.
Instead, the runner simply sends an HTTP request to this separate service.

The entire project was created with Claude Code and is intended for educational and exploratory purposes only.