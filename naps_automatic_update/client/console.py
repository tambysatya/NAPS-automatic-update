import asyncio
from ..utils import NAPSManifest
import shlex

async def admin_console (state):
    while True:
        try:
            line = await asyncio.to_thread(input, "naps-client> ")
            args = shlex.split(line)
            if not args:
                continue
            match args:
                case ["help"]:
                    print ("Need help ?")

        except (EOFError, KeyboardInterrupt):
            break
        except Exception as e:
            print (f"{e!r}")
            continue


