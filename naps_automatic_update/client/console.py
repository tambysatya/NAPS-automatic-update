import asyncio
from ..utils import NAPSManifest, Pending, Failed, Running, Status
import shlex

async def process_n (state):
    """ Generates a "FAILED" """
    status = state.status
    if isinstance (status, Pending):
        msg = Failed (old = status.old, new = status.new, reason = "Manual interruption")
        await state.send(Status(status=msg))
async def process_y (state):
    """ Generates a "Running" """
    status = state.status
    if isinstance (status, Pending):
        msg = Running (config = status.old)
        await state.send(Status(status = msg))       

    

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
                case ["y"]:
                    await process_y (state)
                case ["n"]:
                    await process_n (state)

        except (EOFError, KeyboardInterrupt):
            break
        except Exception as e:
            print (f"{e!r}")
            continue


