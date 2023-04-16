FROM python:3.8-slim-buster

# Install any additional dependencies
RUN apt-get update && apt-get install -y vim curl 

# Install TensorFlow Lite
RUN pip install tflite-runtime

COPY slider /app/slider

COPY requirements.txt /app/requirements.txt

RUN pip install -r  /app/requirements.txt

EXPOSE 7001 
EXPOSE 5001 

WORKDIR /app/slider 

ENTRYPOINT ["python", "app.py"]
