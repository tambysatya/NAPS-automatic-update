import asyncio
import websockets
import ssl
from ..utils import VMMessage, NAPSOrder, NAPSOrderAdapter, VMStatus, ConfigHash, nix_path_info, SwitchTo, Pending, Ack, Status, Commit
from ..utils import Running
from .console import admin_console
import subprocess

class VMState:
    def __init__(self, ws, config):

        self.ws = ws
        self.status = Running (config = config)

    async def send(self, message : VMMessage):
        await self.ws.send(message.model_dump_json())
    async def on_message(self, message : NAPSOrder):
        print(f"\ntype={message.type}")
        match message:
            case SwitchTo() as order :

                self.status = Pending (old = self.status.config, new = order.config)
                ans = Ack(order = order, status = self.status)
                await self.send(ans)

                print (f"SwitchTo: sending ans={ans}")

                # TODO Here should be the update script (backups, rebuild ,....)
                # ...
                await asyncio.sleep(5)
                # End of the update script
                # TODO: arm a watch dog with a nixos-rollback

                self.status = Running (config = order.config)
                await self.send(Status(status=self.status))

            case Commit() as order:
                ans = Ack(order = order, status = self.status)
                print (f"Commit: sending ans={ans}")
                self.send(ack)
                # TODO: Kill the watchdog
                pass
            case _:
                print ("NOTHING FOUND")

        pass
#TODO auto reconnect
async def server_main():
    ssl_context = ssl.create_default_context(cafile="certs/root_ca.crt")
    ssl_context.load_cert_chain(
        certfile="certs/test-client.local/test-client.local.crt",
        keyfile ="certs/test-client.local/test-client.local.key"
    )
    async with websockets.connect(
        "wss://localhost:8090/connect",
        ssl = ssl_context
    ) as ws:
        config = await ConfigHash.current()
        state = VMState(ws, config)
        await state.send(Status (status = state.status))

        async def receive(state):
            async for json in ws:
                message = NAPSOrderAdapter.validate_json(json)
                await state.on_message(message)

        await asyncio.gather (receive(state) , admin_console(state)) 
async def main ():
    await server_main ()

if __name__ == "__main__":
    asyncio.run(main())
