import signal
import sys
import subprocess
import os
import time
from threading import Thread

LOG_DIR = '/var/log/heating'
try:
    os.makedirs(LOG_DIR, mode=0o777)
except FileExistsError:
    print('WARNING: Log directory already exists')

os.setuid(1000)
LOCAL_DIR = os.path.abspath(os.path.dirname(__file__))
os.chdir(LOCAL_DIR)
subprocess.run(['python3', '-m', 'venv', 'env'])
print(LOCAL_DIR)
subprocess.run([f'{LOCAL_DIR}/env/bin/pip', 'install', '-r', 'requirements.txt'])

# def start_server():
proc = subprocess.Popen([f'{LOCAL_DIR}/env/bin/python3', 'main.py'])
time.sleep(10)
subprocess.run(['curl', 'http://localhost:8080'])
proc.send_signal(signal.SIGINT)
time.sleep(5)
proc.send_signal(signal.SIGINT)