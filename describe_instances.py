import boto3
from aws_helper import describe_region_instances

response = describe_region_instances('ap-east-1')
for entry in response:
	print("instance: {} {} {}".format(entry['instance_id'], entry['state'], entry['key']))

