from typing import List
from .base import BaseAgentAdapter, DispatchOptions

class ClineAdapter(BaseAgentAdapter):
    name = "cline"
    binary_names = ["cline"]
    version_flag = "--version"

    def build_command(self, prompt: str, opts: DispatchOptions) -> List[str]:
        if not self.binary_path:
            raise RuntimeError("Cline CLI binary not found on PATH.")

        cmd = [self.binary_path]
        if not opts.interactive:
            cmd.extend(["--auto-approve", "true"])
        
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

    def list_models(self) -> List[str]:
        """Fetch recommended free models from public API and configured provider models for Cline."""
        import json
        import urllib.request
        from pathlib import Path

        models = []

        # 1. Official Public API from Cline: https://api.cline.bot/api/v1/ai/cline/recommended-models
        try:
            req = urllib.request.Request(
                "https://api.cline.bot/api/v1/ai/cline/recommended-models",
                headers={"User-Agent": "cline-dispatcher"}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for item in data.get("free", []):
                    models.append(f"{item.get('name')} [id: {item.get('id')}] (free)")
        except Exception:
            pass


        # 2. Fetch configured models from ~/.cline/data/settings/providers.json
        settings_path = Path.home() / ".cline" / "data" / "settings" / "providers.json"
        if settings_path.exists():
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                providers = data.get("providers", {})
                for prov_key, prov_data in providers.items():
                    st = prov_data.get("settings", {})
                    m = st.get("model")
                    if m:
                        formatted = f"{prov_key}:{m}"
                        if formatted not in [x.split(" ")[0] for x in models]:
                            models.append(formatted)
            except Exception:
                pass

        return models



