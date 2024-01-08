
async def handle_command(command: str, session) -> bool:
    if command == 'screen-length 0 temporary':
        return True

    return False