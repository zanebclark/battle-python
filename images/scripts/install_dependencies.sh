#!/bin/bash
# -x -> Print all executed commands to the terminal
set -xe

# Disable prompts -> https://linuxhint.com/debian_frontend_noninteractive/
export DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies
# Dpkg::Options::="--force-confdef" -> Use default package config for new packages
# Dpkg::Options::="--force-confold" -> Use existing config for already installed packages (to not overwrite the existing config)
# dist-upgrade -> Upgrades and intelligently handles changing dependencies with new versions of packages
sudo apt --assume-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade
sudo apt-get update
# TODO: Think about this: sudo apt install unattended-upgrades
# TODO: Think about this: APT::Periodic::Update-Package-Lists "1";
# TODO: Think about this: APT::Periodic::Unattended-Upgrade "1";
# TODO: Think about this: APT::Periodic::AutocleanInterval "7";
# TODO: Think about this:  Unattended-Upgrade::Automatic-Reboot "true"; # change to true
# -qq -> No output except for errors
sudo apt-get -y -qq install python3-pip nginx git
# Setup Cloudwatch Agent
# https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/download-cloudwatch-agent-commandline.html
sudo wget https://amazoncloudwatch-agent.s3.amazonaws.com/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
