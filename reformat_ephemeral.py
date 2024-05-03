import boto3
import json
import os

from datetime import datetime

def main():

	ssm_file = open("ssm_ephemeral.json")
	ssm_json = ssm_file.read()

	instance_ids = os.environ['Instance ID'].split('\n')
	target_region = os.environ['Region']

	data_log = {"targets":instance_ids, "region":target_region}

	region_lookup = {
		"USEA":"us-east-1",
		"USWE":"us-west-2",
		"CACE":"ca-central-1",
		"EUWE":"eu-west-1",
		"EUCE":"eu-cemtral-1",
		"APSP":"ap-southeast-1",
		"APAU":"ap-southeast-2"
	}

	target_region = region_lookup[target_region]

	ssm_doc_name = 'test-hyperthreading-ephemeral'
	ssm_client = boto3.client('ssm',  region_name = target_region)

	ssm_create_response = ssm_client.create_document(Content = ssm_json, Name = ssm_doc_name, DocumentType = 'Command', DocumentFormat = 'JSON', TargetType =  "/AWS::EC2::Instance")

	for instance in instance_ids:
		ssm_run_response = ssm_client.send_command(InstanceIds = [instance], DocumentName=ssm_doc_name, DocumentVersion="$DEFAULT", TimeoutSeconds=120)
		data_log[instance] = str(ssm_run_response)

	ssm_delete_response = ssm_client.delete_document(Name=ssm_doc_name)

	target_date = str(datetime.today().strftime('%Y-%m-%d(%H:%M:%S)'))
	final_filename = f'reformat_ephemeral({target_date}).json'

	with open('log_data.json', 'w') as outfile:
	    json.dump(data_log, outfile)

	return data_log  


def write_json_s3(data_log):
	
	goss_key_file = open("goss_key.txt")
	goss_key = goss_key_file.read()
	goss_key = goss_key.replace("\n","").strip()

	goss_secret_file = open("goss_secret.txt")
	goss_secret = goss_secret_file.read()
	goss_secret = goss_secret.replace("\n","").strip()

	log_file = open("log_data.json")
	log_json = log_file.read()
	log_json = log_json.replace("'",'"')
	log_json = json.loads(log_json)

	target_bucket = "hyper-threading-automation-logs"
	target_date = str(datetime.today().strftime('%Y-%m-%d(%H:%M:%S)'))
	final_filename = f'hyperthreading-ephemeral({target_date}).json'

	s3_resource = boto3.resource('s3', aws_access_key_id=goss_key, aws_secret_access_key=goss_secret)
	folder_filename = f'ephemeral-disks-log/{final_filename}'

	s3object = s3_resource.Object(target_bucket, folder_filename)

	s3object.put(Body=(bytes(json.dumps(log_json, indent=4).encode('UTF-8'))))


data_log = main()
write_json_s3(data_log)