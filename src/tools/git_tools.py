"""Git repository analysis tools for MCP server."""
import json
import subprocess
import re
from collections import Counter


def git_repo_stats(repo_path: str = ".") -> dict:
    """Get statistics for a git repository."""
    def git(*args):
        r = subprocess.run(["git"] + list(args), capture_output=True, text=True, cwd=repo_path)
        return r.stdout.strip()

    # Commit count
    total_commits = int(git("rev-list", "--count", "HEAD") or 0)

    # Contributors
    authors = git("log", "--format=%an", "--no-merges")
    author_counts = Counter(authors.split("\n")) if authors else Counter()

    # File stats
    files = git("ls-files")
    file_list = files.split("\n") if files else []
    extensions = Counter(f.rsplit(".", 1)[-1] for f in file_list if "." in f)

    # Recent activity
    recent = git("log", "--oneline", "-10", "--no-merges")

    # Branch count
    branches = git("branch", "-a")
    branch_count = len([b for b in branches.split("\n") if b.strip()])

    return {
        "total_commits": total_commits,
        "total_files": len(file_list),
        "contributors": dict(author_counts.most_common(10)),
        "file_types": dict(extensions.most_common(15)),
        "branch_count": branch_count,
        "recent_commits": recent.split("\n") if recent else []
    }


def git_changed_files(repo_path: str = ".", since: str = "7 days ago") -> dict:
    """Get files changed in recent period."""
    cmd = ["git", "log", f"--since={since}", "--name-only", "--pretty=format:", "--no-merges"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_path)
    files = [f for f in result.stdout.strip().split("\n") if f.strip()]
    file_counts = Counter(files)

    return {
        "since": since,
        "unique_files_changed": len(file_counts),
        "most_changed": dict(file_counts.most_common(20))
    }


def git_search_commits(repo_path: str = ".", query: str = "", author: str = "") -> dict:
    """Search git commits by message or author."""
    cmd = ["git", "log", "--oneline", "-50"]
    if query:
        cmd.extend(["--grep", query, "-i"])
    if author:
        cmd.extend(["--author", author])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_path)
    commits = [c for c in result.stdout.strip().split("\n") if c.strip()]

    return {"query": query or author, "count": len(commits), "commits": commits}
