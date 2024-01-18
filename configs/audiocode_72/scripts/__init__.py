
async def handle_command(command: str, session) -> bool:
    if command == "config system":
        session.set_prompt(")#")
        return True
    return False