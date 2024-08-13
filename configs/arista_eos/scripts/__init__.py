
def handle_command(command: str):
    if command.startswith('terminal width '):
        return ("Width set to " + command[15])

    if command.startswith('terminal length 0'):
        return ("Pagination disabled")
    return ""