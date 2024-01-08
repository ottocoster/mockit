
async def handle_command(command: str, session) -> bool:
    if command.startswith("config paging"):
        return True
    return False