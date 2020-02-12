import glob
import json
import time

files = glob.glob("*.txt")
for file in files:
	fid = open(file, "r")
	data = fid.read()
	obj = json.loads(data)
	
	# html5PlayerEvents (use this)
	st = obj["testStart"]
	et = obj["testEnd"]
	i = 0
	delay = 0
	end_duration = 0
	end_buffer_time = 0
	test_duration = et - st
	
	for r in obj["html5PlayerEvents"]:
		if r["event"] == "progress":
			d = r["details"]
			if i == 0:
				delay = r["timestamp"] - st
			if d.has_key("data[bufferedRange][end][0]"):
				end_buffer_time = d["data[bufferedRange][end][0]"]
			end_duration = d["playbackPosition"]
			i += 1
	
	print("{}\ttest_duration:{}\tdelay:{}\tduration:{}\tbuffer:{}".
			format(file, test_duration, delay, end_duration, end_buffer_time))
	

#print(json.dumps(obj["html5PlayerEvents"], indent=4)) # this is good?
#print(json.dumps(obj["otherPlayerEvents"], indent=4)) # playingSegments look useful for duration

#print(json.dumps(obj["resultDeletedTime"], indent=4)) # no use
#print(obj["bufferLevels"]) # no use

#print(json.dumps(obj["hlsJsEvents"], indent=4))
#print(json.dumps(obj["hlsFragmentLoadingEvents"], indent=4))
#print(json.dumps(obj["dashJsEvents"], indent=4))
#print(json.dumps(obj["dashFragmentLoadingEvents"], indent=4))



# resultInString
#print(obj["resultInString"])
#obj = json.load(data)
#print file.read()
#print data["testStart"]
