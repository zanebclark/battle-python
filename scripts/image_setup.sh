#!/bin/bash
# -x -> Print all executed commands to the terminal
set -x

# Disable prompts -> https://linuxhint.com/debian_frontend_noninteractive/
export DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies
sudo apt-get update
# Dpkg::Options::="--force-confdef" -> Use default package config for new packages
# Dpkg::Options::="--force-confold" -> Use existing config for already installed packages (to not overwrite the existing config)
# dist-upgrade -> Upgrades and intelligently handles changing dependencies with new versions of packages
sudo apt --assume-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade
sudo apt-get update
# -qq -> No output except for errors
sudo apt-get -y -qq install curl wget git vim apt-transport-https ca-certificates
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update -y
sudo apt install -y python3.12 python3-pip nginx
sudo systemctl enable nginx
sudo service nginx restart
sudo systemctl start nginx

# TODO: Check this out
python3.12 -m pip install git+https://github.com/zanebclark/battle_pythons_study_group.git@ec2
