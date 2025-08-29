FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV TINI_SUBREAPER=1
ENV DEBUG_ENABLED=false
ENV DEVICE_TYPE="cisco_ios"
#Only relevant for some devices, it will try to find the version number folder inside the device config folder
ENV DEVICE_VERSION=""

ENV SSH_SERVER_ENABLED=""
ENV SSH_KEY="/ssh_key/rsa.key"
ENV SSH_USERNAME="root"
ENV SSH_PASSWORD="Welcome01!"
ENV AUTHKEY_ENABLED=false
ENV AUTHKEY_PATH="/auth_keys/auth.pub"

ENV SNMP_SERVER_ENABLED=true
ENV SNMP_V2_ENABLED=true
ENV SNMP_V2_COMMUNITY="public"

ENV SNMP_V3_ENABLED=false
ENV SNMP_V3_USERNAME="usr-sha-none"

#none, md5, sha, sha224, sha256, sha384, sha512
ENV SNMP_V3_AUTH_TYPE="sha"
#needs to be atleast 8 characters
ENV SNMP_V3_AUTH_KEY="somekey1"

#none, des, 3des, aes128, aes192, aes256, aesblumenthal192, aesblumenthal256
ENV SNMP_V3_PRIV_TYPE="none"
ENV SNMP_V3_PRIV_KEY=""

ENV NETCONF_SERVER_ENABLED=true
ENV NETCONF_USERNAME="test"
ENV NETCONF_PASSWORD="test"

ENV TELNET_SERVER_ENABLED=""
ENV TELNET_USERNAME="test"
ENV TELNET_PASSWORD="test"

ENV OPENAI_SUPPORT=false
ENV OPENAI_APIKEY=""

ENV PYTHONPATH="/"

COPY configs/. configs/.
COPY dev/. /test
COPY requirements.txt requirements.txt
COPY src/. /src
COPY ssh_key/. ssh_key/.
COPY auth_keys/. auth_keys/.

RUN apt update -y && apt upgrade -y \
    && apt-get install procps snmp tini -y \
    && uv pip install --system --no-cache -r requirements.txt

EXPOSE 22 23 161

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "/src/main.py"]
