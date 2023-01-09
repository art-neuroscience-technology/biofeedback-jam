# BIOFEEDBACK
This projects uses a pre-trained GAN in order to generate images from EEG signals.       
Capture EEG activity with Muse Headband and process it, transforming it to a vector, which is input for the GAN. 


## GAN
You can find the code for training the GAN at [neuro-GAN](https://github.com/art-neuroscience-technology/neuro-GAN) 

## Results 
At [https://github.com/art-neuroscience-technology/neuro-GAN/tree/main/images] you can find a mosaic for generated images. 

## Min Monitor
[Mind Monitor](https://mind-monitor.com/) is an app for Muse Headband 


## Install
TODO

## Process

Waves are saved in a list, every 10 seconds a file is saved, creating a csv file. The file contains 10 rows (one per second, calculated by the median of all the registries for that second) and by 10 columns.


AF7_delta,AF7_theta,AF7_alpha,AF7_beta,AF7_gamma,AF8_delta,AF8_theta,AF8_alpha,AF8_beta,AF8_gamma

So, the noise vector is created from this 10x10 matrix, transforming it to a vector. Thus, that is the input for the GAN.  

## Scripts

[mind_monitor_ocs_server.py](mind_monitor_ocs_server.py): OCS server that listens incoming data from Muse Headband, captures the data and saves the EEG files. 

[generate_images.py](generate_images.py): generate images with the GAN from saved EEG files 

[generator.py](generator.py): Code for generate a new image using the pre-trained model 

[ocs_emulator.py](ocs_emulator.py): emulates OCS Sender in order to simulate the traffic from the headband 

[resize_images.py](resize_images.py): uses ESRGAN pre-trained model for resizing the images keeping the resolution 

[upload_files.py](upload_files.py): to upload files to s3 

Execute the following to upload files at eeg directory to s3

```bash
	python3 upload_files.py -d eeg -b biofeedback -f eeg -a {ACCESS_KEY} -s {SECRET_KEY}
```


Execute the following to upload files at images directory to s3

```bash
	python3 upload_files.py -d to_upload -b biofeedback -f images -a {ACCESS_KEY} -s {SECRET_KEY}
```
