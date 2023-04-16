#!/bin/bash/python3

import os
import sys, getopt
import boto3
from botocore.exceptions import NoCredentialsError


def upload_to_s3(local_file, bucket, s3_file, aws_access_key_id, aws_secret_access_key):
    try:
        
        s3 = boto3.client('s3', 
            aws_access_key_id=aws_access_key_id, 
            aws_secret_access_key=aws_secret_access_key
            )
        
        response = s3.upload_file(local_file, bucket, s3_file)
        print(f'response={response}')

        return True
        
    except FileNotFoundError:
        print(f"The file {local_file} was not found")
        return False

    except NoCredentialsError:
        print("Credentials not available")
        return False
    except Exception as ex:
        print(f'Error:{ex}')
        return False
        

