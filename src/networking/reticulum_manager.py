# src/networking/reticulum_manager.py
import RNS
import LXMF
import os
from pathlib import Path

class ReticulumManager:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.environ.get("RNS_DATA_DIR")
        if config_path is None:
            config_path = str(Path.home() / ".simple_sideband")
            
        os.makedirs(config_path, exist_ok=True)
        
        # FIX 1: Removed 'instance_name' which was causing the crash
        self.rns = RNS.Reticulum(configdir=config_path, loglevel=RNS.LOG_VERBOSE)
        self.identity = self._load_or_create_identity(config_path)
        
        lxmf_path = os.path.join(config_path, "lxmf")
        os.makedirs(lxmf_path, exist_ok=True)
        self.lxmf_router = LXMF.LXMRouter(identity=self.identity, storagepath=lxmf_path)

    def _load_or_create_identity(self, config_path):
        identity_file = os.path.join(config_path, "identity")
        if os.path.exists(identity_file):
            return RNS.Identity.from_file(identity_file)
        new_id = RNS.Identity()
        new_id.to_file(identity_file)
        return new_id

    def get_address_hex(self):
        return self.identity.hash.hex()

    def add_tcp_interface(self, host, port):
        try:
            # FIX 2: Modern Reticulum import and explicit naming
            from RNS.Interfaces.TCPInterface import TCPClientInterface
            interface = TCPClientInterface(
                self.rns, 
                name="TCP Interface", 
                target_host=host, 
                target_port=port
            )
            self.rns.add_interface(interface)
            return True
        except Exception as e:
            print(f"TCP Interface error: {str(e)}") # Fixed: string conversion
            return False

    def shutdown(self):
        self.rns.shutdown()