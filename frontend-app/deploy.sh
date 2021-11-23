#!/usr/bin zsh

cd /home/$USER/Coding/public_repos/SmartHomeApp/front-end-v2/ || exit;
yarn build ;
scp -r ./build mj@192.168.1.90:~/apps/heating/ ;
