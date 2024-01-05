
async def handle_command(command: str, session) -> bool:
    if command.startswith('set cli screen-width '):
        session.respond("Screen width set to " + command[21])
        return True
    if command.startswith('set cli complete-on-space off'):
        session.respond("Disabling complete-on-space")
        return True
    if command.startswith('set cli screen-length '):
        session.respond("Screen length set to " + command[22])
        return True

    return False