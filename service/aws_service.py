import boto3

from config import *
import time

from logger import log

filefmt = '%m%d'

t = time.strftime(filefmt, time.localtime())

class AWSService:
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=S3_AWS_ACCESS_KEY,
            aws_secret_access_key=S3_AWS_SECRET_KEY,
        )
        self.data_dir = f"{os.getcwd()}/data"
        self.log_file = f"{os.getcwd()}/logs/crypto.log"
        self.bucket_name = S3_BUCKET_NAME

    def upload(self, file_name, bucket, object_name=None):
        if object_name is None:
            object_name = file_name
        return self.client.upload_file(file_name, bucket, object_name)

    def upload_data_files(self):
        for filename in os.listdir(self.data_dir):
            local_file_path = os.path.join(self.data_dir, filename)

            s3_file_name = f"data/{t}_{filename}"
            log.debug(f"Uploading {local_file_path} as {s3_file_name} to S3")
            self.upload(local_file_path, self.bucket_name, s3_file_name)

        log_s3_file_name = f"logs/{t}_crypto.log"
        log.debug(f"Uploading {self.log_file} as {log_s3_file_name} to S3")
        self.upload(self.log_file, self.bucket_name, log_s3_file_name)
