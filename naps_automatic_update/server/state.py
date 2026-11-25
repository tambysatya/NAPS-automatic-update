
from typing_extensions import assert_never
from ..utils import NAPSManifest, NAPSOrder, VMStatus, VMMessage, Status
from ..utils import Ack, Idle, Pending, Failed, Running, SwitchTo
from fastapi import FastAPI, HTTPException, Request, Body, WebSocket, WebSocketDisconnect

class NAPSState:

    def __init__(self, manifest):
        self.current_manifest : NAPSManifest = manifest.model_copy(deep=True)
        self.expected_manifest : NAPSManifest = manifest.model_copy(deep=True)
        self.clients : dict [str, WebSocket] = {}
        self.awaiting_orders : dict [str, NAPSOrder] = {}
    
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

    def process_status (self, vm, status : VMStatus):
        self.current_manifest.vms[vm] = status
        match (status):
            case Running():
                pass
            case Pending():
                pass
            case Failed():
                pass
            case _ as unreachable:
                assert_never(unreachable)

    def process_message (self, vm, message : VMMessage):
        print (message)
        match (message):
            case Ack():
                order = message.order
                if (not (vm in self.awaiting_orders)) or (self.awaiting_orders[vm] != order):
                    raise BaseException (f"Received an acknowledgment for a non-awaited order: {order}")
                self.awaiting_orders.pop(vm, None)
                self.process_status (vm, message.status)
            case Status():
                self.process_status(vm, message.status)
            case _ as unreachable:
                assert_never(unreachable)

    async def send (self, vm: str, order : NAPSOrder):
       await self.clients[vm].send_text(order.model_dump_json()) 
    
    async def initialize_update (self, expected : NAPSManifest):

        if not isinstance(self.current_manifest.status, Running):
            raise BaseException (f"An update is already ongoing")



        # check if all the VMs are Running properly
        not_running_vms = {vmname: config for vmname, config in self.current_manifest.vms.items() if not isinstance(config, Running)}
        if not_running_vms != {}:
            raise BaseException (f"Some VMs are not available: {not_running_vms}") #TODO exception class


        modified_vms = {vm: conf for vm,conf in expected.vms.items() if not (vm in self.current_manifest.vms) or (conf != self.current_manifest.vms[vm])}

        # check if all the vms are connected
        not_connected_vms = [vm for vm in modified_vms if not vm in self.clients]
        if not_connected_vms != []:
            raise BaseException (f"Some vms are not connected: f{not_connected_vms}")
        
        # check if there is no awaiting order
        if self.awaiting_orders != {}:
            raise BaseException (f"Unable to deploy: already awaiting orders {self.awaiting_orders}")

        self.expected_manifest = expected
        self.current_manifest.status = Pending (old = self.current_manifest.status.config, new = expected.status.config)


        for vm in modified_vms:
            order = SwitchTo (config=expected.vms[vm].config)
            self.awaiting_orders[vm] = order
            await self.send(vm, order)

        # TODO arm the watchdog
            


        

