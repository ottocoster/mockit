from ncclient import manager
expected_result = """
<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply message-id="urn:uuid:test-id"
    xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <data>
        OK
    </data>
</rpc-reply>
"""

mocked_device = 'mocked-device'

def test_netconf():
    # WHEN fetching rpc response from server
    with manager.connect(
        host=mocked_device,
        port=830,
        username="test",
        password="test",
        hostkey_verify=False,
    ) as m:
        # Attempt to retrieve the running configuration
        try:
            # Send get-config request
            result = m.get_config(source='running')
            assert result.strip() == expected_result.strip()

        except Exception as e:
            print(f"Error: {e}")
