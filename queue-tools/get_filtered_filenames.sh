#!/bin/sh

# These regexs don't work on my local OSX machine,
# but they work on the ec2 ubuntu machines.

# I haven't tested the latest version of this script,
# but I have tested the regexs.

aws s3 ls "s3://WWSSN_Scans" --region us-east-1 --profile seismo > ls_WWSSN_Scans.txt

regex1='s/.*\s.*\s\([0-9]\{4\}[7-9][0-9]_[0-9]\{4\}_[0-9]\{4\}_0[456]\.png\).*/\1/p'
# get all filenames of the form xxxx[# >= 70]_xxxx_xxxx_[04, 05, or 06].png
# i.e. only long-period seismos after 1970

regex2='/[0-9]\{6\}_[0-9]\{4\}_0009_0[456]\.png/d'
# delete all lines with station id 0009

sed -n $regex1 <ls_WWSSN_Scans.txt  >temp.txt
sed $regex2 <temp.txt  >filtered_files.txt
