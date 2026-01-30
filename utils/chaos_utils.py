"""
Chaos Testing Utilities
Helper functions for chaos testing framework
"""

import subprocess
import sys
import time
from pathlib import Path

import psutil


def start_worker_process() -> subprocess.Popen:
    """
    Start worker process in background.
    
    Returns:
        subprocess.Popen: Running worker process
    
    Raises:
        RuntimeError: If worker fails to start
    """
    print("Starting worker process...")
    
    worker_script = Path.cwd() / "temporal" / "workers" / "worker.py"
    
    process = subprocess.Popen(
        [sys.executable, str(worker_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    
    # Wait for worker to initialize
    time.sleep(3)
    
    if process.poll() is None:
        print(f"  Worker PID: {process.pid}")
        print(f"  Worker running: YES")
        return process
    else:
        raise RuntimeError("Worker failed to start")


def kill_worker_process(worker_pid: int) -> bool:
    """
    Kill worker process forcefully (SIGKILL).
    
    Args:
        worker_pid: Process ID to kill
    
    Returns:
        bool: True if killed, False if already dead
    """
    print(f"\nKILLING WORKER (PID: {worker_pid})...")
    
    try:
        process = psutil.Process(worker_pid)
        process.kill()  # SIGKILL - immediate termination
        print(f"  Worker killed forcefully")
        return True
    except psutil.NoSuchProcess:
        print(f"  Worker already dead")
        return False


def cleanup_worker(worker: subprocess.Popen, timeout: int = 5):
    """
    Cleanup worker process gracefully.
    
    Args:
        worker: Worker process to clean up
        timeout: Seconds to wait before force kill
    """
    if worker and worker.poll() is None:
        worker.terminate()
        try:
            worker.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            worker.kill()
