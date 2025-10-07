"""
AURA Autonomous Controller
Full project control via Telegram - code changes, deployments, analysis
"""
import os
import logging
import subprocess
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class AutonomousController:
    """
    Provides full autonomous control of the AURA system via Telegram.

    Capabilities:
    - Git operations (status, log, diff, commit, push)
    - Code analysis (what's changed, file structure, dependencies)
    - Railway deployments
    - File editing and creation
    - Project intelligence queries
    """

    def __init__(self, project_root: str = "/Users/johncox/Projects/helix/helix_production"):
        self.project_root = project_root

    async def get_project_summary(self) -> Dict:
        """Get comprehensive project overview"""
        try:
            # Git status
            git_status = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            ).stdout

            # Recent commits
            git_log = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            ).stdout

            # File count
            file_count = subprocess.run(
                ["find", ".", "-type", "f", "-name", "*.py", "|", "wc", "-l"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                shell=True
            ).stdout.strip()

            return {
                "git_status": git_status,
                "recent_commits": git_log,
                "python_files": file_count,
                "project_root": self.project_root
            }
        except Exception as e:
            logger.error(f"Project summary error: {e}")
            return {"error": str(e)}

    async def get_recent_changes(self, days: int = 7) -> str:
        """Analyze what's been added/removed recently"""
        try:
            # Get git log with stats
            result = subprocess.run(
                ["git", "log", f"--since={days} days ago", "--stat", "--pretty=format:%h %s"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.stdout
        except Exception as e:
            logger.error(f"Recent changes error: {e}")
            return f"Error: {e}"

    async def deploy_to_railway(self) -> Dict:
        """Trigger Railway deployment"""
        try:
            # Push to GitHub (Railway auto-deploys)
            push_result = subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if push_result.returncode == 0:
                # Trigger Railway CLI deployment
                railway_result = subprocess.run(
                    ["railway", "up"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                return {
                    "success": railway_result.returncode == 0,
                    "output": railway_result.stdout,
                    "error": railway_result.stderr
                }
            else:
                return {
                    "success": False,
                    "error": f"Git push failed: {push_result.stderr}"
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Railway deployment timed out (>5 min)"}
        except Exception as e:
            logger.error(f"Deploy error: {e}")
            return {"success": False, "error": str(e)}

    async def read_file(self, filepath: str) -> str:
        """Read file contents"""
        try:
            full_path = os.path.join(self.project_root, filepath)
            with open(full_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    async def edit_file(self, filepath: str, old_content: str, new_content: str) -> Dict:
        """Edit file by replacing content"""
        try:
            full_path = os.path.join(self.project_root, filepath)

            # Read current content
            with open(full_path, 'r') as f:
                current = f.read()

            # Check if old_content exists
            if old_content not in current:
                return {"success": False, "error": "Old content not found in file"}

            # Replace
            updated = current.replace(old_content, new_content)

            # Write back
            with open(full_path, 'w') as f:
                f.write(updated)

            return {"success": True, "message": f"Updated {filepath}"}

        except Exception as e:
            logger.error(f"File edit error: {e}")
            return {"success": False, "error": str(e)}

    async def create_file(self, filepath: str, content: str) -> Dict:
        """Create new file"""
        try:
            full_path = os.path.join(self.project_root, filepath)

            # Create directories if needed
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # Write file
            with open(full_path, 'w') as f:
                f.write(content)

            return {"success": True, "message": f"Created {filepath}"}

        except Exception as e:
            logger.error(f"File creation error: {e}")
            return {"success": False, "error": str(e)}

    async def git_commit(self, message: str, files: List[str] = None) -> Dict:
        """Commit changes"""
        try:
            # Add files
            if files:
                for file in files:
                    subprocess.run(["git", "add", file], cwd=self.project_root, check=True)
            else:
                subprocess.run(["git", "add", "-A"], cwd=self.project_root, check=True)

            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }

        except Exception as e:
            logger.error(f"Git commit error: {e}")
            return {"success": False, "error": str(e)}

    async def analyze_codebase(self, query: str) -> str:
        """Analyze codebase to answer questions"""
        query_lower = query.lower()

        try:
            # Different analysis based on query
            if "what files" in query_lower or "file structure" in query_lower:
                result = subprocess.run(
                    ["find", ".", "-type", "f", "-name", "*.py", "-o", "-name", "*.html", "-o", "-name", "*.js"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                return f"Project Files:\n{result.stdout[:2000]}"

            elif "dependencies" in query_lower or "requirements" in query_lower:
                try:
                    with open(os.path.join(self.project_root, "requirements.txt"), 'r') as f:
                        return f"Requirements:\n{f.read()}"
                except:
                    return "No requirements.txt found"

            elif "database" in query_lower or "schema" in query_lower:
                # Find database schema files
                result = subprocess.run(
                    ["grep", "-r", "CREATE TABLE", ".", "--include=*.py"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                return f"Database Tables:\n{result.stdout[:2000]}"

            elif "api" in query_lower or "endpoints" in query_lower:
                # Find FastAPI routes
                result = subprocess.run(
                    ["grep", "-r", "@app\\|@router", ".", "--include=*.py"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                return f"API Endpoints:\n{result.stdout[:2000]}"

            else:
                return "Try asking: 'what files', 'show dependencies', 'list database tables', 'show api endpoints'"

        except Exception as e:
            logger.error(f"Codebase analysis error: {e}")
            return f"Error analyzing codebase: {e}"

    async def get_deployment_status(self) -> Dict:
        """Check Railway deployment status"""
        try:
            result = subprocess.run(
                ["railway", "status"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            return {
                "status": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }

        except Exception as e:
            logger.error(f"Deployment status error: {e}")
            return {"error": str(e)}


# Singleton
autonomous_controller = AutonomousController()
