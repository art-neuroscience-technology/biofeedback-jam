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


def main(argv):
   files_dir = ''
   bucket = ''
   folder_name = ''
   access_key = ''
   secret_key = ''
   try:
      opts, args = getopt.getopt(argv,"hd:b:f:a:s:",["dir=","bucket=","folder=", "access_key=","secret_key="])
   except getopt.GetoptError:
      print ('python3 upload_file.py -d <dir> -b <bucket> -f <s3_folder> -a <access_key> -s <secret_key>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('python3 upload_file.py -d <dir> -o <bucket> -f <s3_folder> -a <access_key> -s <secret_key>')
         sys.exit()
      elif opt in ("-d", "--dir"):
         files_dir = arg
      elif opt in ("-b", "--bucket"):
         bucket = arg
      elif opt in ("-f", "--folder"):
         folder_name = arg
      elif opt in ("-a", "--access_key"):
         access_key = arg
      elif opt in ("-s", "--secret_key"):
         secret_key = arg
   try:
      upload_files(files_dir, bucket, folder_name, access_key, secret_key)
   except Exception as ex:
      print(ex)
   
if __name__ == "__main__":
   main(sys.argv[1:])
