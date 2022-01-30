#!/bin/bash

app_name="apbot"
app_home="/data/lucca/apps/apbot"
app_env=$app_home/env

source $app_env/bin/activate
sleep 2
$app_env/bin/python $app_home/main.py
# python $app_home/main.py
