#!/bin/sh

# set the processing status of a seismogram
# (hit the server endpoint, which updates the database)
#
#   sh set_seismo_status.sh <image_name> <status>
#

# node server
server=http://seismo.redfish.com:3000
user=seismo
pass=Redfish32

# "xxxxxx_xxxx_xxxx_xx.png"
image_name=$1

# <status> can be one of:
#  0: notStarted
#  1: processing  # deprecated; don't use this
#  2: failed
#  3: complete
#  4: edited
status=$2

wget --user $user --password $pass $server/processing/setstatus/$image_name/$status -O /dev/null
