---
name: agent-dispatcher
description: >-
  Dispatch coding tasks EXCLUSIVELY to external AI coding agent CLIs (Cline CLI, OpenCode)
  to offload quota and preserve the main agent's context window. Strictly forbids invoking
  internal subagents or self-CLI for offloaded tasks. Use whenever the user wants to delegate
  coding work to Cline, OpenCode, or other external CLI agents.
---

# Agent Dispatcher Skill

This skill delegates coding tasks (features, bug fixes, refactoring, tests) to **EXTERNAL** coding agent CLIs installed on the machine (`cline`, `opencode`) to consume their independent quota and keep the main agent's context window clean.

---

## 🛡️ CRITICAL GUARDS (STRICT RULES)

When this skill is invoked:

### 1. NO Internal Subagent Dispatch
- **DO NOT** use your own internal/native subagent tools for tasks meant for this skill.
- *Reason*: Internal subagents consume the main agent's own API quota. This skill's explicit mission is to **offload quota to EXTERNAL agents**.

### 2. NO Inferior / Self-CLI Dispatch
- **DO NOT** call the main agent's own CLI (e.g. Antigravity calling `agy`).
- *Reason*: If you want the main agent's own intelligence, native tools are already superior. Calling your own CLI is redundant, slower, and consumes your own quota.

### 3. EXCLUSIVELY Dispatch to External Agents
- Always offload to external agents that possess independent quota/subscriptions:
  - If Main Agent is `agy` → Dispatch to `cline` or `opencode`.
  - If Main Agent is `cline` → Dispatch to `opencode` or `agy`.
  - If Main Agent is `opencode` → Dispatch to `cline` or `agy`.

---

## Quick Command Execution

The calling agent runs `dispatch.py` using its own skill directory path:
```bash
python3 <skill_dir>/scripts/dispatch.py run <external_agent> "<prompt>" --caller <your_identity> [options]
```
*(Or simply `agent-dispatcher run ...` if `agent-dispatcher` is already in PATH)*

> **Interactive by Default**: All tasks automatically run in a detached `tmux` session (`disp-<timestamp>-<hash>`) if `tmux` is available on the system. You can attach with `tmux attach -t <id>` at any time!

### Examples:
- **Offload to Cline**:
  ```bash
  python3 <skill_dir>/scripts/dispatch.py run cline "Viết unit test cho auth module" --caller agy --timeout 120
  ```
- **Offload to OpenCode**:
  ```bash
  python3 <skill_dir>/scripts/dispatch.py run opencode "Tạo helper format tiền tệ" --caller agy --timeout 60
  ```
- **Offload Asynchronously (Background Job)**:
  ```bash
  python3 <skill_dir>/scripts/dispatch.py run opencode "Review codebase" --caller agy --timeout 600 --async
  ```
- **Turn off Interactive Tmux Session**:
  ```bash
  python3 <skill_dir>/scripts/dispatch.py run opencode "Tạo hàm test" --caller agy --no-interactive
  ```
- **Check Status / Activity / Prompt of Dispatched Agent**:
  ```bash
  python3 <skill_dir>/scripts/dispatch.py status [execution_id]
  ```
  *(Tip: Omit `[execution_id]` to automatically check the latest session)*
- **Send Reply / Answer to Agent Prompt (2-Way)**:
  ```bash
  python3 <skill_dir>/scripts/dispatch.py reply "y" [--id <execution_id>]
  ```
- **Watch Live Progress (Terminal Stream)**:
  ```bash
  python3 <skill_dir>/scripts/dispatch.py watch [execution_id]
  ```
  *(Tip: Omit `[execution_id]` to automatically stream the latest session)*
- **Open Live Interactive TUI (Full Visual Monitor & Intervention)**:
  ```bash
  tmux attach -t <execution_id>
  ```
  *(Always available by default! Tip: Press `Ctrl+b` then `d` to detach safely without stopping the agent)*
- **Cancel a Running Dispatched Agent**:
  ```bash
  python3 <skill_dir>/scripts/dispatch.py cancel [execution_id]
  ```
- **List Available Models for Agent**:
  ```bash
  python3 <skill_dir>/scripts/dispatch.py list-models <external_agent>
  ```


### Available Options:
- `--caller <name>`: *(Required)* Calling agent identity (`agy`, `cline`, `opencode`). Blocks self-dispatch.
- `--timeout <seconds>`: Max execution timeout in seconds (default: 120).
- `--async`: Launch external agent asynchronously in the background and return immediately.
- `--interactive`: Launch inside detached tmux session allowing 2-way input (`reply`) and user live attachment (`tmux attach`).
- `--idle-timeout <seconds>`: Max allowed seconds with zero log activity before stopping (default: 120). Prevents killing actively working agents.
- `--checkin <seconds>`: Periodic health check-in interval. Instead of killing on timer, outputs an activity check-in event so main agent can monitor progress.
- `--model <model_id>`: Target model override.
- `--worktree`: Run in isolated git worktree (Cline).
- `--dry-run`: Preview command without running.


---

## Output Contract (Context Shield)
All verbose terminal streams stay in `/tmp/agent_runs/`. The script prints only a clean JSON summary (~80 tokens):
```json
{
  "status": "success",
  "execution_id": "disp-...",
  "caller": "agy",
  "agent": {"name": "cline", "version": "3.0.62"},
  "duration_seconds": 15.2,
  "newly_modified_files": ["src/helpers/currency.ts"],
  "summary": "Helper created successfully.",
  "audit_manifest": "/tmp/agent_runs/.../audit_manifest.json"
}
```
