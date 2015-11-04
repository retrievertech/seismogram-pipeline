#!/bin/sh

# ssh and pull latest version of seismogram-pipeline
#
#   sh update_instance.sh <public_ip_address>
#
# requires that your ssh keys are properly set up on your computer
# and on the ec2 machines

ip=$1

# StrictHostKeyChecking=no means don't require confirmation
# -o UserKnownHostsFile=/dev/null means don't add $ip to the known_hosts file
ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
ubuntu@$ip "cd seismogram-pipeline && git pull"