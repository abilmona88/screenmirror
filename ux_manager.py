import os
import shutil
import subprocess
from typing import Dict, Optional

# Simple in-memory registry of running UxPlay processes.
# Key: label (e.g. "ipad", "iphone")
# Value: subprocess.Popen instance
_processes: Dict[str, subprocess.Popen] = {}


def _resolve_binary(binary_path: str) -> str:
    """
    Resolve the uxplay binary in a tolerant way:

    - Strip whitespace.
    - Expand ~.
    - If it looks like a path and exists, use it.
    - Otherwise, search PATH with shutil.which.
    - If still not found, raise FileNotFoundError.
    """
    candidate = (binary_path or "uxplay").strip()
    candidate = os.path.expanduser(candidate)

    # If it contains a path separator, treat as explicit path
    if os.path.sep in candidate:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
        raise FileNotFoundError(candidate)

    # Otherwise, resolve via PATH
    resolved = shutil.which(candidate)
    if resolved and os.path.isfile(resolved) and os.access(resolved, os.X_OK):
        return resolved

    raise FileNotFoundError(candidate)


def start_instance(
    label: str,
    binary_path: str,
    airplay_name: str,
    base_port: int,
    extra_args: Optional[list] = None,
) -> int:
    """
    Start a UxPlay instance as a background process.

    :param label: Local label for this instance (e.g. "ipad", "iphone").
    :param binary_path: Path or name of the uxplay binary.
    :param airplay_name: Name that iOS devices will see.
    :param base_port: Base TCP/UDP port (UxPlay typically uses base_port, base_port+1, base_port+2).
    :param extra_args: Optional list of additional CLI args to pass to UxPlay.
    :return: PID of the started process.
    :raises RuntimeError: if an instance with this label is already running.
    :raises FileNotFoundError: if the binary cannot be resolved.
    """
    if label in _processes and _processes[label].poll() is None:
        raise RuntimeError(
            f"Instance '{label}' is already running (PID={_processes[label].pid})."
        )

    if extra_args is None:
        extra_args = []

    resolved_binary = _resolve_binary(binary_path)

    cmd = [
        resolved_binary,
        "-n",
        airplay_name,
        "-p",
        str(base_port),
        "-vsync",
        "no",
        *extra_args,
    ]

    # Start process; detach stdio so it won't block.
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _processes[label] = proc
    return proc.pid


def stop_instance(label: str, timeout: float = 5.0) -> bool:
    """
    Stop a running UxPlay instance, if present.

    :param label: Label of the instance to stop.
    :param timeout: Seconds to wait for graceful termination before kill.
    :return: True if a process was stopped, False if nothing was running.
    """
    proc = _processes.get(label)
    if proc is None:
        return False

    if proc.poll() is not None:
        # Already exited
        _processes.pop(label, None)
        return False

    try:
        proc.terminate()
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=timeout)
    finally:
        _processes.pop(label, None)

    return True


def is_running(label: str) -> bool:
    """
    Check if a labeled UxPlay instance is currently running.
    """
    proc = _processes.get(label)
    if proc is None:
        return False
    return proc.poll() is None


def get_pid(label: str) -> Optional[int]:
    """
    Get the PID of a running instance, if any.
    """
    proc = _processes.get(label)
    if proc is None or proc.poll() is not None:
        return None
    return proc.pid


def stop_all(timeout: float = 5.0) -> int:
    """
    Stop all running UxPlay instances.

    :return: Number of instances that were actively stopped.
    """
    labels = list(_processes.keys())
    stopped_count = 0
    for label in labels:
        if stop_instance(label, timeout=timeout):
            stopped_count += 1
    return stopped_count
