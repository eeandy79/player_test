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
from flask import jsonify

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
	
	print("{} finish provision player. sleep for {}".format(baseurl, duration))
	time.sleep(duration)
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
		time.sleep(10)
		i = i + 10
	
	response = listTest(testDeviceUrl)
	print(response)


def job(baseurl, num_player, eventurl, duration):

	testDeviceUrl = "http://" + baseurl + ":8080/playerTest"
	browserType = "chrome"
	playerType = "tfiPlayer"
	
	jobIds = []
	for i in range(0, num_player):
		response = startTest(testDeviceUrl, eventurl, browserType, duration, playerType)
		data = json.loads(response)
		jobId = data["jobId"]
		jobIds.append(jobId)
	
	sleep_duration = duration * 1.1
	print("{} finish provision player. sleep for {}".format(baseurl, sleep_duration))
	time.sleep(sleep_duration)
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
				#print(response)
				success_cnt += 1
				f = open(jobId+".txt", "a")
				f.write(json.dumps(data["testResult"], indent=4))
				f.close()
				deleteTest(testDeviceUrl, jobId)
			elif status == "FAIL":
				fail_cnt += 1
				deleteTest(testDeviceUrl, jobId)
			else:
				_jobIds.append(jobId)

		if len(_jobIds) == 0:
			print("[Done({})][{}] success:{} fail:{}".format(i, baseurl, success_cnt, fail_cnt))
			break;
		else:
			print("[Testing({})][{}] success:{} fail:{}".format(i, baseurl, success_cnt, fail_cnt))
		jobIds = _jobIds
		time.sleep(5)
		i = i + 5 
	
	response = listTest(testDeviceUrl)
	print(response)

### Test environment variable ###
region_asia = ['ap-east-1', 'ap-northeast-1', 'ap-northeast-2']
region_us = ['us-east-1', 'us-west-1']
#cluster = ['ap-east-1']       # Hong Kong
#cluster = ['ap-northeast-1']  # Tokyo
#cluster = ['ap-northeast-2']  # Seoul
#cluster = ['ap-southeast-1']  # Singapore # !!!!! not good !!!!!
#cluster = ['ap-southeast-2']  # Sydney    # !!!!! failure !!!!!
#cluster = ['us-east-1']       # Virginia
#cluster = ['us-east-2']       # Ohio
#cluster = ['us-west-1']       # California
#cluster = ['us_west-2']       # Oregon    # !!!!! invalid endpoint !!!!! 

cluster = region_asia + region_us

num_player_per_node = 32 #38 # number of player per node
duration = 60 # test duration
#eventurl = "https://event.hermeslive.com/event/7e3a0157-13ee-406a-9a2d-0e0b0a7b8330"
#eventurl = "http://rthkcnews-lh.akamaihd.net/i/rthknews_1@312607/master.m3u8"
eventurl = "http://rthklive3-lh.akamaihd.net/i/rthk31_1@143247/index_2028000_av-p.m3u8"

use_jw = False
if use_jw:
	eventurl = eventurl + "?player=jw"

ips = []
filter = [
	{'Name':'key-name','Values':['andy_aws_test']},
	{'Name':'instance-state-name','Values':['running']}
]
for region in cluster:
	response = describe_region_instances(region, filter)
	for entry in response:
		ips.append(entry['ip'])

print(ips)

for i in range(5):
	### start player test ###
	threads = []
	for ip in ips:
		#threads.append(threading.Thread(target = job))
		thread = threading.Thread(
				target = job, 
		#		target = test_lem_routine, 
				args = (ip, num_player_per_node, eventurl, duration))
		#thread = threading.Thread(
		#		args = (ip, num_player_per_node, eventurl, duration))
		threads.append(thread)
		thread.start()
	
	for i in range(len(threads)):
		threads[i].join()

print("Test Complete")


