FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV TINI_SUBREAPER=1 \
    DEBUG_ENABLED=false \
    DEVICE_TYPE="cisco_ios" \
#Only relevant for some devices, it will try to find the version number folder inside the device config folder
    DEVICE_VERSION="" \

    SSH_SERVER_ENABLED="" \
    SSH_KEY="/ssh_key/rsa.key" \
    SSH_USERNAME="root" \
    SSH_PASSWORD="Welcome01!" \
    AUTHKEY_ENABLED=false \
    AUTHKEY_PATH="/auth_keys/auth.pub" \

    SNMP_SERVER_ENABLED=true \
    SNMP_V2_ENABLED=true \
    SNMP_V2_COMMUNITY="public" \

    SNMP_V3_ENABLED=false \
    SNMP_V3_USERNAME="usr-sha-none" \

#none, md5, sha, sha224, sha256, sha384, sha512
    SNMP_V3_AUTH_TYPE="sha" \
#needs to be atleast 8 characters
    SNMP_V3_AUTH_KEY="somekey1" \

#none, des, 3des, aes128, aes192, aes256, aesblumenthal192, aesblumenthal256
    SNMP_V3_PRIV_TYPE="none" \
    SNMP_V3_PRIV_KEY="" \

    NETCONF_SERVER_ENABLED=true \
    NETCONF_USERNAME="test" \
    NETCONF_PASSWORD="test" \

    TELNET_SERVER_ENABLED="" \
    TELNET_USERNAME="test" \
    TELNET_PASSWORD="test" \

    OPENAI_SUPPORT=false \
    OPENAI_APIKEY="" \

    PYTHONPATH="/" 

# Copy app directories
COPY configs/ /configs/
COPY src/ /src/
COPY ssh_key/ /ssh_key/
COPY auth_keys/ /auth_keys/
COPY mibs/ /mibs/

# Copy dependency file
COPY requirements.txt /

RUN apt update -y && apt upgrade -y \
    && apt-get install procps snmp tini -y \
    && uv pip install --system --no-cache -r requirements.txt

EXPOSE 22 23 161

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "/src/main.py"]
