from src.ssh_server.db_operations import create_table, create_record, read_record, update_record, delete_record
import re
create_table('cisco_ios')
def handle_command(command: str):
    if command.startswith("add vlan"):

        # Get the vlan number
        match = re.search(r'add vlan (\d+)', command)
        if match:
            vlan_number = match.group(1)

            db_vlan = read_record("cisco_ios","vlan")
            if db_vlan:
                update_record("cisco_ios", "vlan", db_vlan + " " + vlan_number)
            else:
                create_record("cisco_ios", "vlan", vlan_number)
            
            # Return the device prompt
            return True

    if command == "show vlans":
        vlans = read_record("cisco_ios", "vlan")
        if vlans:
            return vlans
        else:
            return True
    return ""