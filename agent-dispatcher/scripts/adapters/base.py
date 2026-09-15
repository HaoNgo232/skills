import abc
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set

@dataclass
class DispatchOptions:
    timeout: int = 120
    model: Optional[str] = None
    cwd: Optional[str] = None
    worktree: bool = False
    dry_run: bool = False
    async_mode: bool = False


@dataclass
class AgentIdentity:
    engine: str
    binary_path: Optional[str]
    is_available: bool
    version: Optional[str] = None
    active_model: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine": self.engine,
            "binary_path": self.binary_path,
            "is_available": self.is_available,
            "version": self.version,
            "active_model": self.active_model,
            "extra": self.extra
        }

class BaseAgentAdapter(abc.ABC):
    """Base interface for AI Coding Agent Adapters."""
    
    name: str = "base"
    binary_names: List[str] = []
    version_flag: str = "--version"

    def __init__(self):
        self.binary_path = self.locate_binary()

    def locate_binary(self) -> Optional[str]:
        for b in self.binary_names:
            p = shutil.which(b)
            if p:
                return p
        return None

    def is_available(self) -> bool:
        return self.binary_path is not None

    def verify_identity(self) -> AgentIdentity:
        """
        Default pre-flight identity check: locates binary and executes version command.
        """
        if not self.is_available():
            return AgentIdentity(
                engine=self.name,
                binary_path=None,
                is_available=False
            )

        version = None
        extra = {}
        try:
            res = subprocess.run(
                [self.binary_path, self.version_flag],
                capture_output=True, text=True, timeout=5
            )
            if res.returncode == 0:
                version = res.stdout.strip()
            else:
                extra["version_stderr"] = res.stderr.strip()
        except Exception as e:
            extra["version_error"] = str(e)

        return AgentIdentity(
            engine=self.name,
            binary_path=self.binary_path,
            is_available=True,
            version=version,
            extra=extra
        )

    @abc.abstractmethod
    def build_command(self, prompt: str, opts: DispatchOptions) -> List[str]:
        """Builds CLI execution command list."""
        pass

    def parse_activity(self, log_content: str) -> str:
        """Extract a short human-readable description of current activity from recent log lines."""
        lines = [line.strip() for line in log_content.splitlines() if line.strip()]
        if not lines:
            return "Idle / Waiting for output"
        return lines[-1][:120]

    def parse_summary_and_error(self, exit_code: int, log_content: str) -> Dict[str, Any]:
        """Default log parser: extracts the last relevant lines or error indicators."""
        lines = [line.strip() for line in log_content.splitlines() if line.strip()]
        last_lines = lines[-10:] if len(lines) >= 10 else lines
        
        error_lines = []
        for line in lines:
            if any(kw in line.lower() for kw in ["error:", "failed:", "exception:", "fatal:"]):
                error_lines.append(line)
        
        return {
            "summary": "\n".join(last_lines[-3:]) if last_lines else "No output captured.",
            "error_hint": "\n".join(error_lines[-5:]) if error_lines else None
        }


