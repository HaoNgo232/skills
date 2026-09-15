import subprocess
from typing import Dict, Any, Set, List

def get_git_status_files(cwd: str) -> Set[str]:
    """Returns set of relative filepaths currently modified or untracked in git repo."""
    try:
        res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd, capture_output=True, text=True, timeout=5
        )
        files = set()
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                line = line.strip()
                if line:
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        files.add(parts[1].strip())
        return files
    except Exception:
        return set()

def get_git_diff_stat(cwd: str) -> str:
    """Returns git diff --stat summary."""
    try:
        res = subprocess.run(
            ["git", "diff", "--stat"],
            cwd=cwd, capture_output=True, text=True, timeout=5
        )
        return res.stdout.strip() if res.returncode == 0 else ""
    except Exception:
        return ""

def calculate_git_delta(before_files: Set[str], after_files: Set[str], cwd: str) -> Dict[str, Any]:
    """
    Computes files genuinely created or touched by the task run by subtracting before_files.
    """
    newly_modified = sorted(list(after_files - before_files))
    # If the set difference is empty (e.g. modifying an already dirty file), list after_files that exist
    return {
        "newly_modified_files": newly_modified,
        "diff_stat": get_git_diff_stat(cwd)
    }
