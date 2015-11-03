#!/bin/sh

# copies a directory to an s3 bucket
#
#  sh copy_to_s3.sh <image_name> <path_to_dir> <bucket_name> [dev]
#
# if the third argument is "dev", the directory is copied locally.
# otherwise it's copied to the s3 bucket.

# "xxxxxx_xxxx_xxxx_xx.png"
image_name=$1
# directory containing metadata
dir=$2
# bucket_name can be one of: metadata, edited-metadata, logs
bucket_name=$3
# "dev" indicates development mode
# production otherwise
type=$4

if [ "$type" != "dev" ]; then
  aws s3 cp --recursive $dir s3://wwssn-$bucket_name/$image_name --region us-east-1
else
  mkdir -p ../seismogram-app/client/$bucket_name/$image_name && \
  cp -r $dir/* ../seismogram-app/client/$bucket_name/$image_name
fi
