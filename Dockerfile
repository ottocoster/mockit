FROM python:3.11

ENV DEBUG_ENABLED false
ENV DEVICE_TYPE "cisco_ios"
#Only relevant for some devices, it will try to find the version number folder inside the device config folder
ENV DEVICE_VERSION ""

ENV SSH_SERVER_ENABLED true
ENV SSH_KEY "/ssh_key/rsa.key"
ENV SSH_USERNAME "root"
ENV SSH_PASSWORD "Welcome01!"

ENV SSH_PROMPT ""
ENV SSH_RESPONSE_FORMAT ""
ENV SSH_COMMAND_PROMPT_FORMAT ""
ENV SSH_DEFAULT_PROMPT_FORMAT ""
ENV SSH_ECHO_FORMAT ""

ENV SNMP_SERVER_ENABLED true
ENV SNMP_V2_ENABLED true
ENV SNMP_V2_NAME "public"

ENV SNMP_V3_ENABLED false
ENV SNMP_V3_USERNAME "usr-sha-none"

#none, md5, sha, sha224, sha256, sha384, sha512
ENV SNMP_V3_AUTH_TYPE "sha" 
#needs to be atleast 8 characters
ENV SNMP_V3_AUTH_KEY "somekey1"

#none, des, 3des, aes128, aes192, aes256, aesblumenthal192, aesblumenthal256
ENV SNMP_V3_PRIV_TYPE "none"
ENV SNMP_V3_PRIV_KEY ""

COPY configs/. configs/.
COPY ssh_key/. ssh_key/.
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

RUN apt-get update
RUN apt-get install snmp -y

COPY src/. /

CMD ["python", "main.py"]