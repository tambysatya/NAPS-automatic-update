
from pydantic import BaseModel, Field, TypeAdapter
from typing import Literal, Annotated
from typing_extensions import assert_never


class ConfigHash (BaseModel):
    drv: str
    out: str

# NAPS Orders: commands sent by the orchestrator

class Idle (BaseModel):
    """ Nothing to do"""
    type: Literal["idle"] = "idle"

class SwitchTo(BaseModel):
    """ Rebuild and switch to the specified configuration """
    type: Literal["switch-to"] = "switch-to"
    config: ConfigHash # This is the derivation of the virtual-machine system

class Commit (BaseModel):
    """ Acknowledge the update """
    type: Literal["commit"] = "commit"
    config: ConfigHash # This is the derivation of the infrastructure version

NAPSOrder = Annotated[Idle | SwitchTo | Commit, Field(discriminator="type")]

# Status
class Running (BaseModel):
    """ The specified configuration is currently running """
    type: Literal["running"] = "running"
    config: ConfigHash

class Pending (BaseModel):
    """ The switch between the old and new configuration has been done,
        but we are waiting for a confirmation """
    type: Literal["pending"] = "pending"
    old : ConfigHash
    new : ConfigHash

class Failed (BaseModel):
    """ The switch between the old and new configuration has failed """
    type: Literal["failed"] = "failed"
    old : ConfigHash
    new : ConfigHash



VMStatus = Annotated[Running | Pending | Failed, Field(discriminator="type")]
NAPSStatus = Annotated[Running | Pending | Failed, Field(discriminator="type")]

# Messages sent by the VMs

class Acknowledge (BaseModel):
    type: Literal ["ack"] = "ack"
    order: NAPSOrder

class Status (BaseModel):
    type: Literal ["status"] = "status"
    status: VMStatus

VMMessage = Annotated [Acknowledge | Status, Field(discriminator="type")]


class NAPSManifest (BaseModel):
    status: NAPSStatus
    vms: dict[str, VMStatus] # perVM status

    def is_name_allowed (self, name):
        return name in self.vms


class NAPSState:

        manifest : NAPSManifest 

        def __init__(self, manifest):
            self.manifest = manifest

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
                case Acknowledge():
                    pass
                case Status():
                    pass
                case _ as unreachable:
                    assert_never(unreachable)
        
        def initialize_update (self, expected):
            
            not_pending_vms = {vmname: config for vmname, config in self.manifest.vms.items() if not isinstance(config, Running)}
            if not_pending_vms != {}:
                raise BaseException (f"Some VMs are not available: {not_pending_vms}")

            naps = Pending (
                        old = self.manifest.status.config,
                        new = expected.status.config
                   )
            vms = {vm: Pending (old = status.config, new= expected.vms[vm].config) for vm,status in self.manifest.vms.items()}
            self.manifest = NAPSManifest (status=naps, vms=vms)

            return




        



def test():
    status = Running(config=ConfigHash(drv="naps.drv", out="naps.out"))
    vms = {
        "vmA": Running (config=ConfigHash(drv="a.drv", out="a.out")),
        "vmB": Running (config=ConfigHash(drv="b.drv", out="b.out"))
    }
    napsA = NAPSManifest (status=status, vms=vms)

    vms2 = {
        "vmA": Running (config=ConfigHash(drv="a'.drv", out="a'.out")),
        "vmB": Running (config=ConfigHash(drv="b'.drv", out="b'.out"))
    }
    napsB = NAPSManifest (status=status, vms=vms2)
    return napsA, napsB
    
