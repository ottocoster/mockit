from netmiko import ConnectHandler
import pytest

def run_command(host, device_type, command, username="root", password="test"):
    parameters = { 
        "device_type": device_type,
        "host": host,
        "username": username,
        "password": password,
    }

    with ConnectHandler(**parameters) as net_connect:
        return net_connect.send_command(command)

@pytest.mark.test_telnets
def test_adtran_os():
    assert run_command("devices-adtran_os", "adtran_os_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_apresia_aeos():
    assert run_command("devices-apresia_aeos", "apresia_aeos_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_arista_eos():
    assert run_command("devices-arista_eos", "arista_eos_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_aruba_procurve():
    assert run_command("devices-aruba_procurve", "aruba_procurve_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_audiocode_72():
    assert run_command("devices-audiocode_72", "audiocode_72_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_audiocode_66():
    assert run_command("devices-audiocode_66", "audiocode_66_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_audiocode_shell():
    assert run_command("devices-audiocode_shell", "audiocode_shell_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_brocade_fastiron():
    assert run_command("devices-brocade_fastiron", "brocade_fastiron_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_brocade_netiron():
    assert run_command("devices-brocade_netiron", "brocade_netiron_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_calix_b6():
    assert run_command("devices-calix_b6", "calix_b6_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_centec_os():
    assert run_command("devices-centec_os", "centec_os_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_ciena_saos():
    assert run_command("devices-ciena_saos", "ciena_saos_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_cisco_ios():
    assert run_command("devices-cisco_ios", "cisco_ios_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_cisco_xr():
    assert run_command("devices-cisco_xr", "cisco_xr_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_cisco_s200():
    assert run_command("devices-cisco_s200", "cisco_s200_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_cisco_s300():
    assert run_command("devices-cisco_s300", "cisco_s300_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_dell_dnos6():
    assert run_command("devices-dell_dnos6", "dell_dnos6_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_dell_powerconnect():
    assert run_command("devices-dell_powerconnect", "dell_powerconnect_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_dlink_ds():
    assert run_command("devices-dlink_ds", "dlink_ds_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_extreme():
    assert run_command("devices-extreme", "extreme_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_extreme_exos():
    assert run_command("devices-extreme_exos", "extreme_exos_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_extreme_netiron():
    assert run_command("devices-extreme_netiron", "extreme_netiron_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_generic():
    assert run_command("devices-generic", "generic_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_hp_procurve():
    assert run_command("devices-hp_procurve", "hp_procurve_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_hp_comware():
    assert run_command("devices-hp_comware", "hp_comware_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_huawei():
    assert run_command("devices-huawei", "huawei_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_huawei_olt():
    assert run_command("devices-huawei_olt", "huawei_olt_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_ipinfusion_ocnos():
    assert run_command("devices-ipinfusion_ocnos", "ipinfusion_ocnos_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_juniper_junos():
    assert run_command("devices-juniper_junos", "juniper_junos_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_nokia_sros():
    assert run_command("devices-nokia_sros", "nokia_sros_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_oneaccess_oneos():
    assert run_command("devices-oneaccess_oneos", "oneaccess_oneos_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_paloalto_panos():
    assert run_command("devices-paloalto_panos", "paloalto_panos_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_rad_etx():
    assert run_command("devices-rad_etx", "rad_etx_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_raisecom():
    assert run_command("devices-raisecom", "raisecom_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_ruckus_fastiron():
    assert run_command("devices-ruckus_fastiron", "ruckus_fastiron_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_ruijie_os():
    assert run_command("devices-ruijie_os", "ruijie_os_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_supermicro_smis():
    assert run_command("devices-supermicro_smis", "supermicro_smis_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_teldat_cit():
    assert run_command("devices-teldat_cit", "teldat_cit_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_tplink_jetstream():
    assert run_command("devices-tplink_jetstream", "tplink_jetstream_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_yamaha():
    assert run_command("devices-yamaha", "yamaha_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_zte_zxros():
    assert run_command("devices-zte_zxros", "zte_zxros_telnet", "echo test") == "test"

@pytest.mark.test_telnets
def test_maipu():
    assert run_command("devices-maipu", "maipu_telnet", "echo test") == "test"
