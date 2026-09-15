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

def cmd_status(args):
    execution_id = args.execution_id
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
    start_time = meta.get("start_time", time.time())
    cwd = meta.get("cwd", os.getcwd())
    uptime = round(time.time() - start_time, 2)

    adapter = get_adapter(agent_name) if agent_name in REGISTRY else None
    alive = is_pid_alive(pid) if pid else False

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

    if alive:
        res = {
            "status": "running",
            "execution_id": execution_id,
            "agent": agent_name,
            "pid": pid,
            "uptime_seconds": uptime,
            "last_activity_seconds_ago": last_modified_ago,
            "current_activity": activity,
            "raw_log": str(raw_log_path)
        }
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
    execution_id = args.execution_id
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
    if pid and is_pid_alive(pid):
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.5)
            if is_pid_alive(pid):
                os.kill(pid, signal.SIGKILL)
            res = {"status": "cancelled", "execution_id": execution_id, "pid": pid, "message": f"Job {execution_id} cancelled."}
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        except Exception as e:
            res = {"status": "error", "execution_id": execution_id, "message": f"Failed to kill process {pid}: {e}"}
            print(json.dumps(res, indent=2, ensure_ascii=False))
            sys.exit(1)
    else:
        res = {"status": "already_stopped", "execution_id": execution_id, "message": f"Job {execution_id} is not currently running."}
        print(json.dumps(res, indent=2, ensure_ascii=False))

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
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(1)

    opts = DispatchOptions(
        timeout=args.timeout,
        model=args.model,
        cwd=cwd,
        worktree=args.worktree,
        dry_run=args.dry_run,
        async_mode=getattr(args, "async_mode", False)
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
            "check_status_command": f"python3 {os.path.abspath(__file__)} status {execution_id}",
            "cancel_command": f"python3 {os.path.abspath(__file__)} cancel {execution_id}",
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

            try:
                process.wait(timeout=opts.timeout if opts.timeout > 0 else None)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                timed_out = True
                exit_code = 124
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

    # status
    status_parser = subparsers.add_parser("status", help="Check status, activity or result of a dispatched execution")
    status_parser.add_argument("execution_id", help="Execution ID returned from run")

    # cancel
    cancel_parser = subparsers.add_parser("cancel", help="Cancel a running execution")
    cancel_parser.add_argument("execution_id", help="Execution ID to cancel")

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
    run_parser.add_argument("--async", dest="async_mode", action="store_true", help="Launch agent in background and return execution ID immediately")

    args = parser.parse_args()

    if args.subcommand == "list-agents":
        cmd_list(args)
    elif args.subcommand == "verify":
        cmd_verify(args)
    elif args.subcommand == "status":
        cmd_status(args)
    elif args.subcommand == "cancel":
        cmd_cancel(args)
    elif args.subcommand == "run":
        cmd_run(args)

if __name__ == "__main__":
    main()
