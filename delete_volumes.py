import boto3

ec2 = boto3.resource('ec2', region_name='ap-east-1')
volumes_collection = ec2.volumes.filter(Filters=[{'Name':'status', 'Values': ['available']}])

volumes = []
for volume in volumes_collection:
	v = ec2.Volume(volume.id)
	v.delete()




