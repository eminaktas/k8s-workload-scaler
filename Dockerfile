FROM python:3.8-slim-buster

WORKDIR /usr/workload-scaler

COPY . .

RUN pip3 install -r requirements.txt