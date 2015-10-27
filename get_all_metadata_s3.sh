#!/bin/sh

# invokes the full pipeline on an image
#
#   sh get_all_metadata_s3.sh <image_name> <full_image_path> [dev]
#
# if the third argument is "dev", the data is copied locally.
# otherwise it's copied to the s3 metadata bucket.

# "xxxxxx_xxxx_xxxx_xx.png"
image_name=$1
# full path to the image
image_path=$2
# "dev" is development, everything else is production
type=$3
# create temporary directory to hold metadata
dir=`mktemp -d /tmp/seismo.XXXXX` && \
# save stats to metadata directory
stats_path="$dir/stats.json" && \
echo "writing to $dir" && \
sh set_seismo_status.sh $image_name 1 && \
python get_all_metadata.py --image "$image_path" --output "$dir" --stats "$stats_path" && \
sh copy_to_s3.sh $image_name $dir metadata $type && \
sh set_seismo_status.sh $image_name 3 && \
rm -rf $dir
