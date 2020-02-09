# snippet-comment:[These are tags for the AWS doc team's sample catalog. Do not remove.]
# snippet-sourcedescription:[create_instance.py demonstrates how to create an Amazon EC2 instance.]
# snippet-service:[ec2]
# snippet-keyword:[Amazon Elastic Compute Cloud (Amazon EC2)]
# snippet-keyword:[Python]
# snippet-sourcesyntax:[python]
# snippet-sourcesyntax:[python]
# snippet-keyword:[Code Sample]
# snippet-sourcetype:[full-example]
# snippet-sourcedate:[2019-2-18]
# snippet-sourceauthor:[AWS]

# Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# This file is licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License. A copy of the
# License is located at
#
# http://aws.amazon.com/apache2.0/
#
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License. 

import logging
import boto3
import json
from botocore.exceptions import ClientError

def create_spot_instances(target_region_name, image_id, instance_type, keypair_name, count):
	# Provision and launch the EC2 instance
	session = boto3.session.Session(region_name=target_region_name)
	ec2_client = session.client('ec2')
	try:
		response = ec2_client.request_spot_instances(
			InstanceCount=count,
			DryRun=False,
			LaunchSpecification = {
				'ImageId':image_id,
				'KeyName':keypair_name,
				'InstanceType':instance_type,
				'SecurityGroupIds':['launch-wizard-4']
			})
		for request in response['SpotInstanceRequests']:
			#print(request['InstanceId'])
			print(request['SpotInstanceRequestId'])
			print(request['Status'])
		#print(response)

	except ClientError as e:
		print("create spot instances failed")
		logging.error(e)
		return None

	return response


def create_ondemand_instances(target_region_name, image_id, instance_type, keypair_name, count):
	# Provision and launch the EC2 instance
	session = boto3.session.Session(region_name=target_region_name)
	ec2_client = session.client('ec2')
	try:
		response = ec2_client.run_instances(
			ImageId=image_id,
			DryRun=True,
			InstanceType=instance_type,
			KeyName=keypair_name,
			MinCount=1,
			MaxCount=count,
			SecurityGroups=['launch-wizard-4'])

	except ClientError as e:
		print("create on demand instances failed")
		logging.error(e)
		return None

	return response['Instances']

def main():
	cluster = ['ap-east-1', 'ap-southeast-1']
	#cluster = ['ap-east-1', 'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2']
	# windows ami images
	region_ami = {key: None for key in cluster}
	region_ami['ap-east-1']      = 'ami-02b1f4abe6593f257'
	region_ami['ap-southeast-1'] = 'ami-0d35d9390e32df1fe'
	region_ami['ap-southeast-2'] = 'ami-0171c66d7328d7bd1'
	region_ami['ap-northeast-1'] = 'ami-0bd626e7618a6ad7a'
	region_ami['ap-northeast-2'] = 'ami-02f77f39b50aeb96c'

	# Assign these values before running the program
	#instance_type = 'c5.9xlarge'
	#instance_type = 't3.micro'
	instance_type = 'c5.4xlarge' # this is our target
	keypair_name = 'andy_aws_test'
	count = 1 # max number for spot is 25

	response = []
	for region_name in cluster:
		image_id = region_ami[region_name];
		response = create_spot_instances(region_name, image_id, instance_type, keypair_name, count)


if __name__ == '__main__':
    main()
