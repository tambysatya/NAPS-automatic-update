
from typing_extensions import assert_never
from .Types import NAPSManifest, VMStatus, VMMessage, Status, Ack, Idle, Pending, Failed
from fastapi import FastAPI, HTTPException, Request, Body, WebSocket, WebSocketDisconnect

class NAPSState:

    def __init__(self, manifest):
        self.manifest : NAPSManifest = manifest
        self.clients : dict [str, WebSocket] = {}
    
    async def connect (self, vm: str, ws : WebSocket):
        await ws.accept()
        self.clients[vm] = ws
    def disconnect (self, vm : str):
        self.clients.pop(vm, None)

    def is_name_allowed (self, name):
        return self.manifest.is_name_allowed(name)

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
    
    def initialize_update (self, expected):
        
        not_pending_vms = {vmname: config for vmname, config in self.manifest.vms.items() if not isinstance(config, Running)}
        if not_pending_vms != {}:
            raise BaseException (f"Some VMs are not available: {not_pending_vms}") #TODO exception class

        naps = Pending (
                    old = self.manifest.status.config,
                    new = expected.status.config
               )
        vms = {vm: Pending (old = status.config, new= expected.vms[vm].config) for vm,status in self.manifest.vms.items()}
        self.manifest = NAPSManifest (status=naps, vms=vms)

        return




        

