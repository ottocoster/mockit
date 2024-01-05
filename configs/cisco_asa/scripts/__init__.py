
async def handle_command(command: str, session) -> bool:
    if command.startswith('login'):
        session.respond("login")
        return True
    return False