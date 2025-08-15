FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
RUN apt-get update && apt-get install -y iputils-ping  # Install ping

RUN pip3 install pysnmp-lextudio
RUN pip3 install netmiko
RUN pip3 install pytest
RUN pip3 install ncclient

COPY *.py /tests/
COPY pytest.ini /tests/pytest.ini
WORKDIR /tests
