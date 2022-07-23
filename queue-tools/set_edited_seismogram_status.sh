#!/bin/sh

# for each filename in a list, set its status to "edited"
#
#   sh set_edited_seismogram_status.sh < edited_files.txt
#
# where edited_files.txt is a list of filenames that ought to have
# status "edited". You can generate edited_files.txt by running
#
#   aws s3 ls s3://wwssn-edited-metadata --profile seismo > edited_files.txt
#
# and then editing the resulting file so that each line is
# exactly one filename:
#
#   010378_1730_0053_04.png
#   010577_1805_0028_04.png
#   011077_0010_0064_04.png
#   011669_1206_0009_04.png
#   ...

while read line
do
  sh ../set_seismo_status.sh $line 4
done <&0