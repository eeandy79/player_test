import boto3
from aws_helper import search_instances

# Retrieves all regions/endpoints that work with EC2
ec2 = boto3.client('ec2')
regions = ec2.describe_regions()

for region in regions['Regions']:
	region_name = region['RegionName']
	key_name = 'andy_aws_test'
	if region_name != 'ap-east-1':
		continue
	print('region name: {}'.format(region_name))

	running = search_instances(region_name, key_name, 'running')
	terminated = search_instances(region_name, key_name, 'terminated')
	shutting_down = search_instances(region_name, key_name, 'shutting-down')
	pending = search_instances(region_name, key_name, 'pending')

	for instance in running:
		print('id:{} dns:{} state:{}'.format(instance[0], instance[1], instance[2]))
	print('\trunning: {}'.format(len(running)))
	print('\tterminated: {}'.format(len(terminated)))
	print('\tshutting-down: {}'.format(len(shutting_down)))
	print('\tpending: {}'.format(len(pending)))

	
# Retrieves availability zones only for region of the ec2 object
#response = ec2.describe_availability_zones()
#print('Availability Zones:', response['AvailabilityZones'])

