RPC_REPLY_OK = """<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply message-id="{message_id}" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <ok/> <!-- ok response -->
</rpc-reply>"""

RPC_REPLY_ERROR = """<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply message-id="{message_id}" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <rpc-error>
        <error-type>{type}</error-type>
        <error-tag>{tag}</error-tag>
        <error-severity>error</error-severity>
        <error-message xml:lang="en">{message}</error-message>
    </rpc-error>
</rpc-reply>"""
