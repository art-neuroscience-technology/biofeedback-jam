#!/bin/bash/python3

import os
import sys, getopt
import boto3
from botocore.exceptions import NoCredentialsError


def upload_to_s3(local_file, bucket, s3_file, aws_access_key_id, aws_secret_access_key):
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    try:
        print(f"Uploading file {local_file}")
        s3.upload_file(local_file, bucket, s3_file)
        return True
    except FileNotFoundError:
        print(f"The file {local_file} was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


#Save files at the S3 bucket, creating a folder per identifier  
def upload_files(files_dir, bucket, folder_name, aws_access_key_id, aws_secret_access_key):
    for file_name in os.listdir(files_dir):
        identifier = file_name.split('_')[0]
        ok = upload_to_s3(f'{files_dir}/{file_name}',
            bucket, 
            f'{folder_name}/{identifier}/{file_name}', 
            aws_access_key_id, 
            aws_secret_access_key
         )
        if (ok):
         os.remove(f'{files_dir}/{file_name}')

