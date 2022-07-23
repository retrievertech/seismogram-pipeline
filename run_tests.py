from subprocess import call

test_dir = "tests/"

with open(test_dir+'selected_files.txt', 'r') as f:
  filenames = f.readlines()

print filenames
num_to_process = len(filenames)

for (i, filename) in enumerate(filenames):
  filename = filename.rstrip()
  print "\nimage %s of %s" % (i, num_to_process)
  local_path = test_dir+filename
  call(["aws s3 cp \"s3://WWSSN_Scans/"+filename+"\" ./"+local_path+" --region us-east-1 --profile seismo"], shell=True)

  print "running test_meanlines_and_roi.sh"
  call(["bash test_meanlines_and_roi_s3.sh "+filename+" "+local_path], shell=True)

  print "deleting %s" % filename
  call(["rm "+local_path], shell=True)
