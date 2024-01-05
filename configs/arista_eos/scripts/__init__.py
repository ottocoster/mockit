
async def handle_command(command: str, session) -> bool:
    if command.startswith('terminal width '):
        session.respond("Width set to " + command[15])
        return True

    if command.startswith('terminal length 0'):
        session.respond("Pagination disabled")
        return True
    return False