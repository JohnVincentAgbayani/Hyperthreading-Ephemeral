import boto3
import json

api_keys_file = open("api_keys.json")
api_keys = json.load(api_keys_file)

ssm_file = open("ssm_ephemeral.json")
ssm_json = ssm_file.read()

region_lookup = {
	"USEA":"us-east-1",
	"USWE":"us-west-1",
	"CACE":"ca-central-1",
	"EUWE":"eu-west-1",
	"EUCE":"eu-cemtral-1",
	"APSP":"ap-southeast-1",
	"APAU":"ap-southeast-2"
}

instance_ids = ["i-0f0d090f886922105"]
target_region = region_lookup["USEA"]
target_env = "deltekdev"

ssm_doc_name = 'test-hyperthreading-ephemeral'

ssm_client = boto3.client('ssm',  region_name = target_region)

ssm_create_response = ssm_client.create_document(Content = ssm_json, Name = ssm_doc_name, DocumentType = 'Command', DocumentFormat = 'JSON', TargetType =  "/AWS::EC2::Instance")
print(ssm_create_response)

# ssm_run_response = ssm_client.send_command(InstanceIds = instance_ids, DocumentName=ssm_doc_name,DocumentVersion="$DEFAULT", TimeoutSeconds=120,)
# print(ssm_run_response)

# ssm_delete_response = ssm_client.delete_document(Name=ssm_doc_name)
# print(ssm_delete_response)