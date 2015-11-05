'''
List all active us-west-2 instances, and git pull in their seismogram-pipeline repos.

'''

import boto3
import subprocess

ec2 = boto3.resource('ec2', region_name='us-west-2')

instances = ec2.instances.filter()
for instance in instances:
  print(instance.id, instance.instance_type, instance.public_ip_address)
  subprocess.call("sh update_instance.sh "+instance.public_ip_address, shell=True)