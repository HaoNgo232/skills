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

        # In non-interactive mode, include --auto and --format json for automated JSON event streaming
        # In interactive mode (inside tmux), omit --format json and --auto so the full visual TUI is active
        cmd = [self.binary_path, "run"]
        if not opts.interactive:
            cmd.append("--auto")
            cmd.extend(["--format", "json"])

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

    def parse_activity(self, log_content: str) -> str:
        """Parse structured events from OpenCode's json stream to report current activity."""
        lines = [line.strip() for line in log_content.splitlines() if line.strip()]
        for line in reversed(lines):
            try:
                event = json.loads(line)
                part = event.get("part", {})
                event_type = event.get("type")
                part_type = part.get("type")

                if event_type == "tool_call" or "tool" in part:
                    tool_name = part.get("tool") or event.get("tool")
                    tool_args = part.get("args") or event.get("args", {})
                    arg_summary = ""
                    if isinstance(tool_args, dict):
                        # Pick common file or command arguments
                        for k in ["path", "file", "command", "pattern", "query"]:
                            if k in tool_args:
                                arg_summary = f": {tool_args[k]}"
                                break
                    return f"Executing tool {tool_name}{arg_summary}"

                if part_type == "tool-call":
                    tool_name = part.get("name") or "tool"
                    tool_input = part.get("input", {})
                    arg_summary = ""
                    if isinstance(tool_input, dict):
                        for k in ["path", "file", "command", "pattern", "query"]:
                            if k in tool_input:
                                arg_summary = f": {tool_input[k]}"
                                break
                    return f"Executing tool {tool_name}{arg_summary}"

                if part_type == "text" and "text" in part:
                    txt = part["text"].strip().replace("\n", " ")
                    if txt:
                        return f"Thinking/Responding: {txt[:100]}"

                if event_type == "step_start" or part_type == "step-start":
                    return "Starting reasoning step..."
            except Exception:
                continue

        return super().parse_activity(log_content)

    def list_models(self) -> List[str]:
        """Fetch available models via opencode models command."""
        if not self.binary_path:
            return []
        try:
            import subprocess
            res = subprocess.run(
                [self.binary_path, "models"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if res.returncode == 0:
                return [line.strip() for line in res.stdout.splitlines() if line.strip()]
        except Exception:
            pass
        return []


