
import asyncio
from .Types import NAPSManifest
import shlex

init_manifest = NAPSManifest.parse_file("examples/infra.json")
new_manifest = NAPSManifest.parse_file("examples/infra2.json")

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
                case ["update"]:
                    state.initialize_update(new_manifest)
                    print (state.expected_manifest)

        except (EOFError, KeyboardInterrupt):
            break
        except BaseException as e:
            print (f"{e!r}")
            continue
