import time
import json
import threading
import boto3
from aws_helper import startTest
from aws_helper import listTest
from aws_helper import getResult
from aws_helper import deleteTest
from create_instances import create_spot_instances
from aws_helper import start_lem_test
from aws_helper import describe_region_instances

def test_lem_routine(baseurl, num_player, eventurl, duration):

	testDeviceUrl = "http://" + baseurl + ":8080/playerTest"
	browserType = "chrome"
	playerType = "idlePage"
	
	jobIds = []
	for i in range(0, num_player):
		response = start_lem_test(testDeviceUrl, browserType, duration, playerType, eventurl)
		data = json.loads(response)
		jobId = data["jobId"]
		jobIds.append(jobId)
		#print("jobId: {} {}".format(jobId, response))
	
	print("{} finish provision player".format(baseurl))
	time.sleep(30)
	i = 0
	success_cnt = 0
	fail_cnt = 0
	while True:
		_jobIds = []
		for jobId in jobIds:
			response = getResult(testDeviceUrl, jobId)
			data = json.loads(response)
			status = data["status"]
			if status == "SUCCESS":
				success_cnt += 1
				deleteTest(testDeviceUrl, jobId)
			elif status == "FAIL":
				fail_cnt += 1
				deleteTest(testDeviceUrl, jobId)
			else:
				_jobIds.append(jobId)

		if len(_jobIds) == 0:
			print("[Done({})][{}] success:{} fail:{}".format(i, baseurl, success_cnt, fail_cnt))
			break
		else:
			print("[Testing({})][{}] success:{} fail:{}".format(i, baseurl, success_cnt, fail_cnt))

		jobIds = _jobIds
		time.sleep(30)
		i = i + 30
	
	response = listTest(testDeviceUrl)
	print(response)


def job(baseurl, num_player):

	testDeviceUrl = "http://" + baseurl + ":8080/playerTest"
	streamUrl = "https://uat-ingest.hermeslive.com/origin/ingest/m3u8/master.m3u8"
	browserType = "chrome"
	duration = 240
	playerType = "tfiPlayer"
	
	jobIds = []
	for i in range(0, num_player):
		response = startTest(testDeviceUrl, streamUrl, browserType, duration, playerType)
		data = json.loads(response)
		jobId = data["jobId"]
		jobIds.append(jobId)
		print("jobId: {}".format(jobId))
	
	i = 0
	while True:
		_jobIds = []
		for jobId in jobIds:
			response = getResult(testDeviceUrl, jobId)
			data = json.loads(response)
			status = data["status"]
			if status == "SUCCESS":
				f = open(jobId+".txt", "a")
				f.write(data["testResult"]["resultInString"])
				f.close()
				deleteTest(testDeviceUrl, jobId)
			else:
				print("[{}]\t{}({}) : {}".format(baseurl, jobId, i, status))
				_jobIds.append(jobId)

		if len(_jobIds) == 0:
			break;
		jobIds = _jobIds
		time.sleep(10)
		i = i + 10
	
	response = listTest(testDeviceUrl)
	print(response)

### Test environment variable ###
cluster = ['ap-east-1', 'ap-southeast-1']
num_player_per_node = 32 #38 # number of player per node
duration = 60 # test duration
eventurl = "https://event.hermeslive.com/event/7e3a0157-13ee-406a-9a2d-0e0b0a7b8330"

use_jw = False
if use_jw:
	eventurl = eventurl + "?player=jw"

ips = []
for region in cluster:
	response = describe_region_instances(region)
	for entry in response:
		if entry['key'] == 'andy_aws_test' and entry['state'] == 'running':
			ips.append(entry['ip'])

print(ips)

### start player test ###
threads = []
for ip in ips:
	#threads.append(threading.Thread(target = job))
	thread = threading.Thread(
			target = test_lem_routine, 
			args = (ip, num_player_per_node, eventurl, duration))
	threads.append(thread)
	thread.start()

for i in range(len(threads)):
	threads[i].join()

print("Test Complete")


