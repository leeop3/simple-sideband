# src/networking/reticulum_manager.py
import RNS
import LXMF
import os
from pathlib import Path

class ReticulumManager:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = str(Path.home() / ".simple_sideband")
        
        os.makedirs(config_path, exist_ok=True)
        
        print("Initializing Reticulum...")
        
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
            print("Loading saved identity...")
            return RNS.Identity.from_file(identity_file)
        else:
            print("Creating new identity...")
            new_identity = RNS.Identity()
            new_identity.to_file(identity_file)
            return new_identity
    
    def get_address_hex(self):
        return self.identity.hash.hex()
    
    def add_tcp_interface(self, host, port):
        try:
            from RNS.Transport import TCPClientInterface
            print("Connecting to " + host + ":" + str(port) + "...")
            interface = TCPClientInterface(self.rns, host, port)
            self.rns.add_interface(interface)
            print("TCP interface added!")
            return True
        except Exception as e:
            print("Could not add TCP interface: " + str(e))
            return False
    
    def shutdown(self):
        print("Shutting down Reticulum...")
        self.rns.shutdown()
