# BIOFEEDBACK
This projects uses a pre-trained GAN in order to generate images from EEG signals.       
Capture EEG activity with Muse Headband and process it, transforming it to a vector, which is input for the GAN. 

## GAN
You can find the code for training the GAN at [neuro-GAN](https://github.com/art-neuroscience-technology/neuro-GAN) 

## Results 
At [results-images](slides/results-images) you can find a mosaic for generated images. 

## Min Monitor
[Mind Monitor](https://mind-monitor.com/) is an app for Muse Headband 

## Install
Follow these instructions:
- Install  numpy and matplotlib https://www.jarutex.com/index.php/2021/08/25/5448/ 
- Install tensorflow lite https://pimylifeup.com/raspberry-pi-tensorflow-lite/
- Install dependecies:

```bash 
	pip3 install -r requirements.txt
	export PATH=$HOME/.local/bin:$PATH
```

## Process

Waves are saved in a list, every 10 seconds a file is saved, creating a csv file. The file contains 10 rows (one per second, calculated by the median of all the registries for that second) and by 10 columns.


AF7_delta,AF7_theta,AF7_alpha,AF7_beta,AF7_gamma,AF8_delta,AF8_theta,AF8_alpha,AF8_beta,AF8_gamma

So, the noise vector is created from this 10x10 matrix, transforming it to a vector. Thus, that is the input for the GAN.  

## Start the system 

[mind_monitor_ocs_server.py](mind_monitor_ocs_server.py): OCS server that listens incoming data from Muse Headband, captures the data and saves the EEG files. 

```bash
	python mind_monitor_osc_server.py --access_key <access_key> --secret_key <secret_key> --mmode <mode> --ip 0.0.0.0 --port 5000
```
[slider/main.py]
```bash
    cd slider/
	python main.py --access_key <access_key> --secret_key <secret_key> --mmode <mode> 
```

access_key and secret_key parameters are the keys to access S3 bucket and mode takes the value True or False, either if you want to save the information in S3 or not. 

# Auxiliar scripts 

[generate_images.py](generate_images.py): generate images with the GAN from saved EEG files 

[generator.py](generator.py): Code for generate a new image using the pre-trained model 

[ocs_emulator.py](ocs_emulator.py): emulates OCS Sender in order to simulate the traffic from the headband 

[upload_files.py](upload_files.py): to upload files to s3 

Execute the following to upload local files at eeg directory to s3 

```bash
	python upload_file.py -d eeg -o biofeedback -a <access_key> -s <secret_key> -f eeg 
```

Execute the following to upload files at to_upload directory to s3 bucket 'biofeedback'

```bash
	python upload_file.py -d to_upload -o biofeedback -a <access_key> -s <secret_key> 
```
