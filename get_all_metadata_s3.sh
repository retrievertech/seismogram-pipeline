#!/bin/sh

dir=`mktemp -d` && \
echo "writing to $dir" && \
python get_all_metadata.py --image $2 --output $dir && \
aws s3 cp --recursive $dir s3://wwssn-metadata/$1 && \
rm -rf $dir
