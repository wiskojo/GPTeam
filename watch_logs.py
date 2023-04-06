import os
import subprocess
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

log_dir = "logs"
num_logs = 4
multitail_cmd = "multitail"
multitail_proc = None


class LogFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".log"):
            return
        update_multitail()


def get_latest_logs():
    log_files = [
        os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith(".log")
    ]
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return log_files[:num_logs]


def update_multitail():
    global multitail_proc

    if multitail_proc:
        multitail_proc.terminate()

    latest_logs = get_latest_logs()
    multitail_args = [multitail_cmd, "-s", "2", "-n", str(num_logs)] + latest_logs
    multitail_proc = subprocess.Popen(multitail_args)


if __name__ == "__main__":
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    update_multitail()

    event_handler = LogFileHandler()
    observer = Observer()
    observer.schedule(event_handler, log_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
    multitail_proc.terminate()
