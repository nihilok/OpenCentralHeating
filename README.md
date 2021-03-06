# Open Central Heating API
###### This repository succeeds [SmartHomeApp](https://github.com/nihilok/SmartHomeApp) but focuses only on the central heating features.


### How to install on Ubuntu Server
#### Prerequisites
- Python3.7+
- Git
- Redis (`sudo apt install redis-server`)

if you don't have pip3 and/or venv installed run:
```sh
sudo apt install python3-pip -y
sudo apt install python3-venv -y
```
_If you use the included installation script, it will automatically create a Virtual Environment and install the requirements._

#### Installation
```bash
git clone https://github.com/nihilok/OpenCentralHeating.git
cd OpenCentralHeating
sudo python3 install.py
```
You will be prompted to create a Superuser in the database who can then create new users via the API.

You will also be prompted for other information:
- the number of heating loops you want to control.
- the URL/IP of the temperature sensor (microcontroller) of each loop (leave blank for test mode)
- the IP of the Raspberry Pi controlling the relay for each loop (leave blank if installing on the Pi itself)
- the number of the GPIO pin controlling the relay of each loop. (If same Pi, these must all be different obviously.)

Heating systems can also be added / setup / updated and removed via the API.

If you are running the script for a second time, the setup information you provide here will overwrite the previous 
inputs. You can choose '`n`' to skip this step. 
The rest of the installation script should be idempotent, unless stopped halfway through the first time, in which 
case you should remove the `env` directory from the repository directory, and run the script again. If the log 
directory has already been created (`/var/log/heating/`), you can run the script without `sudo` (`python3 install.py`)

You should now start the server from any directory with the command `open-heating`, due to the symlink at 
`/usr/local/bin/open-heating` and you can interact with the API via the swagger interface at http://localhost:8080/docs

If you want to run the server continuously and serve over a network or the internet, I suggest using Nginx 
(`sudo apt install nginx`) and creating a server block that acts a proxy to http://localhost:8080, and then using 
Supervisor (`sudo apt install supervisor`) to run the API in the background (on the same port).

To build the front-end application, cd into the frontend-app directory and install the package with npm or yarn 
(`yarn install`). Now run `yarn build` (or `npm run build`) to create the production build. You can now serve the build 
directory that has been created as you wish, for example using Nginx as above.

Your nginx config (e.g. `/etc/nginx/sites-available/heating`) might look like this:
```nginx config
# React app:
server {
    listen 80;
    server_name heating.example.app;
    location / {
        root /home/$USER/apps/OpenCentralHeating/frontend-app/build;
        index index.html;
        try_files $uri /index.html$is_args$args =404;
    }	
}

# Backend:
server {
    listen 80;
    server_name api.heating.example.app;
    location / {
        proxy_pass http://localhost:8080;
        include /etc/nginx/proxy_params;
        proxy_redirect off;
    }
}

# Proxy to sensor 1
server {
    listen 80;
    server_name upstairs.sensor.example.app;
    location / {
        proxy_pass http://192.168.1.100;
        include /etc/nginx/proxy_params;
        proxy_redirect off;
    }
}

# Proxy to sensor 2
server {
    listen 80;
    server_name downstairs.sensor.example.app;
    location / {
        proxy_pass http://192.168.1.101;
        include /etc/nginx/proxy_params;
        proxy_redirect off;
    }
}
```

And your supervisor program group conf (e.g. `/etc/supervisor/conf.d/heating.conf`) might look like this:
```
[program:heating]
directory=/home/$USER/apps/OpenCentralHeating
command=open-heating
user=$USER
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stdout_logfile=/var/log/heating/heating-out.log
stdout_logfile_maxbytes=1MB
stdout_logfile_backups=10
stdout_capture_maxbytes=1MB
stdout_events_enabled=false
stderr_logfile=/var/log/heating/heating-errors.log
stderr_logfile_maxbytes=1MB
stderr_logfile_backups=10
stderr_capture_maxbytes=1MB
```
