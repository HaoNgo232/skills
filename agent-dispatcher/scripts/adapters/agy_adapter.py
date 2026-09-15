from typing import List
from .base import BaseAgentAdapter, DispatchOptions

class AgyAdapter(BaseAgentAdapter):
    name = "agy"
    binary_names = ["agy"]
    version_flag = "--version"

    def build_command(self, prompt: str, opts: DispatchOptions) -> List[str]:
        if not self.binary_path:
            raise RuntimeError("Agy CLI binary not found on PATH.")

        # Match plan spec: --print, --dangerously-skip-permissions, and --output-format json
        cmd = [
            self.binary_path,
            "--print",
            prompt,
            "--dangerously-skip-permissions",
            "--output-format",
            "json"
        ]

        if opts.model:
            cmd.extend(["--model", opts.model])

        return cmd
