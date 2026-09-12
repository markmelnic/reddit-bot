"""Flask Web Control Panel for Reddit Bot on Render/Railway."""

import os
import json
import threading
import subprocess
import sys
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# Global log buffer
LOG_BUFFER = []
MAX_LOG_LINES = 500

def log_message(msg: str):
    print(msg, flush=True)
    LOG_BUFFER.append(msg)
    if len(LOG_BUFFER) > MAX_LOG_LINES:
        LOG_BUFFER.pop(0)

def get_accounts_info():
    username = ""
    password = ""
    accounts_file = Path("accounts.txt")
    if accounts_file.exists():
        try:
            line = accounts_file.read_text().strip()
            if "|" in line:
                username, password = line.split("|", 1)
        except Exception:
            pass
    return username, password

@app.route("/")
def index():
    username, password = get_accounts_info()
    logs = "\n".join(LOG_BUFFER) if LOG_BUFFER else "No logs yet. Click 'Run Bot Now' or wait for background execution."
    return render_template("index.html", username=username, password=password, logs=logs)

@app.route("/api/logs")
def api_logs():
    return jsonify({"logs": "\n".join(LOG_BUFFER) if LOG_BUFFER else "No logs yet."})

@app.route("/save_account", methods=["POST"])
def save_account():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    if username and password:
        accounts_file = Path("accounts.txt")
        accounts_file.write_text(f"{username}|{password}\n")
        log_message(f"[WEB] Updated account credentials for: {username}")
    return redirect(url_for("index"))

@app.route("/save_cookies", methods=["POST"])
def save_cookies():
    cookies_input = request.form.get("cookies_json", "").strip()
    username, _ = get_accounts_info()
    if not username:
        username = "AppropriateChance699"
        
    if cookies_input:
        try:
            session_dir = Path("sessions")
            session_dir.mkdir(parents=True, exist_ok=True)
            session_file = session_dir / f"{username}.cookies"
            
            if cookies_input.startswith("["):
                cookies = json.loads(cookies_input)
            else:
                cookies = [
                    {
                        "name": "reddit_session",
                        "value": cookies_input,
                        "domain": ".reddit.com",
                        "path": "/"
                    }
                ]
                
            session_file.write_text(json.dumps(cookies, indent=2))
            log_message(f"[WEB] Successfully saved reddit_session cookie for {username}!")
        except Exception as e:
            log_message(f"[WEB] Error saving cookies: {e}")
            
    return redirect(url_for("index"))

@app.route("/run_bot", methods=["POST"])
def run_bot_endpoint():
    log_message("[WEB] Manual bot execution triggered from Control Panel...")
    threading.Thread(target=execute_bot_subprocess, daemon=True).start()
    return redirect(url_for("index"))

def execute_bot_subprocess():
    try:
        cmd = [sys.executable, "-u", "main.py", "--verbose", "-a", "accounts.txt", "-l", "links.txt", "--headless", "--session-persistence"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            log_message(line.strip())
        process.wait()
        log_message(f"[WEB] Bot process finished with exit code {process.returncode}")
    except Exception as e:
        log_message(f"[WEB] Error running bot subprocess: {e}")

def run_web_dashboard(port=3000):
    log_message(f"Starting Flask Web Control Panel on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
