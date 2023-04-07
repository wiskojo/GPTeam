import os
import subprocess
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

log_dir = "logs"
num_logs = 4
tmux_session = "tmux_tail_logs"


class LogFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".log"):
            return
        update_tmux_tail()


def get_latest_logs(k):
    log_files = [
        os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith(".log")
    ]
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return log_files[:k]


def run_tmux_cmd(*args):
    subprocess.run(["tmux"] + list(args))


def update_tmux_tail():
    latest_logs = get_latest_logs(num_logs)

    if len(latest_logs) == 0:
        return

    run_tmux_cmd("kill-pane", "-a")

    # Create new panes with tail -f
    for idx, log in enumerate(latest_logs):
        if idx % 2 == 0:
            run_tmux_cmd("split-window", "-v", f"tail -f {log}")
        else:
            run_tmux_cmd("split-window", "-h", f"tail -f {log}")

    run_tmux_cmd(
        "kill-pane", "-t", "0"
    )  # Kill the first pane which doesn't have tail -f running
    run_tmux_cmd("select-layout", "tile")


if __name__ == "__main__":
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a new tmux session
    subprocess.run(["tmux", "new-session", "-d", "-s", tmux_session])

    update_tmux_tail()

    event_handler = LogFileHandler()
    observer = Observer()
    observer.schedule(event_handler, log_dir, recursive=False)
    observer.start()

    try:
        # Attach to the tmux session
        subprocess.run(["tmux", "attach-session", "-t", tmux_session])
    except KeyboardInterrupt:
        pass

    observer.stop()
    observer.join()

    # Kill the tmux session
    subprocess.run(["tmux", "kill-session", "-t", tmux_session])
