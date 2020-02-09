from aws_helper import listTest
from aws_helper import deleteTest
from aws_helper import describe_region_instances
import json

cluster = ['ap-east-1', 'ap-southeast-1']
ips = []
for region in cluster:
	response = describe_region_instances(region)
	for entry in response:
		if entry['key'] == 'andy_aws_test' and entry['state'] == 'running':
			ips.append(entry['ip'])


for ip in ips:
	testDeviceUrl = "http://" + ip+ ":8080/playerTest"
	
	response = listTest(testDeviceUrl)
	data = json.loads(response)
	i = 0
	for status in data:
		print("({})jobid: {} {} duration: {}".format(i, status["jobId"], status["status"], status["config"]["duration"])) 
		i = i + 1
		deleteTest(testDeviceUrl, status["jobId"])
