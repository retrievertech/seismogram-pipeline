#!/bin/bash
cd /home/ubuntu/seismogram-pipeline && \
sudo -H -u ubuntu bash -c 'git pull' && \
sudo -H -u ubuntu bash -c 'node ./queue-worker/process_queue.js'

# output of this script is written to:
# /var/log/cloud-init-output.log