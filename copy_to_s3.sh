#!/bin/sh

# copies a directory to the s3 metadata bucket
#
#  sh copy_to_s3.sh <image_name> <path_to_metadata_dir> <edited> [dev]
#
# if the third argument is "dev", the metadata is copied locally.
# otherwise it's copied to the s3 bucket.

# "xxxxxx_xxxx_xxxx_xx.png"
image_name=$1
# directory containing metadata
dir=$2
# a value of "edited" means to copy to the edited-metadata bucket
# otherwise to the normal metadata bucket
edited=$3
# "dev" indicates development mode
# production otherwise
type=$4

bucket_name=metadata

if [ "$edited" == "edited" ]; then
  bucket_name=edited-metadata
fi

if [ "$type" != "dev" ]; then
  aws s3 cp --recursive $dir s3://wwssn-$bucket_name/$image_name
else
  mkdir -p ../seismogram-app/client/$bucket_name/$image_name && \
  cp -r $dir/* ../seismogram-app/client/$bucket_name/$image_name
fi
