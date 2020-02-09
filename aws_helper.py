import boto3
import requests
import json

def search_instances(target_region_name, target_key_name, target_state_name):
	session = boto3.session.Session(region_name=target_region_name)
	session_client = session.client('ec2')
	instances = session_client.describe_instances()
	rv = []
	for reservation in instances['Reservations']:
		for instance_description in reservation['Instances']:
			instance_id = instance_description['InstanceId']
			state = instance_description['State']['Name']
			key = instance_description['KeyName']
			dns = instance_description['PublicDnsName']
			if key == target_key_name and state == target_state_name:
				rv.append((instance_id, dns, state))
	return rv

def count_instances_by_state(instances_info):
	result = {key: 0 for key in ['running','stopped','terminated']}
	for instance in instances_info:
		if instance['state'] == 'running':
			result['running'] += 1
		elif instance['state'] == 'stopped':
			result['stopped'] += 1
		elif instance['state'] == 'stopped':
			result['terminated'] += 1
	return result

def terminate_instances(target_region_name, instance_ids):
	session = boto3.session.Session(region_name=target_region_name)
	ec2 = session.client('ec2')
	try:
		states = ec2.terminate_instances(InstanceIds=instance_ids)
	except ClientError as e:
		logging.error(e)
		return None
	return states['TerminatingInstances']

def get_city_from_region(region_name):
	if region_name == 'ap-east-1':
		return 'Hong Kong'
	elif region_name == 'ap-northeast-1':
		return 'Tokyo'
	elif region_name == 'ap-northeast-2':
		return 'Seoul'
	elif region_name == 'ap-southeast-1':
		return 'Singapore'
	elif region_name == 'ap-southeast-2':
		return 'Sydney'
	elif region_name == 'ap-south-1':
		return 'Mumbai'
	else:
		return 'Unknown'

def describe_region_instances(target_region_name, filter=[]):
	session = boto3.session.Session(region_name=target_region_name)
	ec2 = session.client('ec2')
	response = ec2.describe_instances(Filters=filter)
	#print(response['Reservations'])
	instances_info = []
	for reservation in response['Reservations']:
		for instance_description in reservation['Instances']:
			instance_id = instance_description['InstanceId']
			state = instance_description['State']['Name']
			key = instance_description['KeyName']
			ip = 'null'
			if 'PublicIpAddress' in instance_description.keys():
				ip = instance_description['PublicIpAddress']
			instances_info.append(dict(instance_id=instance_id, state=state, key=key, ip=ip))
			#print("instance: {} {} {}".format(instance_id, state, key))
	return instances_info

def startTest(testDeviceUrl, streamUrl, browserType, duration, playerType, lowLatencyMode = None, targetLatency = None):
	headers = {'Content-Type' : 'application/json'}
	testConfig = { "streamUrl": streamUrl,\
		"browserType": browserType,\
			"duration": duration,\
			"playerType": playerType,\
			"playerOptions": {}}

	if lowLatencyMode is not None:
		testConfig["playerOptions"]["lowLatencyMode"] = lowLatencyMode

	if targetLatency is not None:
		testConfig["playerOptions"]["targetLatency"] = targetLatency

	payload = json.dumps(testConfig)
	#print("testConfig: \n" + payload)

	r = requests.post(testDeviceUrl, payload, headers=headers)

	#print(r.content)
	return r.content

def start_lem_test(testDeviceUrl, browserType, duration, playerType, eventurl):
	headers = {'Content-Type' : 'application/json'}
	testConfig = { "streamUrl": "",\
		"browserType": browserType,\
			"duration": duration,\
			"playerType": playerType,\
			"playerOptions": { "siteUrl": eventurl }}

	payload = json.dumps(testConfig)
	#print("testConfig: \n" + payload)

	r = requests.post(testDeviceUrl, payload, headers=headers)

	#print(r.content)
	return r.content



def listTest(testDeviceUrl):
	r = requests.get(testDeviceUrl)
	#print(r.content)
	return r.content

def getResult(testDeviceUrl, jobId):
	r = requests.get(testDeviceUrl + "/" + jobId)
	#print(r.content)
	return r.content

def deleteTest(testDeviceUrl, jobId):
	r = requests.delete(testDeviceUrl + "/" + jobId)
	#print(r.content)
	return r.content


