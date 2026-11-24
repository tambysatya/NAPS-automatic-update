
from pydantic import BaseModel, Field, TypeAdapter
from typing import Ltteral, Annotated


class ConfigHash (BaseModel):
    drv: str
    out: str

# NAPS Orders: commands sent by the orchestrator

class Idle (BaseModel):
    """ Nothing to do"""
    type: Literal["idle"]

class SwitchTo(BaseModel):
    """ Rebuild and switch to the specified configuration """
    type: Literal["switch-to"]
    config: ConfigHash # This is the derivation of the virtual-machine system

class Commit (BaseModel):
    """ Acknowledge the update """
    type: Literal["commit"] 
    config: ConfigHash # This is the derivation of the infrastructure version

NAPSOrder = Annotated[Idle | SwitchTo | Commit, Field(discriminator="type")]

# VMStatus
class Running (BaseModel):
    """ The specified configuration is currently running """
    type: Literal["running"]
    config: ConfigHash

class Pending (BaseModel):
    """ The switch between the old and new configuration has been done,
        but we are waiting for a confirmation """
    type: Literal["pending"]
    old : ConfigHash
    new : ConfigHash

class Failed (BaseModel):
    """ The switch between the old and new configuration has failed """
    type: Literal["failed"]
    old : ConfigHash
    new : ConfigHash


VMStatus = Annotated[Running | Pending | Failed, Field(discriminator="type")]



class VMStatus (Enum):
    RUNNING = "running" # The machine is running properly
    REBUILD = "rebuilding" # The machine is updating: we are waiting for a confirmation
    SUCCESS = "success" # The machine has been successfuly updated and waits for our confirmation (watchdog still armed)
    FAILED  = "failed"  # The machine failed its update and is rolling back

class NAPSStatus (Enum):
    RUNNING = "running" # Everything is running properly
    PENDING = "pending" # Some machine is updating: we are waiting for a confirmation
    FAILED  = "failed"  # The last update has failed

class NAPSOrder (Enum):
    IDLE = "idle" # Everything is OK, nothing to do
    REBUILD = "rebuild" # Run a nixos-rebuild switch and arm watchdog
    ROLLBACK = "rollback" # Run a nixos-rebuild switch and arm watchdog
    COMMIT = "commit"  # All the updates have been confirmed: commit the changes and disarm watchdog



class VMState (BaseModel):
        drv : str
        out : str
        status : VMStatus

class NAPSState (BaseModel):
        version : int
        vms : dict[str, VMState] # perVM status
        status : NAPSStatus

        def is_name_allowed (self, name):
            return name in self.vms

        def process_ping (self, name, status):
            pass

        



def test():
    vms = {
        "vmA": VMState (drv="derivation1.drv", out="path2.out", status=VMStatus.RUNNING),
        "vmB": VMState (drv="derivation2.drv", out="path2.out",  status=VMStatus.RUNNING)
    }
    return NAPSState (version=0, vms=vms,status=NAPSStatus.RUNNING)
    
