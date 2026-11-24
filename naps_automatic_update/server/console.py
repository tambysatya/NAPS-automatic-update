import asyncio
import shlex


async def admin_console (state):
    while True:
        try:
            line = await asyncio.to_thread(input, "naps> ")
            args = shlex.split(line)
            if not args:
                continue
            match args:
                case ["help"]:
                    print ("Need help ?")

        except (EOFError, KeyboardInterrupt):
            break
