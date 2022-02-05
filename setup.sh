#!/bin/bash
apt-get -qq update
apt-get -y -qq install git gcc wget
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y -qq ./google-chrome-stable_current_amd64.deb