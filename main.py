from flask import Flask, render_template, request
from flask_table import Table, Col
import boto3
import json
from aws_helper import search_instances
from aws_helper import describe_region_instances
from aws_helper import count_instances_by_state
from aws_helper import terminate_instances
from aws_helper import get_city_from_region


app = Flask(__name__)

class ItemTable(Table):
	classes = ['table table-sm table-striped table-condensed w-75 mx-auto']
	name = Col('Name')
	description = Col('Description')

class RegionTable(Table):
	classes = ['table table-sm table-striped table-condensed w-75 mx-auto']
	name = Col('Name')
	city = Col('City')
	endpoint = Col('Endpoint')
	running = Col('Running instance')

class InstanceTable(Table):
	classes = ['table table-sm table-striped table-condensed w-75 mx-auto']
	name = Col('Name')
	endpoint = Col('Endpoint')
	description = Col('Description')

@app.route("/")
def home():
	return render_template("home.html")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route('/', methods=['POST'])
def my_form_post():
	### system variables ###
	region_asia = ['ap-east-1', 'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2']
	region_us = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']
	cluster = region_asia + region_us

	if 'list_region_names' in request.form:
		ec2 = boto3.client('ec2')
		regions = ec2.describe_regions(RegionNames=cluster)
		items = []
		filter = [{'Name':'key-name','Values':['andy_aws_test']}]
		for region in regions['Regions']:
			region_name = region['RegionName']
			desc = describe_region_instances(region_name, filter)
			cnts = count_instances_by_state(desc)
			instance_state_cnt = "Running:{} Stopped:{} Terminated: {}".format(
					cnts['running'], cnts['stopped'], cnts['terminated'])
		
			items.append(dict(
						name=region_name, 
						city=get_city_from_region(region_name), 
						endpoint=region['Endpoint'],
						running=cnts['running']))

		table = RegionTable(items)
		table.border = True
		return render_template("home.html", table=table)

	elif 'list_region_raws' in request.form:
		ec2 = boto3.client('ec2')
		regions = ec2.describe_regions()
		items = []
		for region in regions['Regions']:
			items.append(dict(name=region['RegionName'], description=region))
		table = ItemTable(items)
		table.border = True
		return render_template("home.html", table=table)

	elif 'list_instances' in request.form:
		items = []
		filter = [
			{'Name':'key-name','Values':['andy_aws_test']},
			{'Name':'instance-state-name','Values':['running']}
			]
		for region in cluster:
			response = describe_region_instances(region, filter)
			for entry in response:
				if entry['key'] == 'andy_aws_test' and entry['state'] == 'running':
					desc = entry['state'] + " " + entry['key']
					items.append(dict(name=entry['instance_id'], endpoint=entry['ip'],description=desc))
		table = InstanceTable(items)
		table.border = True
		return render_template("home.html", table=table)

	elif 'terminate_instances' in request.form:
		items = []
		for region in cluster:
			key_name = 'andy_aws_test'
			state = 'running'
			instance_ids = []
			instances = search_instances(region, key_name, state)

			for instance in instances:
				instance_ids.append(instance[0])
				
			if len(instance_ids) != 0:
				states = terminate_instances(region, instance_ids)
				items.append(dict(name='status', description=states))

		table = ItemTable(items)
		table.border = True
		return render_template("home.html", table=table)
		
	else:
		return render_template("home.html")

	#for region in regions['Regions']:
	#	print region
	#text = request.form['text']
	#processed_text = text.upper()
	#return processed_text

if __name__ == "__main__":
	app.run(host='0.0.0.0',debug=True)
