FROM python:3.11
RUN apt-get update && apt-get install -y iputils-ping  # Install ping

RUN pip3 install pysnmp-lextudio
RUN pip3 install netmiko
RUN pip3 install pytest

COPY *.py /tests/
COPY pytest.ini /tests/pytest.ini
WORKDIR /tests
