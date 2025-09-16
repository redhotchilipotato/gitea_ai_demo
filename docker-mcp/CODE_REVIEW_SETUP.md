# Claude Code CLI Integration Setup

This guide explains how to set up automated code reviews using the **actual Claude Code CLI tool** directly integrated with your Gitea repository for every Pull Request.

## 🚀 **Claude Code CLI Approach**

This system uses the **real Claude Code CLI** installed in the Actions runner:

- ✅ **Native Claude Code** - Uses the actual CLI tool from Anthropic
- ✅ **Full codebase understanding** - Claude Code has complete repository context  
- ✅ **Advanced AI analysis** - Powered by Claude's latest models
- ✅ **Direct tool integration** - No API wrapper needed
- ✅ **Comprehensive reviews** - Deep code understanding with natural language interface

## Prerequisites

1. **Running Gitea with Actions** - Use `make up` to start the stack
2. **Standard runner** - Uses regular Gitea Actions runner
3. **Claude Code authentication** - Requires Claude account setup
4. **Repository with Actions enabled**

## Setup Instructions

### 1. Claude Code Authentication

The workflow automatically installs Claude Code CLI during execution. You'll need:

- **Claude account** with Pro/Max plan OR
- **Anthropic Console access** with active billing OR  
- **Enterprise setup** (Bedrock/Vertex AI)

### 2. Add Repository Secrets

In your Gitea repository, go to:
**Settings → Secrets and Variables → Actions**

Add this secret:
- `GITEA_TOKEN` - Your Gitea access token (found in `.env` after running `make up`)

**Note:** Claude Code CLI handles its own authentication - no API key needed in secrets!

### 3. Enable Actions in Repository

1. Go to your repository **Settings → Actions**
2. Enable **Actions** for the repository
3. Ensure the runner is active (check with `make runner-status`)

### 4. Test the Setup

1. Create a test branch and make some changes
2. Open a Pull Request
3. The workflow will automatically trigger
4. Check the **Actions** tab to see the workflow progress
5. Claude's review will appear as a comment on the PR

## Workflow Details

### Trigger Events
- Pull request opened
- Pull request updated (new commits)
- Pull request reopened

### Review Process
1. **Fetches PR diff** and metadata from Gitea API
2. **Sends to Claude** for comprehensive analysis
3. **Posts review** as a comment with:
   - Overall assessment
   - Code quality feedback
   - Potential issues and bugs
   - Specific suggestions
   - Approval recommendation

### Customization

Edit `.gitea/workflows/code-review.yml` to:
- Change trigger events
- Modify the review prompt
- Add additional checks or tools
- Customize the output format

Edit `scripts/code-review.sh` to:
- Change Claude model or parameters
- Modify the review format
- Add custom analysis logic

## Troubleshooting

### Workflow Not Triggering
- Check if Actions are enabled in repository settings
- Verify runner is active: `make runner-status`
- Ensure workflow file is in `.gitea/workflows/`

### API Errors
- Verify Claude API key is valid and has credits
- Check Gitea token has proper permissions
- Review workflow logs in Actions tab

### Permission Issues
- Ensure Gitea token has repository read/write access
- Check if the runner can access internal Gitea API

## Security Notes

- Store API keys as repository secrets, never in code
- Claude API usage will incur costs based on token usage
- Review Claude's suggestions before implementing changes
- The automation posts public comments on PRs

## Monitoring

- Check `make runner-logs` for runner activity
- Monitor Claude API usage in Anthropic Console
- Review workflow execution in repository Actions tab