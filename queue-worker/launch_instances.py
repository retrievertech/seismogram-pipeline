import boto3
ec2 = boto3.resource('ec2')

# id for the machine image that has all of
# our dependencies installed
ami_image_id = 'ami-dfa1eeba'

# id for the security group that permits ssh access
# from all IP addresses
security_group_ids = ['sg-1b34cb7d']

instance_type = 'r3.large'

# the user_data script is run once when a new machine boots
with open("user_data.sh", "r") as myfile:
  user_data = myfile.read()

print "Creating instances..."
new_instance_ids = ec2.create_instances(ImageId=ami_image_id,
                     MinCount=1, MaxCount=1,
                     SecurityGroupIds=security_group_ids,
                     InstanceType=instance_type,
                     UserData=user_data)

print "created instances: %s" % new_instance_ids