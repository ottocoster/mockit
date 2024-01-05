FROM python:3.11

RUN pip3 install pysnmp-lextudio
RUN pip3 install netmiko
RUN pip3 install pytest

COPY *.py /tests/
WORKDIR /tests
