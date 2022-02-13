#!/usr/bin zsh

cd /home/$USER/Coding/public_repos/OpenCentralHeating/frontend-app/ || exit
yarn build
scp -r ./build mj@192.168.1.90:~/apps/heating/
