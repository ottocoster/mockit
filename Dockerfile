FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV TINI_SUBREAPER=1 \
    DEBUG_ENABLED=false \
    LOG_FULL_PATH="true" \
    DEVICE_TYPE="cisco_ios" \
#Only relevant for some devices, it will try to find the version number folder inside the device config folder
    DEVICE_VERSION="" \
    SSH_SERVER_ENABLED="" \
    SSH_KEY="/ssh_key/rsa.key" \
    SSH_USERNAME="root" \
    SSH_PASSWORD="Welcome01!" \
    SSH_KEX_ALGORITHMS="" \
    SSH_CIPHERS="" \
    AUTHKEY_ENABLED=false \
    AUTHKEY_PATH="/auth_keys/auth.pub" \
    SNMP_SERVER_ENABLED="" \
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
    NETCONF_SERVER_ENABLED="" \
    NETCONF_USERNAME="test" \
    NETCONF_PASSWORD="test" \
    TELNET_SERVER_ENABLED="" \
    TELNET_USERNAME="test" \
    TELNET_PASSWORD="test" \
    AI_SUPPORT=false \
    AI_APIKEY="" \
    AI_URL="" \
    AI_MODEL="gpt-5.5" \
    AI_STORE_RESPONSES=false \
    API_SERVER_ENABLED="" \
    API_PORT="80" \
    API_AUTH_TYPE="none" \
    API_TOKEN="" \
    API_KEY="" \
    API_KEY_HEADER="X-API-KEY" \
    API_OAUTH_CLIENT_ID="" \
    API_OAUTH_CLIENT_SECRET="" \
    API_TLS="false" \
    API_TLS_KEY="/api_cert/key.pem" \
    API_CERT="/api_cert/cert.pem" \
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
    && apt-get install procps snmp tini openssl -y \
    && mkdir -p /api_cert \
    && openssl req -x509 -newkey rsa:2048 -nodes \
        -keyout /api_cert/key.pem -out /api_cert/cert.pem \
        -days 3650 -subj "/CN=mockit" \
    && uv pip install --system --no-cache -r requirements.txt

EXPOSE 22 23 161 443

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "/src/main.py"]
