#!/bin/bash

app_name="apbot"
app_home=$(pwd)
app_env=$app_home/env


# make a folder logs
if [ ! -e "${app_env}/logs" ]; then
        mkdir $app_env/logs
fi

# make a virtual env
if [ ! -e "${app_env}/bin/activate" ]; then
        virtualenv env
fi

source $app_env/bin/activate

# install libs
pip3 install -r requirements.txt

ln -s $app_home/elk/logstash/pipeline/$app_name.conf /data/lucca/elk/logstash/pipeline/$app_name.conf
cat $app_home/elk/logstash/config/pipelines.yml >> /data/lucca/elk/logstash/config/pipelines.yml
