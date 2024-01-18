from netmiko import ConnectHandler, platforms  

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
        return net_connect.send_command_timing(command)

def test_a10():
    assert run_command("devices-a10", "a10", "echo test") == "test"

def test_accedian():
    assert run_command("devices-accedian", "accedian", "echo test") == "test"

def test_adtran_os():
    assert run_command("devices-adtran_os", "adtran_os", "echo test") == "test"

def test_adva_fsp150f2():
    assert run_command("devices-adva_fsp150f2", "adva_fsp150f2", "echo test") == "test"

def test_adva_fsp150f3():
    assert run_command("devices-adva_fsp150f3", "adva_fsp150f3", "echo test") == "test"

def test_alcatel_aos():
    assert run_command("devices-alcatel_aos", "alcatel_aos", "echo test") == "test"

def test_alcatel_sros():
    assert run_command("devices-alcatel_sros", "alcatel_sros", "echo test") == "test"

def test_allied_telesis_awplus():
    assert run_command("devices-allied_telesis_awplus", "allied_telesis_awplus", "echo test") == "test"

def test_apresia_aeos():
    assert run_command("devices-apresia_aeos", "apresia_aeos", "echo test") == "test"

def test_arista_eos():
    assert run_command("devices-arista_eos", "arista_eos", "echo test") == "test"
    
def test_arris_cer():
    assert run_command("devices-arris_cer", "arris_cer", "echo test") == "test"

def test_aruba_os():
    assert run_command("devices-aruba_os", "aruba_os", "echo test") == "test"
    
def test_aruba_osswitch():
    assert run_command("devices-aruba_osswitch", "aruba_osswitch", "echo test") == "test"
    
def test_aruba_procurve():
    assert run_command("devices-aruba_procurve", "aruba_procurve", "echo test") == "test"
    
def test_audiocode_66():
    assert run_command("devices-audiocode_66", "audiocode_66", "echo test") == "test"
    
def test_audiocode_72():
    assert run_command("devices-audiocode_72", "audiocode_72", "echo test") == "test"
    
def test_audiocode_shell():
    assert run_command("devices-audiocode_shell", "audiocode_shell", "echo test") == "test"
    
def test_avaya_ers():
    assert run_command("devices-avaya_ers", "avaya_ers", "echo test") == "test"
    
def test_avaya_vsp():
    assert run_command("devices-avaya_vsp", "avaya_vsp", "echo test") == "test"
    
def test_broadcom_icos():
    assert run_command("devices-broadcom_icos", "broadcom_icos", "echo test") == "test"
    
def test_brocade_fastiron():
    assert run_command("devices-brocade_fastiron", "brocade_fastiron", "echo test") == "test"
    
def test_brocade_fos():
    assert run_command("devices-brocade_fos", "brocade_fos", "echo test") == "test"
    
def test_brocade_netiron():
    assert run_command("devices-brocade_netiron", "brocade_netiron", "echo test") == "test"
    
def test_brocade_nos():
    assert run_command("devices-brocade_nos", "brocade_nos", "echo test") == "test"
    
def test_brocade_vdx():
    assert run_command("devices-brocade_vdx", "brocade_vdx", "echo test") == "test"
    
def test_brocade_vyos():
    assert run_command("devices-brocade_vyos", "brocade_vyos", "echo test") == "test"
    
def test_calix_b6():
    assert run_command("devices-calix_b6", "calix_b6", "echo test") == "test"
    
def test_casa_cmts():
    assert run_command("devices-casa_cmts", "casa_cmts", "echo test") == "test"
    
def test_cdot_cros():
    assert run_command("devices-cdot_cros", "cdot_cros", "echo test") == "test"
    
def test_centec_os():
    assert run_command("devices-centec_os", "centec_os", "echo test") == "test"
    
def test_checkpoint_gaia():
    assert run_command("devices-checkpoint_gaia", "checkpoint_gaia", "echo test") == "test"
    
def test_ciena_saos():
    assert run_command("devices-ciena_saos", "ciena_saos", "echo test") == "test"

def test_cisco_asa():
    assert run_command("devices-cisco_asa", "cisco_asa", "echo test") == "test"
    
def test_cisco_ftd():
    assert run_command("devices-cisco_ftd", "cisco_ftd", "echo test") == "test"

def test_cisco_ios():
    assert run_command("devices-cisco_ios", "cisco_ios", "echo test") == "test"

def test_cisco_nxos():
    assert run_command("devices-cisco_nxos", "cisco_nxos", "echo test") == "test"

def test_cisco_wlc():
    assert run_command("devices-cisco_wlc", "cisco_wlc", "echo test") == "test"

def test_cisco_xr():
    assert run_command("devices-cisco_xr", "cisco_xr", "echo test") == "test"

def test_fortinet():
    assert run_command("devices-fortinet", "fortinet", "echo test") == "test"

def test_hp_comware():
    assert run_command("devices-hp_comware", "hp_comware", "echo test") == "test"

def test_huawei():
    assert run_command("devices-huawei", "huawei", "echo test") == "test"

def test_juniper_junos():
    assert run_command("devices-juniper_junos", "juniper_junos", "echo test") == "test"

def test_mikrotik_routeros_v6():
    assert run_command("devices-mikrotik_routeros_v6", "mikrotik_routeros", "echo test") == "test"

def test_mikrotik_routeros_v7():
    assert run_command("devices-mikrotik_routeros_v7", "mikrotik_routeros", "echo test") == "test"

def test_ubiquiti_edgerouter():
    assert run_command("devices-ubiquiti_edgerouter", "ubiquiti_edgerouter", "echo test") == "test"

def test_ubiquiti_edgeswitch():
    assert run_command("devices-ubiquiti_edgeswitch", "ubiquiti_edgeswitch", "echo test") == "test"