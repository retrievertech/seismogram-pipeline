"""
Description:
  Launch EC2 r3.xlarge (30.5GB RAM) machines that will immediately begin
  processing the seismogram queue.

Usage:
  launch_instances.py --num <num_instances>
  launch_instances.py -h | --help

Options:
  -h --help              Show this screen.
  --num <num_instances>  Number of instances to launch.

"""

from docopt import docopt
import boto3

def launch_instances(num_instances):
  ec2 = boto3.resource('ec2')

  # id for the machine image that has all of
  # our dependencies installed
  ami_image_id = 'ami-0027566a'

  # id for the security group that permits ssh access
  # from all IP addresses
  security_group_ids = ['sg-1b34cb7d']

  instance_type = 'r3.xlarge'

  # the user_data script is run once when a new machine boots
  with open("user_data.sh", "r") as myfile:
    user_data = myfile.read()
    
  print "Creating instances..."
  new_instance_ids = ec2.create_instances(ImageId=ami_image_id,
                       MinCount=num_instances, MaxCount=num_instances,
                       SecurityGroupIds=security_group_ids,
                       InstanceType=instance_type,
                       UserData=user_data)

  print "created instances: %s" % new_instance_ids

if __name__ == '__main__':
  arguments = docopt(__doc__)
  num_instances = int(arguments["--num"])
  
  if (num_instances >= 1):
    launch_instances(num_instances)
  else:
    print(arguments)
