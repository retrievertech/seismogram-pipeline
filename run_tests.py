import random
from subprocess import call

f = open('filtered_files.txt', 'r')
lines = f.readlines()
num_files = len(lines)

num_to_process = 5
random_idxs = random.sample(range(num_files), num_to_process)

for idx in random_idxs:
  filename = lines[idx].rstrip()
  print "copying %s from s3" % filename
  call(["aws s3 cp \"s3://WWSSN_Scans/"+filename+"\" ./"+filename+" --region us-east-1"], shell=True)

  # print "running test_meanlines_and_roi.sh"
  # call(["bash test_meanlines_and_roi_s3.sh", filename, filename], shell=True)

  print "deleting %s" % filename
  call(["rm "+filename], shell=True)
