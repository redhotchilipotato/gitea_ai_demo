#!/usr/bin/env python3

import os
import subprocess
import tempfile
import shutil
from flask import Flask, request, jsonify
import git
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "code-review"})

@app.route('/review', methods=['POST'])
def code_review():
    """
    Code review endpoint
    Expected JSON payload:
    {
        "repo_url": "http://gitea:3000/admin/repo.git",
        "branch": "feature-branch",
        "base_branch": "main"
    }
    """
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        branch = data.get('branch', 'main')
        base_branch = data.get('base_branch', 'main')

        if not repo_url:
            return jsonify({"error": "repo_url is required"}), 400

        logging.info(f"Starting code review for {repo_url}, branch: {branch}")

        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Clone repository
                logging.info(f"Cloning repository to {temp_dir}")
                repo = git.Repo.clone_from(repo_url, temp_dir)

                # Checkout the branch to review
                if branch != 'main':
                    try:
                        repo.git.checkout(branch)
                        logging.info(f"Checked out branch: {branch}")
                    except git.exc.GitCommandError as e:
                        logging.warning(f"Could not checkout branch {branch}: {e}")

                # Get diff between base and current branch
                try:
                    if branch != base_branch:
                        diff = repo.git.diff(f"{base_branch}...{branch}")
                    else:
                        # If same branch, get recent changes
                        diff = repo.git.diff("HEAD~1")

                    if not diff.strip():
                        return jsonify({
                            "status": "success",
                            "review": "No changes found to review.",
                            "branch": branch
                        })

                    logging.info(f"Generated diff ({len(diff)} characters)")
                except git.exc.GitCommandError as e:
                    logging.warning(f"Could not generate diff: {e}")
                    diff = "Unable to generate diff"

                # Run Claude Code CLI for code review
                claude_result = run_claude_code_review(temp_dir, diff, branch)

                return jsonify({
                    "status": "success",
                    "review": claude_result,
                    "branch": branch,
                    "repo_url": repo_url
                })

            except git.exc.GitCommandError as e:
                logging.error(f"Git error: {e}")
                return jsonify({"error": f"Git operation failed: {str(e)}"}), 500

    except Exception as e:
        logging.error(f"Code review failed: {e}")
        return jsonify({"error": f"Code review failed: {str(e)}"}), 500

def run_claude_code_review(repo_path, diff, branch):
    """Run Claude Code CLI to perform code review"""
    try:
        # Change to repo directory
        original_cwd = os.getcwd()
        os.chdir(repo_path)

        # Create a prompt for code review
        prompt = f"""Please perform a code review for the following changes on branch '{branch}':

CHANGES:
{diff}

Please provide:
1. Overall assessment of the changes
2. Potential issues or bugs
3. Code quality suggestions
4. Security considerations (if any)
5. Performance implications (if any)

Keep the review concise but comprehensive."""

        # Run Claude Code CLI with correct syntax
        result = subprocess.run([
            'claude', '--print', prompt
        ],
        capture_output=True,
        text=True,
        timeout=300  # 5 minute timeout
        )

        os.chdir(original_cwd)

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            logging.error(f"Claude CLI error: {result.stderr}")
            return f"Claude CLI error: {result.stderr}"

    except subprocess.TimeoutExpired:
        return "Code review timed out after 5 minutes"
    except Exception as e:
        return f"Error running Claude Code: {str(e)}"
    finally:
        # Ensure we return to original directory
        try:
            os.chdir(original_cwd)
        except:
            pass

if __name__ == '__main__':
    logging.info("Starting Code Review Service...")
    app.run(host='0.0.0.0', port=5000, debug=False)