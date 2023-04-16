import os
from distutils.util import strtobool

class Config:
    def __init__(self):
        self.s3_bucket = os.getenv('S3_BUCKET', 'biofeedback')
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID', '')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', '')
        self.models_path = os.getenv('MODELS_PATH')
        self.images_path = os.getenv('IMAGES_PATH')
        self.qrs_path = os.getenv('QRS_PATH', '/app/qrs')
        self.qrs_backup_path = os.getenv('QRS_BACKUP_PATH', '/app/backup_qrs')
        self.result_grid_path = os.getenv('RESULT_GRID_PATH', '/app/result/')
        self.result_grid_path_backup = os.getenv('RESULT_GRID_PATH_BACKUP',  '/app/to_upload/')
        self.logos_path = os.getenv('LOGOS_PATH', '/app/slider/logos')
        self.ql_path = os.getenv('QL_PATH', '')
        self.generate_qr = bool(strtobool(os.getenv('GENERTE_QR', 'False')))
        self.result_eeg_path = os.getenv('RESULT_EEG_PATH', '/app/eeg-files')
        self.eeg_backup_folder = os.getenv('EEG_BACKUP_FOLDER', '/app/eeg/')
        self.port = int(os.getenv('PORT_SLIDER', 7000))
        self.osc_ip = os.getenv('IP', '0.0.0.0')
        self.osc_port = int(os.getenv('PORT', '5001'))
        self.row_size = int(os.getenv('ROW_SIZE', '6'))
        self.col_size = int(os.getenv('ROW_SIZE', '3'))
        self.save_mode_slider = bool(strtobool(os.getenv('SAVE_MODE_SLIDER', 'False')))
        self.save_mode_mind_monitor = bool(strtobool(os.getenv('SAVE_MODE_MIND_MONITOR', 'False')))
        self.interval = int(os.getenv('INTERVAL', '0'))
