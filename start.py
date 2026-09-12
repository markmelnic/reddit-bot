"""Start script for Render/Railway running Flask Web Control Panel and background bot."""

import os
import sys
import threading
import time
import subprocess
from web_dashboard import run_web_dashboard, log_message

PORT = int(os.environ.get("PORT", 3000))

def background_bot_loop():
    # Wait a few seconds for web server to boot up
    time.sleep(5)
    while True:
        log_message("Starting automated background bot execution cycle...")
        cmd = [sys.executable, "-u", "main.py", "--verbose", "-a", "accounts.txt", "-l", "links.txt", "--headless", "--session-persistence"]
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                log_message(line.strip())
            process.wait()
            log_message(f"Bot cycle completed with exit code {process.returncode}. Sleeping for 1 hour...")
        except Exception as e:
            log_message(f"Error in background bot loop: {e}")
        time.sleep(3600)

if __name__ == "__main__":
    log_message("Initializing Reddit Bot Cloud Service...")
    
    # Start background bot thread
    bot_thread = threading.Thread(target=background_bot_loop, daemon=True)
    bot_thread.start()

    # Run Flask Web Dashboard on main thread (port 3000)
    run_web_dashboard(port=PORT)
