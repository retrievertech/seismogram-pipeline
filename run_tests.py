import random
from subprocess import call

test_dir = "tests/"

f = open(test_dir+'filtered_files.txt', 'r')
lines = f.readlines()
num_files = len(lines)

num_to_process = 5
random_idxs = random.sample(range(num_files), num_to_process)

for (i, idx) in enumerate(random_idxs):
  print "\nimage %s of %s" % (i, num_to_process)
  filename = lines[idx].rstrip()
  local_path = test_dir+filename
  call(["aws s3 cp \"s3://WWSSN_Scans/"+filename+"\" ./"+local_path+" --region us-east-1"], shell=True)

  print "running test_meanlines_and_roi.sh"
  call(["bash test_meanlines_and_roi_s3.sh "+filename+" "+local_path], shell=True)

  print "deleting %s" % filename
  call(["rm "+local_path], shell=True)
