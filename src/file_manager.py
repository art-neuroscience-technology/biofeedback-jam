import s3_uploader 
import os 
import shutil 

class FileManager():
     def __init__(self,result_eeg_path, eeg_backup_folder, s3_bucket, s3_key, s3_secret_key):
         self.result_eeg_path = result_eeg_path
         self.s3_bucket = s3_bucket
         self.eeg_backup_folder = eeg_backup_folder
         self.s3_key = s3_key
         self.s3_secret_key = s3_secret_key

def save_eeg(self, df, save_name):
    result = f'{self.result_eeg_path}/{save_name}.csv'
    df.to_csv(result)
    ok = s3_uploader.upload_to_s3(result, 
        self,s3_uploader, 
        f'eeg/{save_name}.csv', 
        self.s3_key, 
        self.s3_secret_key)
    if ok:
        os.remove(result)
    else:
        shutil.move(result, self.eeg_backup_folder)