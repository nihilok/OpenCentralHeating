### Open Central Heating API
How to install on Ubuntu Server
#### Prerequisites
- Python3.7+
- Git

if you don't have pip3 and/or venv installed run:
```sh
sudo apt install python3-pip -y
sudo apt install python3-venv -y
```
(The installation script will create a Virtual Environment)

#### Installation
```bash
git clone https://github.com/nihilok/OpenCentralHeating.git
cd OpenCentralHeating
sudo python3 install.py
```
You will be prompted to create a Super User who can then create new users via the api.
You will also be prompted for other information:
- the URL/IP of the temperature sensor (microcontroller) (leave blank for test mode)
- the IP of the Raspberry Pi (leave blank if installing on the Pi)

If you are running the script for a second time, the setup information you provide here will overwrite the previous inputs. 
The rest of the installation script should be idempotent, unless stopped halfway through the first time, in which case you should remove the `env` directory from the repository directory, and run the script again.

You can start the server from any directory with the command `open-heating` and you can interact with the API via the swagger interface at http://localhost:8080/docs

If you want to run the server continuously and serve over a network or the internet, I suggest using `nginx` (`sudo apt install nginx`) and creating a server block that acts a proxy to http://localhost:8080, and then using `supervisor` (`sudo apt install supervisor`) to run the API in the background (on the same port).