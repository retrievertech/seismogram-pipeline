#!/bin/bash
cd /home/ubuntu/seismogram-pipeline && \
git pull && \
node ./queue-worker/process_queue.js