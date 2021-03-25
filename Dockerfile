FROM python:3.8-slim-buster

WORKDIR /usr/workload-scaler

COPY . .

RUN python3 setup.py install