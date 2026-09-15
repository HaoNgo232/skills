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

    def parse_activity(self, log_content: str) -> str:
        """Parse clean activity from Cline's output by removing ANSI escapes."""
        import re
        ansi_regex = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_text = ansi_regex.sub('', log_content)
        lines = [line.strip() for line in clean_text.splitlines() if line.strip()]

        for line in reversed(lines):
            # Look for common Cline indicators: [run_commands], [read_files], [thinking], etc.
            if any(tag in line for tag in ["[run_commands]", "[read_files]", "[write_to_file]", "[search_files]", "[thinking]"]):
                return line[:120]

        return super().parse_activity(clean_text)

