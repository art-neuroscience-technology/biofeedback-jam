FROM --platform=linux/amd64 python:3.8-slim-buster

# Install any additional dependencies
RUN apt-get update && apt-get install -y vim curl 

# Install TensorFlow Lite
RUN pip install tflite-runtime

COPY requirements.txt /app/requirements.txt

RUN pip install -r  /app/requirements.txt

COPY slider /app/slider

EXPOSE 7001/tcp 5001/udp 

WORKDIR /app/slider 

ENTRYPOINT ["python", "app.py"]
