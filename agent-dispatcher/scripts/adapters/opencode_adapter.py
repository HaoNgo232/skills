import json
from typing import Dict, Any, List
from .base import BaseAgentAdapter, DispatchOptions

class OpenCodeAdapter(BaseAgentAdapter):
    name = "opencode"
    binary_names = ["opencode"]
    version_flag = "--version"

    def build_command(self, prompt: str, opts: DispatchOptions) -> List[str]:
        if not self.binary_path:
            raise RuntimeError("OpenCode CLI binary not found on PATH.")

        # Always include --auto to prevent non-interactive permission stalls
        # and --format json for structured stream output
        cmd = [self.binary_path, "run", "--auto", "--format", "json"]

        if opts.model:
            cmd.extend(["-m", opts.model])

        cmd.append(prompt)
        return cmd

    def parse_summary_and_error(self, exit_code: int, log_content: str) -> Dict[str, Any]:
        summary_texts = []
        tokens_info = None
        session_id = None

        for line in log_content.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if not session_id and "sessionID" in event:
                    session_id = event["sessionID"]

                part = event.get("part", {})
                if part.get("type") == "text" and "text" in part:
                    summary_texts.append(part["text"])
                elif part.get("type") == "step-finish" and "tokens" in part:
                    tokens_info = part["tokens"]
            except Exception:
                continue

        summary = "\n".join(summary_texts).strip() if summary_texts else None
        if not summary:
            return super().parse_summary_and_error(exit_code, log_content)

        return {
            "summary": summary,
            "tokens": tokens_info,
            "session_id": session_id,
            "error_hint": None if exit_code == 0 else "Execution did not finish cleanly."
        }
