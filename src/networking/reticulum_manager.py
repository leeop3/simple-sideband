# src/networking/reticulum_manager.py
import RNS
import LXMF
import os
from pathlib import Path
from kivy.utils import platform

class ReticulumManager:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.environ.get("RNS_DATA_DIR")
        
        if config_path is None:
            config_path = str(Path.home() / ".simple_sideband")
            
        os.makedirs(config_path, exist_ok=True)
        print(f"Initializing Reticulum with config: {config_path}")
        
        # FIX: Removed 'instance_name' which caused the crash
        # Most RNS versions only take configdir and loglevel
        self.rns = RNS.Reticulum(
            configdir=config_path, 
            loglevel=RNS.LOG_VERBOSE
        )
        
        self.identity = self._load_or_create_identity(config_path)
        self.lxmf_router = LXMF.LXMRouter(
            identity=self.identity, 
            storagepath=os.path.join(config_path, "lxmf")
        )
        print("Reticulum ready! My address: " + self.get_address_hex())
    
    def _load_or_create_identity(self, config_path):
        identity_file = os.path.join(config_path, "identity")
        if os.path.exists(identity_file):
            return RNS.Identity.from_file(identity_file)
        else:
            new_identity = RNS.Identity()
            new_identity.to_file(identity_file)
            return new_identity
    
    def get_address_hex(self):
        return self.identity.hash.hex()
    
    def add_tcp_interface(self, host, port):
        try:
            # Fix: Correct import for modern RNS
            from RNS.Interfaces.TCPInterface import TCPClientInterface
            interface = TCPClientInterface(self.rns, host, port)
            self.rns.add_interface(interface)
            return True
        except Exception as e:
            print("TCP fallback error: " + str(e))
            return False
    
    def shutdown(self):
        self.rns.shutdown()

def create_manager_with_tcp(host, port):
    manager = ReticulumManager()
    manager.add_tcp_interface(host, port)
    return manager