#!/bin/sh

# download an image, invoke pipeline, copy
# results to s3, and clean up
#
#   sh process_task.sh <image_name>
#
# this script will only work on an EC2 machine

# "xxxxxx_xxxx_xxxx_xx.png"
image_name=$1
# temporary directory to put image
dir=`mktemp -d /tmp/seismo.XXXXX` && \
# full path to the image
image_path="$dir/$image_name"

echo "downloading $image_name to $image_path" && \
aws s3 cp s3://WWSSN_Scans/$image_name --region us-east-1 "$image_path" && \
echo "invoking pipeline" && \
sh get_all_metadata_s3.sh $image_name "$image_path"
echo "cleaning up" && \
rm -rf $dir