import asyncio
import websockets
import ssl
from ..utils import VMMessage, NAPSOrderAdapter, VMStatus, ConfigHash, nix_path_info 
from ..utils import Running
from .console import admin_console
import subprocess

class VMState:
    def __init__(self, config):


        self.status = Running (config = config)
        print (self.status.model_dump_json())
        pass
    async def on_message(self, message : VMMessage):
        print(f"\n[SERVER] {message}")
        pass

async def server_main(state):
    ssl_context = ssl.create_default_context(cafile="certs/root_ca.crt")
    ssl_context.load_cert_chain(
        certfile="certs/test-client.local/test-client.local.crt",
        keyfile ="certs/test-client.local/test-client.local.key"
    )
    async with websockets.connect(
        "wss://localhost:8090/connect",
        ssl = ssl_context
    ) as ws:
        async def receive(state):
            for json in ws:
                print(f"\n[SERVER] {json}")
                message = NAPSOrderAdapter.validate_json(json)
            await state.on_message(message)

        await asyncio.gather (receive(state) , admin_console(state)) 
async def main ():
    conf = await ConfigHash.current()
    print(conf)

    state = VMState(conf)
    print(state.status)
    await server_main (state)

if __name__ == "__main__":
    asyncio.run(main())
