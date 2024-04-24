import logging
import threading
import boto3
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError, ParamValidationError
import os
import sys
from pprint import pprint
#boto3.set_stream_logger('')
#import json
#from urllib.request import Request, urlopen
#from urllib.error import URLError
#print("========== EC2 Role Capture =========")
#ec2_role_url = "http://< some IP address >/latest/meta-data/iam/security-credentials/EC2_S3_Access_ivault-media"
#ec2_role_response = urlopen(ec2_role_url)
#print(" ============ ec2_role_response ============ ")
#ec2_role_respBytes = ec2_role_response.read()
#print(type(ec2_role_respBytes))
#ec2_role_obj = json.loads(ec2_role_respBytes.decode('utf-8'))
#print(" =============== ec2_role_obj ============== ")
#pprint(ec2_role_obj)
#print(" =============== ec2_role_CREDENTIALS ============== ")
#print("S3 ROLE_ACCESS__ID: " + ec2_role_obj["AccessKeyId"])
#print("S3 ROLE_ACCESS__KEY: " + ec2_role_obj["SecretAccessKey"])

"""
SEE:  https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html

"""
def upload_file_to_S3(file_path, bucket, object_name=None, extraArgs = {}):

    #session = boto3.Session(profile_name="default")

    # pprint(file_path)
    # pprint( bucket)
    # pprint( object_name)

    sts = boto3.client('sts')
    sts.get_caller_identity()

    """Upload a file to an S3 bucket
    :param file_path: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_path is used
    :return: True if file was uploaded, else False
    """

    config = TransferConfig(multipart_threshold=1024 * 25, max_concurrency=10,
                            multipart_chunksize=1024 * 25, use_threads=True)

    # If S3 object_name was not specified, use file_path
    if object_name is None:
        object_name = file_path

    # Boto3 can auto detect the .aws/credntials like this: s3_client = boto3.client('s3')
    # Or you can enter them here from .env file like this :
    # print("S3 ACCESS__ID: " + os.environ['AWS_ACCESS_KEY_ID'])
    # print("S3 SECRET__KEY: " + os.environ['AWS_SECRET_ACCESS_KEY'])
    # print('======== file_path ========')
    # pprint(file_path)
    # print('======== bucket ========')
    # pprint(bucket)
    # print('======== object_name ========')
    # pprint(object_name)
    # pprint('======== ExtraArgs ========')
    # print(extraArgs)
    # print('======== Config ========')
    # pprint(config)

    s3_client = boto3.client('s3')

    try:
        response = s3_client.upload_file(file_path, bucket, object_name,
                                         ExtraArgs=extraArgs,
                                         Config=config,
                                         Callback=ProgressPercentage(file_path))
    except ClientError as e:
        pprint("EXCEPTION in upload_file_to_S3(): " + e)
        logging.error(e)
        return False
    return True


class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(str(percentage))
            sys.stdout.flush()
