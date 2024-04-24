# Scratch notes

curl http://< some IP address >/latest/meta-data/iam/security-credentials/EC2_S3_Access_ivault-media


from urllib.request import Request, urlopen
from urllib.error import URLError
print("========== EC2 Role Capture =========")
ec2_role_url = "http://< some IP address >/latest/meta-data/iam/security-credentials/EC2_S3_Access_ivault-media"
ec2_role_response = urlopen(ec2_role_url)
print(" ============ ec2_role_response ============ ")
ec2_role_respBytes = ec2_role_response.read()
print(type(ec2_role_respBytes))
ec2_role_obj = json.loads(ec2_role_respBytes.decode('utf-8'))
print(" =============== ec2_role_obj ============== ")
pprint(ec2_role_obj)
print(" =============== ec2_role_CREDENTIALS ============== ")
print(ec2_role_obj["AccessKeyId"])
print(ec2_role_obj["SecretAccessKey"])
session = boto3.Session(aws_access_key_id=ec2_role_obj["AccessKeyId"], aws_secret_access_key=ec2_role_obj["SecretAccessKey"])


#  https://stackoverflow.com/questions/49184578/how-to-convert-bytes-type-to-dictionary
#  convert type of 'bytes' to dict or json

https://stackoverflow.com/questions/45170108/how-to-get-the-users-canonical-id-for-adding-a-s3-permission
