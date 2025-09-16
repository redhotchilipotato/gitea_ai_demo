# Gitea + AI (Claude Code) Demo
## Overview: 
Repository contains a Docker-based demo setup showcasing an experimental code-review workflow.
It spins up several containers:
- Gitea – self-hosted Git service.
- Gitea MCP server – provides the Model Context Protocol bridge.
- Ubuntu Runner – runs Gitea Actions.
- Claude Code CLI server – listens for HTTP requests and performs automated code reviews on Pull Requests.

A dedicated server for the Claude Code CLI is used because the runner had connectivity issues accessing either the CLI or the Gitea server.
Instead, the runner simply sends an HTTP request to this separate service.

The entire project was created with Claude Code and is intended for educational and exploratory purposes only.

## Note:
This demo was generated with Claude Code. During development, several approaches for automating code review were tested, so some unused scripts remain in the project (e.g., claude-code-review.sh, code-review.sh). These represent earlier attempts to run the Claude Code CLI directly on the Ubuntu runner or to use the API instead of the CLI.

The current solution still requires manual setup on the Claude Code CLI server:
- You must log in to the CLI with your own account.
- The MCP server needs to be configured manually.

Additionally, the review prompt is generic and not optimized for any specific project.

## Potential Improvements:
- Leverage the MCP server more effectively in the review prompt and request reviews for the entire Pull Request rather than just the diff.
- Improve file handling by storing the checked-out branch in a temporary directory and keeping it until the Pull Request is closed and merged.
- Enhance the security of the deployed services and Docker containers.