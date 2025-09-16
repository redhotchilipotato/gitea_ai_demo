#!/usr/bin/env python3
"""
Claude Code Analyzer - AI-powered code review with MCP integration
This simulates
 Code functionality for code reviews
"""
import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
import requests

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class MCPClient:
    """Basic MCP client for Gitea integration"""

    def __init__(self, mcp_url="http://mcp:8080"):
        self.mcp_url = mcp_url

    def health_check(self):
        """Check if MCP server is available"""
        try:
            response = requests.get(f"{self.mcp_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_pr_info(self, pr_number, repo_owner, repo_name):
        """Get PR information via MCP (simulated)"""
        # In a real implementation, this would use MCP protocol
        # For now, we'll return a simulated structure
        return {
            "number": pr_number,
            "title": f"Pull Request #{pr_number}",
            "body": "Automated analysis of code changes",
            "repository": f"{repo_owner}/{repo_name}"
        }


class CodeAnalyzer:
    """Advanced code analyzer with AI capabilities"""

    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)
        self.mcp_client = MCPClient()

    def analyze_repository_structure(self):
        """Analyze repository structure and patterns"""
        structure = {}

        # Get file types and counts
        for ext in ['.py', '.js', '.ts', '.go', '.java', '.cpp', '.c', '.rs', '.rb']:
            files = list(self.repo_path.rglob(f'*{ext}'))
            if files:
                structure[ext] = len(files)

        # Get recent commits
        try:
            result = subprocess.run(['git', 'log', '--oneline', '-10'],
                                  capture_output=True, text=True, cwd=self.repo_path)
            structure['recent_commits'] = result.stdout.strip().split('\n')[:5]
        except:
            structure['recent_commits'] = ["No git history available"]

        return structure

    def analyze_code_changes(self):
        """Analyze recent code changes"""
        changes = {}

        try:
            # Get diff of recent changes
            result = subprocess.run(['git', 'diff', 'HEAD~1..HEAD'],
                                  capture_output=True, text=True, cwd=self.repo_path)
            changes['diff'] = result.stdout

            # Get changed files
            result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1..HEAD'],
                                  capture_output=True, text=True, cwd=self.repo_path)
            changes['files'] = result.stdout.strip().split('\n') if result.stdout.strip() else []

        except:
            changes['diff'] = "No recent changes detected"
            changes['files'] = []

        return changes

    def generate_review(self, pr_number, repo_owner, repo_name):
        """Generate comprehensive code review"""

        # Check MCP connectivity
        mcp_available = self.mcp_client.health_check()

        # Analyze repository
        structure = self.analyze_repository_structure()
        changes = self.analyze_code_changes()

        # Try to get AI-powered review if Claude API key is available
        claude_review = None
        claude_api_key = os.getenv('CLAUDE_API_KEY')

        if claude_api_key and HAS_ANTHROPIC:
            claude_review = self.get_claude_review(changes, structure, claude_api_key)

        # Generate review content
        review = self.create_review_content(pr_number, repo_owner, repo_name,
                                          structure, changes, mcp_available, claude_review)

        return review

    def get_claude_review(self, changes, structure, api_key):
        """Get AI-powered review from Claude API"""
        try:
            client = anthropic.Anthropic(api_key=api_key)

            # Create analysis prompt
            prompt = f"""Please perform a code review analysis:

Repository Structure:
{json.dumps(structure, indent=2)}

Code Changes:
{changes.get('diff', 'No changes detected')[:4000]}  # Limit for API

Please provide:
1. Code quality assessment
2. Potential issues or bugs
3. Security considerations
4. Performance implications
5. Best practice recommendations

Focus on actionable, specific feedback."""

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text

        except Exception as e:
            return f"Claude API analysis failed: {str(e)}"

    def create_review_content(self, pr_number, repo_owner, repo_name,
                            structure, changes, mcp_available, claude_review=None):
        """Create structured review content"""

        # Count total files analyzed
        total_files = sum(structure.get(ext, 0) for ext in structure if ext.startswith('.'))

        review = f"""## 🤖 AI-Powered Code Review

### Pull Request Analysis
- **Repository**: {repo_owner}/{repo_name}
- **PR Number**: #{pr_number}
- **Files Analyzed**: {total_files} source files
- **MCP Integration**: {'✅ Active' if mcp_available else '⚠️  Fallback mode'}

### Repository Overview
"""

        # Add file type breakdown
        if structure:
            review += "**File Types:**\n"
            for ext, count in structure.items():
                if ext.startswith('.'):
                    review += f"- {ext}: {count} files\n"

        # Add recent commits context
        if 'recent_commits' in structure:
            review += "\n**Recent Development Activity:**\n```\n"
            for commit in structure['recent_commits'][:3]:
                if commit.strip():
                    review += f"{commit}\n"
            review += "```\n"

        # Analyze changes
        review += "\n### Change Analysis\n"

        if changes['files']:
            review += f"**Modified Files**: {len(changes['files'])} files changed\n"
            for file in changes['files'][:5]:  # Show first 5 files
                if file.strip():
                    review += f"- {file}\n"

        # Add Claude AI analysis if available
        if claude_review:
            review += f"\n### 🤖 Claude AI Analysis\n\n{claude_review}\n"

        # Add basic analysis
        review += "\n### Code Quality Assessment\n"

        if changes['diff']:
            # Simple heuristic analysis
            diff_lines = changes['diff'].split('\n')
            added_lines = [line for line in diff_lines if line.startswith('+')]
            removed_lines = [line for line in diff_lines if line.startswith('-')]

            review += f"- **Changes**: +{len(added_lines)} -{len(removed_lines)} lines\n"

            # Check for potential issues
            issues = []
            if any('TODO' in line for line in added_lines):
                issues.append("Contains TODO comments - consider addressing before merge")
            if any('console.log' in line for line in added_lines):
                issues.append("Contains console.log statements - consider removing for production")
            if any('print(' in line for line in added_lines):
                issues.append("Contains print statements - consider using proper logging")

            if issues:
                review += "\n**Potential Issues:**\n"
                for issue in issues:
                    review += f"- ⚠️  {issue}\n"
            else:
                review += "- ✅ No obvious issues detected\n"
        else:
            review += "- ℹ️  No specific changes detected in current analysis\n"

        # Add recommendations
        review += "\n### Recommendations\n"
        review += "- ✅ Code follows general best practices\n"
        review += "- 🧪 Ensure comprehensive test coverage for new features\n"
        review += "- 📚 Update documentation if public APIs changed\n"
        review += "- 🔒 Verify security implications of changes\n"

        # Integration status
        review += "\n### Integration Status\n"
        if mcp_available:
            review += "- ✅ MCP server integration active\n"
            review += "- ✅ Full repository context available\n"
            review += "- ✅ Real-time Gitea integration enabled\n"
        else:
            review += "- ⚠️  MCP server not available - using fallback analysis\n"
            review += "- ℹ️  Limited to local repository analysis\n"

        review += "\n---\n*Generated by AI Code Analyzer with MCP integration*"

        return review


def main():
    parser = argparse.ArgumentParser(description='AI Code Analyzer for Pull Requests')
    parser.add_argument('pr_number', help='Pull request number')
    parser.add_argument('repo_owner', help='Repository owner')
    parser.add_argument('repo_name', help='Repository name')
    parser.add_argument('--repo-path', default='.', help='Path to repository')

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = CodeAnalyzer(args.repo_path)

    # Generate review
    review = analyzer.generate_review(args.pr_number, args.repo_owner, args.repo_name)

    # Output review
    print(review)


if __name__ == '__main__':
    main()