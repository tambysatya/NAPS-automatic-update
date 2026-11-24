
from typing_extensions import assert_never
from .Types import NAPSManifest, VMStatus, VMMessage

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
    
