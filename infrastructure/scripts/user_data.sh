#!/bin/bash
# -x -> Print all executed commands to the terminal
set -xe

/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
  -a fetch-config \
  -m ec2 \
  -s
systemctl enable amazon-cloudwatch-agent.service
