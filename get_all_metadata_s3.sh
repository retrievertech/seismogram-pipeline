#!/bin/sh

# invokes the full pipeline on an image
#
#   sh get_all_metadata_s3.sh <image_name> <full_image_path> [dev]
#
# if the third argument is "dev", the data is copied locally.
# otherwise it's copied to the s3 metadata bucket.

# node server
server=http://localhost:3000
# "xxxxxx_xxxx_xxxx_xx.png"
image_name=$1
# full path to the image
image_path=$2
# "dev" is development, everything else is production
type=$3

dir=`mktemp -d /tmp/seismo.XXXXX` && \
echo "writing to $dir" && \
wget $server/processing/setstatus/$image_name/1 -O /dev/null && \
python get_all_metadata.py --image "$image_path" --output "$dir" && \
sh copy_to_s3.sh $image_name $dir normal $type && \
wget $server/processing/setstatus/$image_name/3 -O /dev/null && \
rm -rf $dir
