import signal
import subprocess
import os
import sys
import sqlite3

try:
    UID = int(sys.argv[-1])
except Exception:
    print("Using default UID (1000) for permissions")
    UID = 1000

LOG_DIR = "/var/log/heating"
try:
    os.makedirs(LOG_DIR, mode=0o665)
except FileExistsError:
    print("WARNING: Log directory already exists")

if not os.path.exists(LOG_DIR + "/heating.log"):
    try:
        os.chown(LOG_DIR, 0, UID)
        os.chdir(LOG_DIR)
        open("heating.log", "a").close()
        os.chown("heating.log", UID, UID)
    except PermissionError:
        print(
            "PermissionError: you need to run the install script with sudo\n\n   $ sudo python3 install.py"
        )
        sys.exit()

with open("run.sh", "w") as f:
    f.write(
        """#!/usr/bin/env bash

source env/bin/activate
python main.py"""
    )
os.chmod("run.sh", 0o755)
os.chown("run.sh", UID, UID)
subprocess.run(["ln", "run.sh", "/usr/local/bin/open-heating"])

os.setuid(UID)
LOCAL_DIR = os.path.abspath(os.path.dirname(__file__))
os.chdir(LOCAL_DIR)
print("creating Python virtual environment...")
subprocess.run(["python3", "-m", "venv", "env"])
print("Installing requirements")
subprocess.run(
    [f"{LOCAL_DIR}/env/bin/pip", "install", "-r", "requirements.txt"],
)
with subprocess.Popen(
    [f"{LOCAL_DIR}/env/bin/python3", "main.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True,
) as process:
    print("Creating database...")
    for line in process.stdout:
        if "Application startup complete" in line:
            print("API started successfully")
            subprocess.run(
                [
                    "wget",
                    "-O",
                    "/dev/null",
                    "-o",
                    "/dev/null",
                    "http://localhost:8080/docs",
                ]
            )
            process.send_signal(signal.SIGINT)
        if "Stopping reloader process" in line:
            print(
                'Installation  complete!\n\nUse command "open-heating" to run the server.'
            )
            process.send_signal(signal.SIGINT)
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    if not c.execute("SELECT * FROM householdmember where id=1"):
        print("=====================================================")
        print("Please create a superuser...", end="\n\n")
        subprocess.run([f"{LOCAL_DIR}/env/bin/python", "create_superuser.py"])
    conn.close()
