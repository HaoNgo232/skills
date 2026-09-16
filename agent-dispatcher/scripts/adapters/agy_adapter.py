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

    def list_models(self) -> List[str]:
        """Fetch available models via agy models command."""
        if not self.binary_path:
            return []
        try:
            import re
            import subprocess
            res = subprocess.run(
                [self.binary_path, "models"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if res.returncode == 0:
                ansi_regex = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                clean_text = ansi_regex.sub('', res.stdout)
                models = []
                for line in clean_text.splitlines():
                    line = line.strip()
                    if not line or "Fetching available" in line:
                        continue
                    # Each line is: <id>\t<DisplayName> or <id>  <DisplayName>
                    parts = re.split(r'\t+|\s{2,}', line)
                    if parts:
                        models.append(parts[0])
                return models
        except Exception:
            pass
        return []

