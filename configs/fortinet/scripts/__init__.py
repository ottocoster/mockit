
async def handle_command(command: str, session) -> bool:
    if command == "get system status | grep Version":
        session.respond("Version: abc v7.")
        return True
    if command == "get system console":
        session.respond("output : standard")
        return True
    return False