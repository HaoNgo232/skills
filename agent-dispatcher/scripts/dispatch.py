#!/usr/bin/env python3
import argparse
import datetime
import json
import os
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

# Add current directory to path so adapters package can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from adapters import REGISTRY, get_adapter, DispatchOptions
from adapters.git_utils import get_git_status_files, calculate_git_delta

RUN_LOG_DIR = Path("/tmp/agent_runs")

def is_pid_alive(pid: int) -> bool:
    """Check if process with given PID is still active."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False

def has_tmux() -> bool:
    """Check if tmux binary exists on system."""
    import shutil
    return shutil.which("tmux") is not None

def is_tmux_session_alive(session_name: str) -> bool:
    """Check if a tmux session is active."""
    if not has_tmux():
        return False
    try:
        res = subprocess.run(
            ["tmux", "has-session", "-t", session_name],
            capture_output=True,
            timeout=3
        )
        return res.returncode == 0
    except Exception:
        return False

def get_tmux_session_pid(session_name: str) -> Optional[int]:
    """Retrieve pane PID from tmux session."""
    if not has_tmux():
        return None
    try:
        res = subprocess.run(
            ["tmux", "list-panes", "-t", session_name, "-F", "#{pane_pid}"],
            capture_output=True,
            text=True,
            timeout=3
        )
        if res.returncode == 0 and res.stdout.strip():
            return int(res.stdout.strip().splitlines()[0])
    except Exception:
        pass
    return None

def send_tmux_keys(session_name: str, text: str, enter: bool = True) -> bool:
    """Send keystrokes to a running tmux session."""
    if not has_tmux() or not is_tmux_session_alive(session_name):
        return False
    try:
        cmd = ["tmux", "send-keys", "-t", session_name, text]
        if enter:
            cmd.append("C-m")
        res = subprocess.run(cmd, capture_output=True, timeout=5)
        return res.returncode == 0
    except Exception:
        return False

def kill_tmux_session(session_name: str) -> bool:
    """Kill a tmux session."""
    if not has_tmux():
        return False
    try:
        res = subprocess.run(
            ["tmux", "kill-session", "-t", session_name],
            capture_output=True,
            timeout=3
        )
        return res.returncode == 0
    except Exception:
        return False

def finalize_run(task_dir: Path, execution_id: str, caller: str, identity, prompt: str, opts: DispatchOptions,
                 exit_code: int, timed_out: bool, duration: float, command: list, git_before: set, cwd: str, adapter):
    raw_log_path = task_dir / "raw.log"
    manifest_path = task_dir / "audit_manifest.json"

    git_after = get_git_status_files(cwd)
    git_delta = calculate_git_delta(git_before, git_after, cwd)

    log_content = ""
    try:
        with open(raw_log_path, "r", encoding="utf-8", errors="replace") as f:
            log_content = f.read()
    except Exception:
        pass

    summary_info = adapter.parse_summary_and_error(exit_code, log_content)

    audit_manifest = {
        "execution_id": execution_id,
        "caller": caller or "unknown",
        "timestamp": datetime.datetime.now().isoformat(),
        "agent_identity": identity.to_dict(),
        "task_prompt": prompt,
        "options": vars(opts),
        "execution": {
            "exit_code": exit_code,
            "duration_seconds": duration,
            "timed_out": timed_out,
            "command": command
        },
        "git_delta": git_delta,
        "log_path": str(raw_log_path)
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(audit_manifest, f, indent=2, ensure_ascii=False)

    status = "success" if (exit_code == 0 and not timed_out) else "failed"

    clean_response = {
        "status": status,
        "execution_id": execution_id,
        "caller": caller or "unknown",
        "agent": {
            "name": identity.engine,
            "version": identity.version,
            "binary": identity.binary_path
        },
        "duration_seconds": duration,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "newly_modified_files": git_delta["newly_modified_files"],
        "summary": summary_info.get("summary"),
        "error_hint": summary_info.get("error_hint") if status != "success" else None,
        "audit_manifest": str(manifest_path),
        "raw_log": str(raw_log_path)
    }
    return clean_response

def cmd_list(args):
    results = {}
    for name, adapter in REGISTRY.items():
        results[name] = adapter.verify_identity().to_dict()
    print(json.dumps({"agents": results}, indent=2, ensure_ascii=False))

def cmd_verify(args):
    adapter = get_adapter(args.agent)
    identity = adapter.verify_identity()
    print(json.dumps({"verified_identity": identity.to_dict()}, indent=2, ensure_ascii=False))

def cmd_list_models(args):
    adapter = get_adapter(args.agent)
    models = adapter.list_models()
    print(json.dumps({"agent": args.agent, "models": models}, indent=2, ensure_ascii=False))


def get_cli_command(subcmd: str, *args: str) -> str:
    """Return friendly CLI invocation string, preferring 'agent-dispatcher' if in PATH."""
    import shutil
    cli = "agent-dispatcher" if shutil.which("agent-dispatcher") else f"python3 {os.path.abspath(__file__)}"
    args_str = " ".join(args)
    return f"{cli} {subcmd} {args_str}".strip()

def get_latest_execution_id() -> Optional[str]:
    """Find the most recently created or modified execution ID in RUN_LOG_DIR."""
    if not RUN_LOG_DIR.exists():
        return None
    runs = []
    for d in RUN_LOG_DIR.iterdir():
        if d.is_dir() and (d / "meta.json").exists():
            try:
                runs.append((d.stat().st_mtime, d.name))
            except Exception:
                pass
    if not runs:
        return None
    runs.sort(key=lambda x: x[0], reverse=True)
    return runs[0][1]

def cmd_status(args):
    execution_id = args.execution_id or get_latest_execution_id()
    if not execution_id:
        res = {
            "status": "error",
            "message": "No execution ID provided and no previous executions found in /tmp/agent_runs."
        }
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(1)
    task_dir = RUN_LOG_DIR / execution_id

    if not task_dir.exists():
        res = {
            "status": "not_found",
            "execution_id": execution_id,
            "message": f"Execution ID '{execution_id}' not found in {RUN_LOG_DIR}."
        }
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(1)

    meta_path = task_dir / "meta.json"
    manifest_path = task_dir / "audit_manifest.json"
    raw_log_path = task_dir / "raw.log"

    # If audit_manifest exists, the job has finalized
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            status = "success" if (manifest["execution"]["exit_code"] == 0 and not manifest["execution"]["timed_out"]) else "failed"
            res = {
                "status": status,
                "execution_id": execution_id,
                "agent": manifest.get("agent_identity", {}).get("engine"),
                "duration_seconds": manifest["execution"]["duration_seconds"],
                "exit_code": manifest["execution"]["exit_code"],
                "timed_out": manifest["execution"]["timed_out"],
                "newly_modified_files": manifest.get("git_delta", {}).get("newly_modified_files", []),
                "audit_manifest": str(manifest_path),
                "raw_log": str(raw_log_path)
            }
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        except Exception:
            pass

    # Process is either running or completed without finalize
    meta = {}
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            pass

    pid = meta.get("pid")
    agent_name = meta.get("agent")
    tmux_session = meta.get("tmux_session")
    start_time = meta.get("start_time", time.time())
    cwd = meta.get("cwd", os.getcwd())
    uptime = round(time.time() - start_time, 2)

    adapter = get_adapter(agent_name) if agent_name in REGISTRY else None

    # Determine if process/session is alive
    alive = False
    if tmux_session:
        alive = is_tmux_session_alive(tmux_session)
        if alive and not pid:
            pid = get_tmux_session_pid(tmux_session)
    elif pid:
        alive = is_pid_alive(pid)

    # Read log for activity
    log_content = ""
    last_modified_ago = None
    if raw_log_path.exists():
        try:
            stat = raw_log_path.stat()
            last_modified_ago = round(time.time() - stat.st_mtime, 1)
            with open(raw_log_path, "r", encoding="utf-8", errors="replace") as f:
                log_content = f.read()
        except Exception:
            pass

    activity = adapter.parse_activity(log_content) if adapter else "Processing..."
    waiting_input = adapter.check_waiting_input(log_content) if adapter else None

    if alive:
        status_str = "waiting_for_input" if waiting_input else "running"
        res = {
            "status": status_str,
            "execution_id": execution_id,
            "agent": agent_name,
            "pid": pid,
            "uptime_seconds": uptime,
            "last_activity_seconds_ago": last_modified_ago,
            "current_activity": activity,
            "waiting_for_input": waiting_input,
            "raw_log": str(raw_log_path)
        }
        if tmux_session:
            res["tmux_session"] = tmux_session
            res["attach_command"] = f"tmux attach -t {tmux_session}"
            res["reply_command"] = get_cli_command("reply", execution_id, '"<answer>"')
        res["watch_command"] = get_cli_command("watch", execution_id)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        # Process died or finished without manifest
        exit_code = 0
        timed_out = False
        if meta.get("timeout") and uptime > meta.get("timeout"):
            timed_out = True
            exit_code = 124

        identity = adapter.verify_identity() if adapter else None
        opts = DispatchOptions(
            timeout=meta.get("timeout", 120),
            model=meta.get("model"),
            cwd=cwd,
            worktree=meta.get("worktree", False),
            async_mode=True
        )
        git_before = set(meta.get("git_before", []))
        cmd = meta.get("command", [])

        clean_response = finalize_run(
            task_dir=task_dir,
            execution_id=execution_id,
            caller=meta.get("caller", "unknown"),
            identity=identity,
            prompt=meta.get("prompt", ""),
            opts=opts,
            exit_code=exit_code,
            timed_out=timed_out,
            duration=uptime,
            command=cmd,
            git_before=git_before,
            cwd=cwd,
            adapter=adapter
        )
        print(json.dumps(clean_response, indent=2, ensure_ascii=False))

def cmd_cancel(args):
    execution_id = args.execution_id or get_latest_execution_id()
    if not execution_id:
        print(json.dumps({"status": "error", "message": "No execution ID provided and no previous executions found."}, indent=2, ensure_ascii=False))
        sys.exit(1)
    task_dir = RUN_LOG_DIR / execution_id

    if not task_dir.exists():
        print(json.dumps({"status": "not_found", "execution_id": execution_id}, indent=2, ensure_ascii=False))
        sys.exit(1)

    meta_path = task_dir / "meta.json"
    if not meta_path.exists():
        print(json.dumps({"status": "error", "message": "Meta information missing, cannot cancel."}, indent=2, ensure_ascii=False))
        sys.exit(1)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    pid = meta.get("pid")
    tmux_session = meta.get("tmux_session")

    killed = False
    if tmux_session and is_tmux_session_alive(tmux_session):
        kill_tmux_session(tmux_session)
        killed = True

    if pid and is_pid_alive(pid):
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.5)
            if is_pid_alive(pid):
                os.kill(pid, signal.SIGKILL)
            killed = True
        except Exception:
            pass

    if killed:
        res = {"status": "cancelled", "execution_id": execution_id, "message": f"Job {execution_id} cancelled."}
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        res = {"status": "already_stopped", "execution_id": execution_id, "message": f"Job {execution_id} is not currently running."}
        print(json.dumps(res, indent=2, ensure_ascii=False))

def cmd_reply(args):
    """Send user/agent reply into the active session."""
    execution_id = args.execution_id or get_latest_execution_id()
    if not execution_id:
        print(json.dumps({"status": "error", "message": "No execution ID provided and no previous executions found."}, indent=2, ensure_ascii=False))
        sys.exit(1)
    message = args.message
    task_dir = RUN_LOG_DIR / execution_id

    if not task_dir.exists():
        print(json.dumps({"status": "not_found", "execution_id": execution_id}, indent=2, ensure_ascii=False))
        sys.exit(1)

    meta_path = task_dir / "meta.json"
    if not meta_path.exists():
        print(json.dumps({"status": "error", "message": "Meta information missing."}, indent=2, ensure_ascii=False))
        sys.exit(1)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    tmux_session = meta.get("tmux_session")
    if not tmux_session or not is_tmux_session_alive(tmux_session):
        res = {
            "status": "error",
            "execution_id": execution_id,
            "message": f"Session '{tmux_session or execution_id}' is not currently running or not an interactive session."
        }
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(1)

    success = send_tmux_keys(tmux_session, message, enter=True)
    if success:
        res = {
            "status": "sent",
            "execution_id": execution_id,
            "tmux_session": tmux_session,
            "message_sent": message
        }
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        res = {
            "status": "error",
            "execution_id": execution_id,
            "message": f"Failed to send keys to tmux session {tmux_session}."
        }
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(1)

def cmd_watch(args):
    """Live-watch output stream and status of a dispatched agent."""
    execution_id = args.execution_id or get_latest_execution_id()
    if not execution_id:
        print(json.dumps({"status": "error", "message": "No execution ID provided and no previous executions found."}, indent=2, ensure_ascii=False))
        sys.exit(1)
    task_dir = RUN_LOG_DIR / execution_id

    if not task_dir.exists():
        print(json.dumps({"status": "not_found", "execution_id": execution_id}, indent=2, ensure_ascii=False))
        sys.exit(1)

    raw_log_path = task_dir / "raw.log"
    meta_path = task_dir / "meta.json"
    manifest_path = task_dir / "audit_manifest.json"

    meta = {}
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            pass

    tmux_session = meta.get("tmux_session")
    print(f"=== Watching execution {execution_id} ===")
    if tmux_session:
        print(f"Direct terminal attach: tmux attach -t {tmux_session}")
    print("Streaming log (Ctrl+C to stop watching)...\n")

    # Read existing and tail
    file_pos = 0
    if raw_log_path.exists():
        with open(raw_log_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            sys.stdout.write(content)
            sys.stdout.flush()
            file_pos = f.tell()

    try:
        while True:
            # Check if finalized
            if manifest_path.exists():
                print(f"\n=== Execution {execution_id} finalized ===")
                break

            # Read new log content
            if raw_log_path.exists():
                with open(raw_log_path, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(file_pos)
                    new_chunk = f.read()
                    if new_chunk:
                        sys.stdout.write(new_chunk)
                        sys.stdout.flush()
                        file_pos = f.tell()

            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nWatcher stopped.")

def cmd_run(args):
    agent_name = args.agent
    caller = (args.caller or "").strip().lower()
    prompt = args.prompt
    cwd = os.path.abspath(args.cwd or os.getcwd())

    # Anti-Self-Dispatch Enforcement
    if caller and caller == agent_name.lower():
        other_agents = [name for name in REGISTRY.keys() if name != caller]
        native_tool_hint = (
            "If you intended to run internal tasks using your own quota, use your own agent's native subagent/task execution tools instead of this external CLI wrapper. "
            f"If your goal is to offload quota to external agents, dispatch to one of: {other_agents}."
        )
        res = {
            "status": "error",
            "error_type": "SelfDispatchForbidden",
            "message": f"Self-dispatch via CLI is forbidden. Caller '{caller}' attempted to dispatch to itself ('{agent_name}').",
            "guidance": native_tool_hint,
            "external_alternatives": other_agents
        }
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(2)

    adapter = get_adapter(agent_name)
    identity = adapter.verify_identity()

    if not identity.is_available:
        res = {
            "status": "error",
            "error_type": "BinaryNotFound",
            "message": f"Agent '{agent_name}' is not installed or not in PATH.",
            "agent_identity": identity.to_dict()
        }
    # Determine interactive mode: default True if tmux is installed, unless user explicitly disabled it or requested non-interactive async
    raw_interactive = getattr(args, "interactive", None)
    async_mode = getattr(args, "async_mode", False)
    if raw_interactive is None:
        interactive = has_tmux() and not async_mode
    else:
        interactive = raw_interactive

    opts = DispatchOptions(
        timeout=args.timeout,
        model=args.model,
        cwd=cwd,
        worktree=args.worktree,
        dry_run=args.dry_run,
        async_mode=async_mode,
        interactive=interactive,
        idle_timeout=getattr(args, "idle_timeout", 120),
        checkin_interval=getattr(args, "checkin_interval", 0)
    )

    try:
        command = adapter.build_command(prompt, opts)
    except Exception as e:
        res = {
            "status": "error",
            "error_type": "CommandBuildError",
            "message": str(e),
            "agent_identity": identity.to_dict()
        }
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(1)

    # If dry-run requested, output planned execution and exit
    if opts.dry_run:
        dry_run_res = {
            "status": "dry_run",
            "caller": caller or "unknown",
            "target_agent": identity.to_dict(),
            "target_cwd": cwd,
            "prompt": prompt,
            "planned_command": command,
            "options": vars(opts)
        }
        print(json.dumps(dry_run_res, indent=2, ensure_ascii=False))
        return

    execution_id = f"disp-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    task_dir = RUN_LOG_DIR / execution_id
    task_dir.mkdir(parents=True, exist_ok=True)
    raw_log_path = task_dir / "raw.log"
    meta_path = task_dir / "meta.json"

    # Git state before execution
    git_before = get_git_status_files(cwd)
    start_time = time.time()

    # If interactive mode requested and tmux is available, launch inside a detached tmux session with unbuffered pipe to raw.log
    if opts.interactive and has_tmux():
        tmux_session = execution_id
        # Build command that pipes output to raw_log_path in real-time
        # Use shlex.join to construct safe shell execution inside tmux
        import shlex
        escaped_cmd = " ".join(shlex.quote(c) for c in command)
        tmux_shell_cmd = f"{escaped_cmd} 2>&1 | tee -a {shlex.quote(str(raw_log_path))}"

        subprocess.run(
            ["tmux", "new-session", "-d", "-s", tmux_session, "-c", cwd, f"bash -c {shlex.quote(tmux_shell_cmd)}"],
            check=True
        )

        time.sleep(0.5)
        pane_pid = get_tmux_session_pid(tmux_session)

        meta = {
            "execution_id": execution_id,
            "pid": pane_pid,
            "tmux_session": tmux_session,
            "interactive": True,
            "caller": caller,
            "agent": agent_name,
            "prompt": prompt,
            "command": command,
            "cwd": cwd,
            "timeout": opts.timeout,
            "model": opts.model,
            "worktree": opts.worktree,
            "start_time": start_time,
            "git_before": list(git_before)
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        interactive_res = {
            "status": "launched_interactive",
            "execution_id": execution_id,
            "caller": caller or "unknown",
            "agent": {
                "name": identity.engine,
                "version": identity.version,
                "binary": identity.binary_path
            },
            "tmux_session": tmux_session,
            "pane_pid": pane_pid,
            "user_attach_command": f"tmux attach -t {tmux_session}",
            "check_status_command": get_cli_command("status", execution_id),
            "reply_command": get_cli_command("reply", execution_id, '"<answer>"'),
            "watch_command": get_cli_command("watch", execution_id),
            "cancel_command": get_cli_command("cancel", execution_id),
            "raw_log": str(raw_log_path)
        }
        print(json.dumps(interactive_res, indent=2, ensure_ascii=False))
        return

    # If async requested, launch process in background and return immediately
    if opts.async_mode:
        log_file = open(raw_log_path, "w", encoding="utf-8")
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True
        )
        meta = {
            "execution_id": execution_id,
            "pid": process.pid,
            "caller": caller,
            "agent": agent_name,
            "prompt": prompt,
            "command": command,
            "cwd": cwd,
            "timeout": opts.timeout,
            "model": opts.model,
            "worktree": opts.worktree,
            "start_time": start_time,
            "git_before": list(git_before)
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        async_res = {
            "status": "launched_async",
            "execution_id": execution_id,
            "caller": caller or "unknown",
            "agent": {
                "name": identity.engine,
                "version": identity.version,
                "binary": identity.binary_path
            },
            "pid": process.pid,
            "check_status_command": get_cli_command("status", execution_id),
            "watch_command": get_cli_command("watch", execution_id),
            "cancel_command": get_cli_command("cancel", execution_id),
            "raw_log": str(raw_log_path)
        }
        print(json.dumps(async_res, indent=2, ensure_ascii=False))
        return

    # Synchronous execution
    exit_code = -1
    timed_out = False
    process = None
    try:
        with open(raw_log_path, "w", encoding="utf-8") as log_file:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True
            )
            # Save meta for visibility during synchronous runs too
            meta = {
                "execution_id": execution_id,
                "pid": process.pid,
                "caller": caller,
                "agent": agent_name,
                "prompt": prompt,
                "command": command,
                "cwd": cwd,
                "timeout": opts.timeout,
                "model": opts.model,
                "worktree": opts.worktree,
                "start_time": start_time,
                "git_before": list(git_before)
            }
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)

            # Adaptive wait loop with Check-in and Idle Timeout
            last_checkin_time = start_time
            last_activity_time = start_time
            last_log_size = 0

            while True:
                ret = process.poll()
                if ret is not None:
                    exit_code = ret
                    break

                now = time.time()
                # Check log file size/mtime for activity
                if raw_log_path.exists():
                    try:
                        current_size = raw_log_path.stat().st_size
                        if current_size > last_log_size:
                            last_log_size = current_size
                            last_activity_time = now
                    except Exception:
                        pass

                # 1. Idle timeout check: agent produced zero output for idle_timeout seconds
                if opts.idle_timeout > 0 and (now - last_activity_time) > opts.idle_timeout:
                    process.kill()
                    timed_out = True
                    exit_code = 124
                    with open(raw_log_path, "a", encoding="utf-8") as lf:
                        lf.write(f"\n[dispatcher] Terminated due to inactivity (idle > {opts.idle_timeout}s).\n")
                    break

                # 2. Check-in interval: trigger status report instead of kill
                if opts.checkin_interval > 0 and (now - last_checkin_time) >= opts.checkin_interval:
                    last_checkin_time = now
                    # Read recent activity
                    log_sample = ""
                    try:
                        with open(raw_log_path, "r", encoding="utf-8", errors="replace") as lf:
                            log_sample = lf.read()
                    except Exception:
                        pass
                    activity = adapter.parse_activity(log_sample)
                    waiting_input = adapter.check_waiting_input(log_sample)

                    # Explicit Wakeup Signal for Main Agent
                    checkin_event = {
                        "status": "wakeup_trigger",
                        "execution_id": execution_id,
                        "uptime_seconds": round(now - start_time, 1),
                        "idle_seconds": round(now - last_activity_time, 1),
                        "raw_log": str(raw_log_path),
                        "action_required": "WAKEUP_MAIN_AGENT_TO_INSPECT_LOG",
                        "quick_hint": activity,
                        "message": f"Timeout checkpoint reached ({round(now - start_time, 1)}s). External agent is still running. Main agent: inspect raw.log directly to assess real progress."
                    }
                    print(json.dumps(checkin_event, ensure_ascii=False), flush=True)

                # 3. Hard timeout check (only if checkin_interval == 0 and timeout > 0)
                if opts.checkin_interval == 0 and opts.timeout > 0 and (now - start_time) > opts.timeout:
                    process.kill()
                    timed_out = True
                    exit_code = 124
                    with open(raw_log_path, "a", encoding="utf-8") as lf:
                        lf.write(f"\n[dispatcher] Terminated due to hard timeout ({opts.timeout}s).\n")
                    break

                time.sleep(1.0)
    except Exception as e:
        exit_code = 1
        with open(raw_log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"\nExecution exception: {e}\n")

    duration = round(time.time() - start_time, 2)
    clean_response = finalize_run(
        task_dir=task_dir,
        execution_id=execution_id,
        caller=caller,
        identity=identity,
        prompt=prompt,
        opts=opts,
        exit_code=exit_code,
        timed_out=timed_out,
        duration=duration,
        command=command,
        git_before=git_before,
        cwd=cwd,
        adapter=adapter
    )

    print(json.dumps(clean_response, indent=2, ensure_ascii=False))
    if clean_response["status"] != "success":
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Universal Coding Agent Dispatcher CLI")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # list-agents
    subparsers.add_parser("list-agents", help="List all supported agents and their availability")

    # verify
    verify_parser = subparsers.add_parser("verify", help="Verify the identity and version of a specific agent")
    verify_parser.add_argument("agent", choices=list(REGISTRY.keys()), help="Agent name to verify")

    # list-models
    models_parser = subparsers.add_parser("list-models", help="List available models for a specific agent")
    models_parser.add_argument("agent", choices=list(REGISTRY.keys()), help="Agent name to query models for")


    # status
    status_parser = subparsers.add_parser("status", help="Check status, activity or result of a dispatched execution")
    status_parser.add_argument("execution_id", nargs="?", default=None, help="Execution ID returned from run (defaults to latest)")

    # cancel
    cancel_parser = subparsers.add_parser("cancel", help="Cancel a running execution")
    cancel_parser.add_argument("execution_id", nargs="?", default=None, help="Execution ID to cancel (defaults to latest)")

    # reply
    reply_parser = subparsers.add_parser("reply", help="Send input/reply to an active interactive session")
    reply_parser.add_argument("message", help="Message or option to send to the running agent")
    reply_parser.add_argument("--id", dest="execution_id", default=None, help="Execution ID to reply to (defaults to latest)")

    # watch
    watch_parser = subparsers.add_parser("watch", help="Live watch output stream and progress of an agent session")
    watch_parser.add_argument("execution_id", nargs="?", default=None, help="Execution ID to watch (defaults to latest)")

    # run
    run_parser = subparsers.add_parser("run", help="Dispatch a task to a coding agent")
    run_parser.add_argument("agent", choices=list(REGISTRY.keys()), help="Target agent")
    run_parser.add_argument("prompt", help="The task prompt to execute")
    run_parser.add_argument("--caller", type=str, default=None, help="The identity of the calling agent (e.g. agy, cline, opencode) to prevent self-dispatch")
    run_parser.add_argument("--timeout", type=int, default=120, help="Max execution timeout in seconds (default: 120)")
    run_parser.add_argument("--model", type=str, default=None, help="Override model for the session")
    run_parser.add_argument("--cwd", type=str, default=None, help="Working directory (default: current dir)")
    run_parser.add_argument("--worktree", action="store_true", help="Run in a separate git worktree if supported")
    run_parser.add_argument("--dry-run", action="store_true", help="Display planned execution command without running")
    run_parser.add_argument("--async", dest="async_mode", action="store_true", help="Launch agent in background and return execution ID immediately (non-interactive)")
    run_parser.add_argument("--interactive", dest="interactive", action="store_true", default=None, help="Explicitly enable tmux interactive session (default: True if tmux installed)")
    run_parser.add_argument("--no-interactive", dest="interactive", action="store_false", help="Disable tmux session and run as standard subprocess")
    run_parser.add_argument("--idle-timeout", type=int, default=120, help="Max allowed idle seconds with no new output before considering agent stalled (default: 120)")
    run_parser.add_argument("--checkin", dest="checkin_interval", type=int, default=0, help="Interval in seconds to yield a health check-in status report instead of hard termination")

    args = parser.parse_args()

    if args.subcommand == "list-agents":
        cmd_list(args)
    elif args.subcommand == "verify":
        cmd_verify(args)
    elif args.subcommand == "list-models":
        cmd_list_models(args)
    elif args.subcommand == "status":
        cmd_status(args)
    elif args.subcommand == "cancel":
        cmd_cancel(args)
    elif args.subcommand == "reply":
        cmd_reply(args)
    elif args.subcommand == "watch":
        cmd_watch(args)
    elif args.subcommand == "run":
        cmd_run(args)

if __name__ == "__main__":
    main()
