#!/bin/sh

dir=tests

mkdir -p $dir 

aws s3 ls "s3://WWSSN_Scans" --region us-east-1 > $dir/ls_WWSSN_Scans.txt

regex='s/.*\s.*\s\([0-9]\{4\}[7-9][0-9]_[0-9]\{4\}_[0-9]\{4\}_0[456]\.png\).*/\1/p'
# get all filenames of the form xxxx[# >= 70]_xxxx_xxxx_[04, 05, or 06].png
# i.e. only long-period seismos after 1970

sed -n $regex <$dir/ls_WWSSN_Scans.txt  >$dir/filtered_files.txt
