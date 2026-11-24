
from typing_extensions import assert_never
from ..utils import NAPSManifest, NAPSOrder, VMStatus, VMMessage, Status
from ..utils import Ack, Idle, Pending, Failed, Running, SwitchTo
from fastapi import FastAPI, HTTPException, Request, Body, WebSocket, WebSocketDisconnect

class NAPSState:

    def __init__(self, manifest):
        self.current_manifest : NAPSManifest = manifest
        self.expected_manifest : NAPSManifest = manifest
        self.clients : dict [str, WebSocket] = {}
    
    async def connect (self, vm: str, ws : WebSocket):
        await ws.accept()
        self.clients[vm] = ws

        not_connected_vms = [client for client in self.expected_manifest.vms if not (client in self.clients)]
        if not_connected_vms == []:
            print ("All clients are now connected")


    def disconnect (self, vm : str):
        self.clients.pop(vm, None)

    def is_name_allowed (self, name):
        return self.expected_manifest.is_name_allowed(name)

    def process_status (self, vmname, status : VMStatus):
        match (status):
            case Idle():
                pass
            case Pending():
                pass
            case Failed():
                pass
            case _ as unreachable:
                assert_never(unreachable)

    def process_message (self, vmname, message : VMMessage):
        match (message):
            case Ack():
                pass
            case Status():
                pass
            case _ as unreachable:
                assert_never(unreachable)

    async def send (self, vm: str, order : NAPSOrder):
       await self.clients[vm].send_text(order.model_dump_json()) 
    
    async def initialize_update (self, expected : NAPSManifest):
        
        # check if all the VMs are Running properly
        not_running_vms = {vmname: config for vmname, config in self.current_manifest.vms.items() if not isinstance(config, Running)}
        if not_running_vms != {}:
            raise BaseException (f"Some VMs are not available: {not_running_vms}") #TODO exception class

        # check if all the vms are connected
        not_connected_vms = [vm for vm in self.expected_manifest.vms if not vm in self.clients]
        if not_connected_vms != []:
            raise BaseException (f"Some vms are not connected: f{not_connected_vms}")
            return
        

        self.expected_manifest = expected
        self.current_manifest.status = Pending (old = self.current_manifest.status.config, new = expected.status.config)


        print (f"expected={expected}")
        for vm in expected.vms:
            order = SwitchTo (config=expected.vms[vm].config)
            await self.send(vm, order)
            


        

