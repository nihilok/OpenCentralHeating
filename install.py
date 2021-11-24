import signal
import subprocess
import os
import time

UID = 1000

LOG_DIR = '/var/log/heating'
try:
    os.makedirs(LOG_DIR, mode=0o777)
except FileExistsError:
    print('WARNING: Log directory already exists')
os.chdir(LOG_DIR)
open('heating.log', 'a').close()
os.chown(LOG_DIR, 0, UID)
os.chown('heating.log', UID, UID)

with open('run.sh', 'w') as f:
    f.write('''#!/usr/bin/env bash

source env/bin/activate
python main.py''')
os.chmod('run.sh', 0o755)
os.chown('run.sh', UID, UID)
subprocess.run(['ln', 'run.sh', '/usr/local/bin/open-heating'])

os.setuid(UID)
LOCAL_DIR = os.path.abspath(os.path.dirname(__file__))
os.chdir(LOCAL_DIR)
subprocess.run(['python3', '-m', 'venv', 'env'])
subprocess.run([f'{LOCAL_DIR}/env/bin/pip', 'install', '-r', 'requirements.txt'])
proc = subprocess.Popen([f'{LOCAL_DIR}/env/bin/python3', 'main.py'])
time.sleep(10)
subprocess.run(['wget', '-O', '/dev/null', '-o', '/dev/null', 'http://localhost:8080/docs'])
proc.send_signal(signal.SIGINT)
time.sleep(5)
proc.send_signal(signal.SIGINT)
print('=====================================================')
print('Please create a superuser...', end='\n\n')
subprocess.run([f'{LOCAL_DIR}/env/bin/python', 'create_superuser.py'])
