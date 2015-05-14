#!/bin/sh

server=http://localhost:3000

dir=`mktemp -d /tmp/seismo.XXXXX` && \
echo "writing to $dir" && \
wget $server/processing/setstatus/$1/1 && \
python get_all_metadata.py --image $2 --output $dir && \
if [ "$3" != "dev" ]; then
  aws s3 cp --recursive $dir s3://wwssn-metadata/$1
else
  cp -r $dir ../seismogram-app/client/metadata/$1
fi && \
rm -rf $dir && \
wget $server/processing/setstatus/$1/3 #complete
