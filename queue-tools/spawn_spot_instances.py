"""
Description:
  Create spot requests for EC2 machines that will immediately begin
  processing the seismogram queue.

Usage:
  spawn_spot_instances.py --region <region_name> --type <instance_type> --num <num_instances>
  spawn_spot_instances.py -h | --help

Options:
  --region <region_name>  Name of the region in which to launch instances. E.g. 'us-east-1' or 'us-west-2'.
  --type <instance_type>  Type of instance to launch. E.g. 'r3.xlarge' or 'r3.2xlarge'.
  --num <num_instances>   Number of instances to launch.
  -h --help               Show this screen.

"""

from docopt import docopt
import boto3
import base64
import sys

def launch_instances(region_name, instance_type, num_instances):
  ec2 = boto3.client('ec2', region_name=region_name)

  # id for the machine image that has all of
  # our dependencies installed
  ami_image_id = {
    'us-east-1': 'ami-0027566a',
    'us-west-2': 'ami-2d17004c'
  }

  if (not region_name in ami_image_id):
    print "Missing an ami image id for region %s." % region_name
    print '''Log into the AWS console, create a new image in the
    desired region, and add it to spawn_spot_instances.py'''
    sys.exit(1)

  # id for the security group that permits ssh access
  # from all IP addresses
  security_group_ids = {
   'us-east-1': ['sg-1b34cb7d'],
   'us-west-2': ['sg-c9601aad']
  }

  if (not region_name in security_group_ids):
    print "Missing a security group id for region %s." % region_name
    print '''Log into the AWS console, create a new security group
    with ssh permissions, and add it to spawn_spot_instances.py'''
    sys.exit(1)

  # the user_data script is run once when a new machine boots
  with open("user_data.sh", "r") as myfile:
    user_data = myfile.read()
  
  base64_user_data = base64.b64encode(user_data)

  print "Creating spot requests..."
  requests = ec2.request_spot_instances(
    SpotPrice='0.2',
    InstanceCount=num_instances,
    Type='persistent',
    LaunchSpecification={
      'ImageId': ami_image_id[region_name],
      'UserData': base64_user_data,
      'InstanceType': instance_type,
      'SecurityGroupIds': security_group_ids[region_name]
    }
  )

  print "created spot requests: %s" % requests

if __name__ == '__main__':
  arguments = docopt(__doc__)
  region_name = arguments["--region"]
  instance_type = arguments["--type"]
  num_instances = int(arguments["--num"])
  
  if (num_instances >= 1 and instance_type and region_name):
    launch_instances(region_name, instance_type, num_instances)
  else:
    print(arguments)
