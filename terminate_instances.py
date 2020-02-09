import logging
import boto3
from botocore.exceptions import ClientError
from aws_helper import search_instances
from aws_helper import terminate_instances

def main():
	cluster = ['ap-east-1', 'ap-southeast-1']

	for target_region_name in cluster:
		target_key_name = 'andy_aws_test'
		target_state = 'running'
		instance_ids = []
	
		instances = search_instances(target_region_name, target_key_name, target_state)
		for instance in instances:
			instance_ids.append(instance[0])
			
		states = terminate_instances(target_region_name, instance_ids)
	
		if states is not None:
			print('Terminating the following EC2 instances')
			for state in states:
				print('ID: {} '.format(state["InstanceId"]))
				print('\tCurr state: Code {} {}'.format(state["CurrentState"]["Code"], state["CurrentState"]["Name"]))
				print('\tPrev state: Code {} {}'.format(state["PreviousState"]["Code"], state["PreviousState"]["Name"]))
	
	
    # Assign these values before running the program

    # Set up logging
    #logging.basicConfig(level=logging.DEBUG,
    #                    format='%(levelname)s: %(asctime)s: %(message)s')

    # Terminate the EC2 instance(s)
    #states = terminate_instances(ec2_instance_ids)
    #if states is not None:
    #    logging.debug('Terminating the following EC2 instances')
    #    for state in states:
    #        logging.debug('ID: {state["InstanceId"]}')
    #        logging.debug('  Current state: Code {state["CurrentState"]["Code"]}, '
    #                      '{state["CurrentState"]["Name"]}')
    #        logging.debug('  Previous state: Code {state["PreviousState"]["Code"]}, '
    #                      '{state["PreviousState"]["Name"]}')


if __name__ == '__main__':
    main()
