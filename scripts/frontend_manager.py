#!/usr/bin/env python3
"""
Frontend Process Manager - Daemon process manager with auto-restart
Manages the frontend server as a background daemon with monitoring and auto-restart
"""

import os
import sys
import time
import signal
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
PID_FILE = PROJECT_ROOT / "logs" / "frontend.pid"
LOG_FILE = PROJECT_ROOT / "logs" / "frontend.log"
ERROR_LOG_FILE = PROJECT_ROOT / "logs" / "frontend_error.log"
SERVE_SCRIPT = PROJECT_ROOT / "frontend" / "serve.py"
VENV_PYTHON = PROJECT_ROOT / "venv" / "bin" / "python3"

# Process manager configuration
MAX_RESTART_ATTEMPTS = 5
RESTART_WINDOW = 60  # seconds
MIN_UPTIME = 3  # seconds - if process dies before this, it's a fast crash


class FrontendManager:
    """Manages the frontend server as a daemon process"""

    def __init__(self):
        self.pid = None
        self.restart_attempts = []
        self.ensure_logs_dir()

    def ensure_logs_dir(self):
        """Create logs directory if it doesn't exist"""
        logs_dir = PROJECT_ROOT / "logs"
        logs_dir.mkdir(exist_ok=True)

    def log(self, message, level="INFO"):
        """Write to manager log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}\n"

        with open(LOG_FILE, "a") as f:
            f.write(log_msg)

        # Also print to console when not in daemon mode
        if not self.is_daemon_running():
            print(f"{log_msg.strip()}")

    def read_pid(self):
        """Read PID from PID file"""
        if PID_FILE.exists():
            try:
                with open(PID_FILE, "r") as f:
                    return int(f.read().strip())
            except (ValueError, IOError):
                return None
        return None

    def write_pid(self, pid):
        """Write PID to PID file"""
        with open(PID_FILE, "w") as f:
            f.write(str(pid))

    def remove_pid(self):
        """Remove PID file"""
        if PID_FILE.exists():
            PID_FILE.unlink()

    def is_process_running(self, pid):
        """Check if process with given PID is running"""
        if pid is None:
            return False
        try:
            os.kill(pid, 0)  # Doesn't actually kill, just checks if process exists
            return True
        except OSError:
            return False

    def is_daemon_running(self):
        """Check if daemon is currently running"""
        pid = self.read_pid()
        return self.is_process_running(pid)

    def start_frontend_process(self):
        """Start the frontend server process"""
        self.log("Starting frontend server process...")

        try:
            # Open log files for subprocess output
            log_f = open(LOG_FILE, "a")
            error_f = open(ERROR_LOG_FILE, "a")

            # Write header to logs
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_f.write(f"\n{'='*60}\n")
            log_f.write(f"Frontend Server Started: {timestamp}\n")
            log_f.write(f"{'='*60}\n\n")
            log_f.flush()

            # Start the frontend server
            process = subprocess.Popen(
                [str(VENV_PYTHON), str(SERVE_SCRIPT)],
                stdout=log_f,
                stderr=error_f,
                cwd=str(PROJECT_ROOT),
                start_new_session=True  # Detach from parent process
            )

            self.log(f"Frontend server started with PID: {process.pid}")
            return process

        except Exception as e:
            self.log(f"Failed to start frontend server: {e}", "ERROR")
            raise

    def monitor_process(self, process):
        """Monitor a process and return when it exits"""
        start_time = time.time()
        try:
            process.wait()
            uptime = time.time() - start_time
            return uptime
        except KeyboardInterrupt:
            self.log("Monitor interrupted by user", "INFO")
            return None

    def should_restart(self, uptime):
        """Determine if process should be restarted based on crash history"""
        now = time.time()

        # Clean old restart attempts outside the window
        self.restart_attempts = [
            t for t in self.restart_attempts
            if now - t < RESTART_WINDOW
        ]

        # Add current restart attempt
        self.restart_attempts.append(now)

        # Check if we've exceeded max restarts in the time window
        if len(self.restart_attempts) > MAX_RESTART_ATTEMPTS:
            self.log(
                f"Too many restarts ({len(self.restart_attempts)}) in {RESTART_WINDOW}s. Giving up.",
                "ERROR"
            )
            return False

        # If process died very quickly, it's a bad crash
        if uptime is not None and uptime < MIN_UPTIME:
            self.log(
                f"Process died after only {uptime:.1f}s (fast crash). "
                f"Restart attempt {len(self.restart_attempts)}/{MAX_RESTART_ATTEMPTS}",
                "WARNING"
            )

        return True

    def start_daemon(self):
        """Start the frontend server as a daemon with monitoring"""
        # Check if already running
        if self.is_daemon_running():
            pid = self.read_pid()
            print(f"Frontend daemon is already running (PID: {pid})")
            return False

        # Fork to create daemon
        try:
            pid = os.fork()
            if pid > 0:
                # Parent process - wait a moment then exit
                time.sleep(1)
                if self.is_daemon_running():
                    new_pid = self.read_pid()
                    print(f"✓ Frontend daemon started successfully (PID: {new_pid})")
                    print(f"  Logs: {LOG_FILE}")
                    print(f"  Errors: {ERROR_LOG_FILE}")
                    return True
                else:
                    print("✗ Failed to start daemon")
                    return False
        except OSError as e:
            self.log(f"Fork failed: {e}", "ERROR")
            return False

        # Child process (daemon)
        os.setsid()  # Create new session

        # Fork again to prevent zombie
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            self.log(f"Second fork failed: {e}", "ERROR")
            sys.exit(1)

        # Setup daemon environment
        os.chdir(str(PROJECT_ROOT))
        os.umask(0)

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()

        with open("/dev/null", "r") as dev_null:
            os.dup2(dev_null.fileno(), sys.stdin.fileno())

        # Write daemon PID
        self.write_pid(os.getpid())
        self.log(f"Daemon started with PID: {os.getpid()}")

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.handle_sigterm)
        signal.signal(signal.SIGINT, self.handle_sigterm)

        # Start monitoring loop
        self.run_monitoring_loop()

    def handle_sigterm(self, signum, frame):
        """Handle termination signals"""
        self.log(f"Received signal {signum}, shutting down gracefully...")

        # Kill frontend process if running
        pid = self.read_pid()
        if pid and self.is_process_running(pid):
            try:
                # Get the actual server process (child of daemon)
                import psutil
                parent = psutil.Process(os.getpid())
                for child in parent.children(recursive=True):
                    child.terminate()
            except:
                # Fallback if psutil not available
                pass

        self.remove_pid()
        sys.exit(0)

    def run_monitoring_loop(self):
        """Main monitoring loop that keeps restarting the frontend"""
        self.log("Starting monitoring loop")

        while True:
            try:
                process = self.start_frontend_process()
                uptime = self.monitor_process(process)

                if uptime is None:
                    # Interrupted by user
                    break

                self.log(f"Frontend server stopped (uptime: {uptime:.1f}s)", "WARNING")

                # Decide whether to restart
                if self.should_restart(uptime):
                    wait_time = 2
                    self.log(f"Restarting in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.log("Not restarting. Too many failures.", "ERROR")
                    break

            except Exception as e:
                self.log(f"Monitoring loop error: {e}", "ERROR")
                break

        self.log("Monitoring loop ended")
        self.remove_pid()
        sys.exit(0)

    def stop_daemon(self):
        """Stop the daemon process"""
        pid = self.read_pid()

        if not pid:
            print("Frontend daemon is not running (no PID file)")
            return False

        if not self.is_process_running(pid):
            print(f"Frontend daemon is not running (stale PID: {pid})")
            self.remove_pid()
            return False

        print(f"Stopping frontend daemon (PID: {pid})...")

        try:
            # Send SIGTERM for graceful shutdown
            os.kill(pid, signal.SIGTERM)

            # Wait for process to die
            for _ in range(10):
                if not self.is_process_running(pid):
                    print("✓ Frontend daemon stopped successfully")
                    self.remove_pid()
                    return True
                time.sleep(0.5)

            # Force kill if still running
            print("Process didn't stop gracefully, forcing...")
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)

            if not self.is_process_running(pid):
                print("✓ Frontend daemon stopped (forced)")
                self.remove_pid()
                return True
            else:
                print("✗ Failed to stop daemon")
                return False

        except ProcessLookupError:
            print("✓ Process already stopped")
            self.remove_pid()
            return True
        except Exception as e:
            print(f"✗ Error stopping daemon: {e}")
            return False

    def status(self):
        """Show daemon status"""
        pid = self.read_pid()

        print("\n" + "="*60)
        print("Frontend Daemon Status")
        print("="*60)

        if not pid:
            print("Status:    \033[0;31m✗ Not running\033[0m")
            print("\nTo start: make frontend")
        else:
            if self.is_process_running(pid):
                print(f"Status:    \033[0;32m✓ Running\033[0m")
                print(f"PID:       {pid}")

                # Try to get process info
                try:
                    import psutil
                    p = psutil.Process(pid)
                    print(f"Memory:    {p.memory_info().rss / 1024 / 1024:.1f} MB")
                    print(f"CPU:       {p.cpu_percent(interval=0.1):.1f}%")
                    uptime = time.time() - p.create_time()
                    hours = int(uptime // 3600)
                    minutes = int((uptime % 3600) // 60)
                    seconds = int(uptime % 60)
                    print(f"Uptime:    {hours}h {minutes}m {seconds}s")
                except ImportError:
                    pass
                except Exception:
                    pass
            else:
                print(f"Status:    \033[0;31m✗ Not running (stale PID: {pid})\033[0m")

        print(f"\nLog File:   {LOG_FILE}")
        print(f"Error Log:  {ERROR_LOG_FILE}")

        # Show last few log lines
        if LOG_FILE.exists():
            print("\nRecent Logs:")
            print("-" * 60)
            try:
                with open(LOG_FILE, "r") as f:
                    lines = f.readlines()
                    for line in lines[-10:]:
                        print(f"  {line.rstrip()}")
            except Exception as e:
                print(f"  (Could not read logs: {e})")

        print("="*60 + "\n")

    def restart_daemon(self):
        """Restart the daemon"""
        print("Restarting frontend daemon...")
        self.stop_daemon()
        time.sleep(1)
        self.start_daemon()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Frontend Server Process Manager")
    parser.add_argument(
        "command",
        choices=["start", "stop", "restart", "status"],
        help="Command to execute"
    )

    args = parser.parse_args()
    manager = FrontendManager()

    if args.command == "start":
        manager.start_daemon()
    elif args.command == "stop":
        manager.stop_daemon()
    elif args.command == "restart":
        manager.restart_daemon()
    elif args.command == "status":
        manager.status()


if __name__ == "__main__":
    main()
