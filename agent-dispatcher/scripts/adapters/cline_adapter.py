from typing import List
from .base import BaseAgentAdapter, DispatchOptions

class ClineAdapter(BaseAgentAdapter):
    name = "cline"
    binary_names = ["cline"]
    version_flag = "--version"

    def build_command(self, prompt: str, opts: DispatchOptions) -> List[str]:
        if not self.binary_path:
            raise RuntimeError("Cline CLI binary not found on PATH.")

        cmd = [self.binary_path, "--auto-approve", "true"]
        
        if opts.timeout > 0:
            cmd.extend(["--timeout", str(opts.timeout)])

        if opts.model:
            cmd.extend(["-m", opts.model])

        if opts.worktree:
            cmd.append("--worktree")

        cmd.append(prompt)
        return cmd
