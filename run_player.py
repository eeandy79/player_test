import time
import json
import threading
from aws_helper import startTest
from aws_helper import listTest
from aws_helper import getResult
from aws_helper import deleteTest
from aws_helper import start_lem_test


#testDeviceUrl = "http://ec2-18-162-124-236.ap-east-1.compute.amazonaws.com:8080/playerTest"
def job2():
	testDeviceUrl = "http://18.163.187.8:8080/playerTest"
	browserType = "chrome"
	duration = 30
	playerType = "idlePage"
	
	
	response = start_lem_test(testDeviceUrl, browserType, duration, playerType)
	data = json.loads(response)
	jobId = data["jobId"]
	print("jobId: {}".format(jobId))
	
	i = 0
	while True:
		response = getResult(testDeviceUrl, jobId)
		data = json.loads(response)
		status = data["status"]
		if status == "SUCCESS":
			print(data["testResult"])
			#f = open(jobId+".txt", "a")
			#f.write(data["testResult"]["resultInString"])
			#f.close()
			break
		else:
			print("{}({}) : {}".format(jobId, i, status))
		time.sleep(10)
		i = i + 10
	
	
	response = deleteTest(testDeviceUrl, jobId)
	print(response)
	
	response = listTest(testDeviceUrl)
	print(response)


def job():
	testDeviceUrl = "http://18.162.111.9:8080/playerTest"
	streamUrl = "https://uat-ingest.hermeslive.com/origin/ingest/m3u8/master.m3u8"
	browserType = "chrome"
	duration = 30
	playerType = "tfiPlayer"
	
	
	response = startTest(testDeviceUrl, streamUrl, browserType, duration, playerType)
	data = json.loads(response)
	jobId = data["jobId"]
	print("jobId: {}".format(jobId))
	
	i = 0
	while True:
		response = getResult(testDeviceUrl, jobId)
		data = json.loads(response)
		status = data["status"]
		if status == "SUCCESS":
			f = open(jobId+".txt", "a")
			f.write(data["testResult"]["resultInString"])
			f.close()
			break
		else:
			print("{}({}) : {}".format(jobId, i, status))
		time.sleep(10)
		i = i + 10
	
	
	response = deleteTest(testDeviceUrl, jobId)
	print(response)
	
	response = listTest(testDeviceUrl)
	print(response)

num_threads = 1
threads = []
for i in range(num_threads):
	threads.append(threading.Thread(target = job2))
	#threads.append(threading.Thread(target = job, args = (i,)))
	threads[i].start()


for i in range(num_threads):
	threads[i].join()

print("Test Complete")


