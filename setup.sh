#!/bin/bash

${app_home:=$(pwd)}

# make a folder logs
mkdir $app_home"/logs"

$app_env=$app_home"/env"

# make a virtual env
if [ -e $app_env"/bin/activate" ]; then
        python3 -m virtualenv env
fi

source $app_env"/bin/activate"

# install libs
pip3 install -r requirements.txt

