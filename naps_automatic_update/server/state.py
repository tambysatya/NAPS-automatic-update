
from typing_extensions import assert_never
from ..utils import NAPSManifest, NAPSOrder, VMStatus, VMMessage, Status
from ..utils import Ack, Idle, Pending, Failed, Committing, Running, SwitchTo, Commit
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
    def update_vm_status (self, vm : str, status : VMStatus):
        self.current_manifest.vms[vm] = status

    async def on_pending_phase_status (self, vm : str, status : VMStatus):
        match (status):
            case Failed ():
                print (f"Error: {vm} failed to update")
                self.switch_to_failed(reason = f"{vm} failed to update")
            case Running():
                current = status.config
                expected = self.expected_manifest.vms[vm].config
                if current != expected:
                    print (f"Error: {vm} is running an unexpected configuration. Current={current} Expected={expected}")
                    order = SwitchTo (config=expected)
                    await self.send_order(vm, order)
                self.update_vm_status(vm, status)

    async def on_pending_phase (self, vm : str, message : VMMessage):
        status = message.status 
        await self.on_pending_phase_status(vm, status)
        if self.current_manifest.vms == self.expected_manifest.vms:
            await self.switch_to_commit()


    async def on_commit_phase_status (self, vm : str, status : VMStatus):
        pass
    async def on_commit_phase_ack (self, vm : str,  order : NAPSOrder, status : VMStatus):
        pass
    async def on_commit_phase(self, vm, message : VMMessage):
        pass

    async def on_failed_phase_status (self, vm : str, status : VMStatus):
        pass
    async def on_failed_phase_ack(self, vm : str, order : NAPSOrder, status : VMStatus):
        pass
    async def on_failed_phase(self, vm, message : VMMessage):
        pass

    async def on_running_phase_status (self, vm : str, status : VMStatus):
        current = status.config
        assumed = self.current_manifest.vms[vm].config
        if current != assumed:
            print (f"Warning: unexpected config from {vm}: current={current} assumed={assumed}. Updating current state")
            self.update_vm_status(vm, status)
    async def on_running_phase_ack(self, vm : str, order : NAPSOrder, status : VMStatus):
        pass
    async def on_running_phase(self, vm, message : VMMessage):
        await self.on_running_phase_status(vm, message.status)




    async def process_message (self, vm, message : VMMessage):
        print (message)
        current_status = self.current_manifest.status
        if isinstance (message, Ack):
            order = message.order
            if (not (vm in self.awaiting_orders)) or (self.awaiting_orders[vm] != order):
                await self.send(vm, order) # resending the order
                raise BaseException (f"Received an acknowledgment for a non-awaited order: {order}")
            self.awaiting_orders.pop(vm, None)
        match current_status:
            case Pending():
                await self.on_pending_phase (vm, message)
            case Failed():
                await self.on_failed_phase (vm, message) 
            case Committing():
                await self.on_commit_phase (vm, message) 
            case Running():
                await self.on_running_phase (vm, message)
            case _ as unreachable:
                assert_never(unreachable)


    async def send_order (self, vm: str, order : NAPSOrder):
        if vm in self.awaiting_orders:
            raise BaseException (f"send: unable to send order: {order}. Reason: already awaiting order: {self.awaiting_orders}")
        self.awaiting_orders[vm] = order
        await self.clients[vm].send_text(order.model_dump_json()) 
    

    async def switch_to_pending(self):
        """ Sets the current to "Pending" """
        current, expected = self.current_manifest, self.expected_manifest
        modified_vms = {vm: conf for vm,conf in expected.vms.items() if not (vm in current.vms) or (conf != current.vms[vm])}

        # check if all the vms are connected
        not_connected_vms = [vm for vm in modified_vms if not vm in self.clients]
        if not_connected_vms != []:
            raise BaseException (f"Some vms are not connected: f{not_connected_vms}")
        
        # check if there is no awaiting order
        if self.awaiting_orders != {}:
            raise BaseException (f"Unable to deploy: already awaiting orders {self.awaiting_orders}")

        self.expected_manifest = expected
        self.current_manifest.status = Pending (old = current.status.config, new = expected.status.config)


        for vm in modified_vms:
            order = SwitchTo (config=expected.vms[vm].config)
            await self.send_order(vm, order)

        # TODO arm the watchdog

    def switch_to_failed (self, reason):
        """ Sets the current to "Failed" """
        self.current_manifest.status = Failed (old = self.current_manifest.status.config, new = self.expected_manifest.status.config)
    async def switch_to_commit (self):
        print ("Switching to commit")
        if self.awaiting_orders != {}:
            raise BaseException (f"Cannot switch to commit: awaiting orders {self.awaiting_orders}")
        self.current_manifest.status = Committing(config = self.current_manifest.status.new)
        for vm, expected in self.expected_manifest.vms.items():
            order = Commit (config=expected.config)
            await self.send_order(vm, order)


    async def initialize_update (self, expected : NAPSManifest):

        if not isinstance(self.current_manifest.status, Running):
            raise BaseException (f"An update is already ongoing")



        # check if all the VMs are Running properly
        not_running_vms = {vmname: config for vmname, config in self.current_manifest.vms.items() if not isinstance(config, Running)}
        if not_running_vms != {}:
            raise BaseException (f"Some VMs are not available: {not_running_vms}") #TODO exception class


        await self.switch_to_pending()


            


        

