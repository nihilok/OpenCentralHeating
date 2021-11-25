import grp
import signal
import subprocess
import os
import sys
import sqlite3
from pwd import getpwnam

LOG_DIR = "/var/log/heating"
LOCAL_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    user = os.getenv('SUDO_USER')
    UID = int(getpwnam(user).pw_uid)
    print(f'Using UID {UID} ({user}) for permissions')
except ValueError:
    print("Using default UID (1000) for permissions")
    UID = 1000

try:
    os.makedirs(LOG_DIR, mode=0o764)
except FileExistsError:
    print("WARNING: Log directory already exists")

if not os.path.exists(LOG_DIR + "/heating.log"):
    print(f'Creating log file in {LOG_DIR}')
    try:
        GID = grp.getgrnam('adm')[2]
        os.chown(LOG_DIR, UID, GID)
        os.chdir(LOG_DIR)
        open("heating.log", "a").close()
        os.chown("heating.log", UID, GID)
        os.chmod("heating.log", 0o764)
    except PermissionError:
        print(
            "PermissionError: you need to run the install script with sudo\n\n   $ sudo python3 install.py"
        )
        sys.exit()

os.chdir(LOCAL_DIR)
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

if not os.path.exists(f"{LOCAL_DIR}/env"):
    print("creating Python virtual environment...")
    subprocess.run(["python3", "-m", "venv", "env"])
    print("Installing requirements...")
    subprocess.run([f"{LOCAL_DIR}/env/bin/pip", "install", "-r", "requirements.txt"])
    print("\n****Done****\n")
else:
    print('WARNING: Virtual environment already exists')

if not os.path.exists('db.sqlite3'):
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
                    'Installation  complete!\n\nUse command "open-heating" to run the server.',
                    end="\n\n",
                )
                process.send_signal(signal.SIGINT)
else:
    print('WARNING: db.sqlite3 already exists')

conn = sqlite3.connect("db.sqlite3")
c = conn.cursor()
if not len(list((c.execute("SELECT * FROM householdmember where id=1")))):
    print("=====================================================")
    print("Please create a superuser...", end="\n\n")
    subprocess.run([f"{LOCAL_DIR}/env/bin/python", "create_superuser.py"])
else:
    print('Superuser already exists')
conn.close()
