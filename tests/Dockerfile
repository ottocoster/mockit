FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
RUN apt-get update && apt-get install -y iputils-ping  # Install ping

RUN pip3 install --no-cache-dir pysnmp netmiko pytest ncclient requests

COPY *.py test.sh pytest.ini /tests/
WORKDIR /tests
