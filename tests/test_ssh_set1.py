from netmiko import ConnectHandler, platforms  
import pytest

def run_command(host, device_type, command, username="root", password="test"):
    parameters = { 
        "device_type": device_type,
        "host": host,
        "username": username,
        "password": password,
        "verbose": True,
        "fast_cli": False
    }

    with ConnectHandler(**parameters) as net_connect:
        return net_connect.send_command(command)

@pytest.mark.test_set1
def test_a10():
    assert run_command("devices_a10", "a10", "echo test") == "test"

@pytest.mark.test_set1
def test_accedian():
    assert run_command("devices_accedian", "accedian", "echo test") == "test"

@pytest.mark.test_set1
def test_adtran_os():
    assert run_command("devices_adtran_os", "adtran_os", "echo test") == "test"

@pytest.mark.test_set1
def test_alcatel_aos():
    assert run_command("devices_alcatel_aos", "alcatel_aos", "echo test") == "test"

@pytest.mark.test_set1
def test_alcatel_sros():
    assert run_command("devices_alcatel_sros", "alcatel_sros", "echo test") == "test"

@pytest.mark.test_set1
def test_allied_telesis_awplus():
    assert run_command("devices_allied_telesis_awplus", "allied_telesis_awplus", "echo test") == "test"

@pytest.mark.test_set1
def test_apresia_aeos():
    assert run_command("devices_apresia_aeos", "apresia_aeos", "echo test") == "test"

@pytest.mark.test_set1
def test_arista_eos():
    assert run_command("devices_arista_eos", "arista_eos", "echo test") == "test"
    
@pytest.mark.test_set1
def test_arris_cer():
    assert run_command("devices_arris_cer", "arris_cer", "echo test") == "test"

@pytest.mark.test_set1
def test_aruba_os():
    assert run_command("devices_aruba_os", "aruba_os", "echo test") == "test"
    
@pytest.mark.test_set1
def test_aruba_osswitch():
    assert run_command("devices_aruba_osswitch", "aruba_osswitch", "echo test") == "test"
    
@pytest.mark.test_set1
def test_aruba_procurve():
    assert run_command("devices_aruba_procurve", "aruba_procurve", "echo test") == "test"
    
@pytest.mark.test_set1
def test_audiocode_66():
    assert run_command("devices_audiocode_66", "audiocode_66", "echo test") == "test"
    
@pytest.mark.test_set1
def test_audiocode_72():
    assert run_command("devices_audiocode_72", "audiocode_72", "echo test") == "test"
    
# @pytest.mark.test_set1
# def test_audiocode_shell():
#     assert run_command("devices_audiocode_shell", "audiocode_shell", "echo test") == "test"
    
@pytest.mark.test_set1
def test_avaya_ers():
    assert run_command("devices_avaya_ers", "avaya_ers", "echo test") == "test"
    
@pytest.mark.test_set1
def test_avaya_vsp():
    assert run_command("devices_avaya_vsp", "avaya_vsp", "echo test") == "test"
    
@pytest.mark.test_set1
def test_broadcom_icos():
    assert run_command("devices_broadcom_icos", "broadcom_icos", "echo test") == "test"
    
@pytest.mark.test_set1
def test_brocade_fastiron():
    assert run_command("devices_brocade_fastiron", "brocade_fastiron", "echo test") == "test"
    
@pytest.mark.test_set1
def test_brocade_fos():
    assert run_command("devices_brocade_fos", "brocade_fos", "echo test") == "test"
    
@pytest.mark.test_set1
def test_brocade_netiron():
    assert run_command("devices_brocade_netiron", "brocade_netiron", "echo test") == "test"
    
@pytest.mark.test_set1
def test_brocade_nos():
    assert run_command("devices_brocade_nos", "brocade_nos", "echo test") == "test"
    
@pytest.mark.test_set1
def test_brocade_vdx():
    assert run_command("devices_brocade_vdx", "brocade_vdx", "echo test") == "test"
    
@pytest.mark.test_set1
def test_brocade_vyos():
    assert run_command("devices_brocade_vyos", "brocade_vyos", "echo test") == "test"
    
@pytest.mark.test_set1
def test_calix_b6():
    assert run_command("devices_calix_b6", "calix_b6", "echo test") == "test"
    
@pytest.mark.test_set1
def test_casa_cmts():
    assert run_command("devices_casa_cmts", "casa_cmts", "echo test") == "test"
    
@pytest.mark.test_set1
def test_cdot_cros():
    assert run_command("devices_cdot_cros", "cdot_cros", "echo test") == "test"
    
@pytest.mark.test_set1
def test_centec_os():
    assert run_command("devices_centec_os", "centec_os", "echo test") == "test"
    
@pytest.mark.test_set1
def test_checkpoint_gaia():
    assert run_command("devices_checkpoint_gaia", "checkpoint_gaia", "echo test") == "test"
    
@pytest.mark.test_set1
def test_ciena_saos():
    assert run_command("devices_ciena_saos", "ciena_saos", "echo test") == "test"

@pytest.mark.test_set1
def test_cisco_asa():
    assert run_command("devices_cisco_asa", "cisco_asa", "echo test") == "test"
    
@pytest.mark.test_set1
def test_cisco_ftd():
    assert run_command("devices_cisco_ftd", "cisco_ftd", "echo test") == "test"

@pytest.mark.test_set1
def test_cisco_ios():
    assert run_command("devices_cisco_ios", "cisco_ios", "echo test") == "test"

@pytest.mark.test_set1
def test_cisco_nxos():
    assert run_command("devices_cisco_nxos", "cisco_nxos", "echo test") == "test"

@pytest.mark.test_set1
def test_cisco_s200():
    assert run_command("devices_cisco_s200", "cisco_s200", "echo test") == "test"

@pytest.mark.test_set1
def test_cisco_s300():
    assert run_command("devices_cisco_s300", "cisco_s300", "echo test") == "test"

# @pytest.mark.test_set1
# def test_cisco_tp():
#     assert run_command("devices_cisco_tp", "cisco_tp", "echo test") == "test"

@pytest.mark.test_set1
def test_cisco_viptela():
    assert run_command("devices_cisco_viptela", "cisco_viptela", "echo test") == "test"

@pytest.mark.test_set1
def test_cisco_wlc():
    assert run_command("devices_cisco_wlc", "cisco_wlc", "echo test") == "test"

@pytest.mark.test_set1
def test_cisco_xe():
    assert run_command("devices_cisco_xe", "cisco_xe", "echo test") == "test"

@pytest.mark.test_set1
def test_cisco_xr():
    assert run_command("devices_cisco_xr", "cisco_xr", "echo test") == "test"

@pytest.mark.test_set1
def test_cloudgenix_ion():
    assert run_command("devices_cloudgenix_ion", "cloudgenix_ion", "echo test") == "test"

@pytest.mark.test_set1
def test_coriant():
    assert run_command("devices_coriant", "coriant", "echo test") == "test"