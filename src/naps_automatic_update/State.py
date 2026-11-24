
from pydantic import BaseModel, Field, TypeAdapter
from typing import Literal, Annotated


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


class NAPSState (BaseModel):
        status : NAPSStatus
        vms : dict[str, VMStatus] # perVM status

        def is_name_allowed (self, name):
            return name in self.vms

        def process_ping (self, name, status):
            pass

        



def test():
    status = Running(config=ConfigHash(drv="naps.drv", out="naps.out"))
    vms = {
        "vmA": Running (config=ConfigHash(drv="a.drv", out="a.out")),
        "vmB": Running (config=ConfigHash(drv="a.drv", out="a.out"))
    }
    return NAPSState (status=status, vms=vms)
    
