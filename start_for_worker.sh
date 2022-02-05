#!/bin/bash

app_name="apbot"
app_home="/data/lucca/apps/apbot"
app_env="~/envs/apbot"
PATH="/data/lucca/apps/apbot/mongodb-linux-x86_64-enterprise-ubuntu2004-4.4.12/bin:"${PATH}
source ~/.bashrc

# make a folder logs
if [ ! -e "${app_home}/logs" ]; then
  mkdir $app_home/logs
fi

# make a virtual env
if [ ! -e "${app_env}/bin/activate" ]; then
  mkdir ${app_env} && cd ${app_env}
  virtualenv env
  source $app_env/bin/activate
  # install libs
  pip3 install -r requirements.txt
fi

source $app_env/bin/activate
sleep 2
$app_env/bin/python $app_home/main.py --app_home $app_home