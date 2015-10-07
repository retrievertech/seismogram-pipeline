from subprocess import call

with open('selected_files.txt', 'r') as f:
  filenames = f.readlines()

print filenames

# for filename.rstrip() in filenames:
#   print "copying %s from s3" % filename
#   call(["aws s3 cp \"s3://WWSSN_Scans/"+filename+"\" ./"+filename+" --region us-east-1"], shell=True)

#   # print "running test_meanlines_and_roi.sh"
#   # call(["bash test_meanlines_and_roi_s3.sh", filename, filename], shell=True)

#   print "deleting %s" % filename
#   call(["rm "+filename], shell=True)
