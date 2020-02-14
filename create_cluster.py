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
from aws_helper import search_instances
from aws_helper import terminate_instances

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
			DryRun=False,
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
	region_1 = ['ap-east-1'] # Hong Kong only
	#region_2 = ['ap-northeast-1'] # Tokyo only
	region_asia_all  = ['ap-east-1', 'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2']
        region_asia_good =  ['ap-east-1', 'ap-northeast-1', 'ap-northeast-2']
	region_us_good = ['us-east-1', 'us-west-1']

        ### setup the cluster
	cluster = region_asia_all
	region_ami = {key: None for key in cluster}

	### linux ami images
	## asia pacific
	region_ami['ap-east-1']      = 'ami-028e04e09aeb8c76f' # Hong Kong
	region_ami['ap-southeast-1'] = 'ami-0f3da50a41b5f55c6' # Singapore
	region_ami['ap-southeast-2'] = 'ami-0ff78b6d10c21d29b' # Sydney
	region_ami['ap-northeast-1'] = 'ami-0bc6b28b070149a91' # Tokyo
	region_ami['ap-northeast-2'] = 'ami-04c7d8293cca08276' # Seoiul
	## US
	region_ami['us-east-1']      = 'ami-05c466aa5338c20bf' # Virginia
	region_ami['us-east-2']      = 'ami-0066c1931d059dda3' # Ohio
	region_ami['us-west-1']      = 'ami-00245f8fd00bb8ce4' # California
	region_ami['us-west-2']      = 'ami-0ef88643acacc9ed4' # Oregon


	# Assign these values before running the program
	#instance_type = 'c5.9xlarge'
	#instance_type = 't3.micro'
	instance_type = 'c5.4xlarge' # this is our target
	keypair_name = 'andy_aws_test'
	count = 5 # max number for spot is 25


        # target cluster -> number of nodes
        regions = []
        regions.append(('ap-east-1',      0))
        regions.append(('ap-southeast-1', 0))
        regions.append(('ap-southeast-2', 0))
        regions.append(('ap-northeast-1', 0))
        regions.append(('ap-northeast-2', 0))

        for region in regions:
            region_name = region[0]
            instances = search_instances(region_name, keypair_name, "running")
            to_create = region[1] - len(instances)
            if to_create > 0:
                print("instance to create on {} : {}".format(region_name, to_create))
                image_id = region_ami[region_name]
		response = create_spot_instances(region_name, image_id, instance_type, keypair_name, to_create)
            elif to_create < 0:
                to_delete = -to_create
                print("instance to delete on {} : {}".format(region_name, to_delete))
                instance_to_delete = []
                for idx in range(to_delete):
                    instance_to_delete.append(instances[idx][0])
                response = terminate_instances(region_name, instance_to_delete)
            else:
                print("instance on {}: {} match target {}".format(region_name, len(instances), region[1]))




	#response = []
	#for region_name in cluster:
	#	image_id = region_ami[region_name]
	#	response = create_spot_instances(region_name, image_id, instance_type, keypair_name, count)
	#	#response = create_ondemand_instances(region_name, image_id, instance_type, keypair_name, count)


if __name__ == '__main__':
    main()
