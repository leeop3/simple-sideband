# src/networking/reticulum_manager.py
# Clean version with RNode BLE support + proper structure

import RNS
import LXMF
import os
from pathlib import Path


class ReticulumManager:
    def __init__(self, config_path=None):
        # If no path provided, check if environment variable was set by main.py
        if config_path is None:
            config_path = os.environ.get("RNS_DATA_DIR")
        
        # Fallback for desktop/default
        if config_path is None:
            config_path = str(Path.home() / ".simple_sideband")
            
        os.makedirs(config_path, exist_ok=True)
        print("Initializing Reticulum with config: " + config_path)
        
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
    
    def add_rnode_ble_interface(self, device_name=None, device_address=None):
        """Add RNode over Bluetooth LE (Android)"""
        try:
            from RNS.Interfaces import BLEInterface
            print("Adding RNode BLE interface...")
            
            # Try with device name first (more reliable on Android)
            if device_name:
                interface = BLEInterface(self.rns, device_name=device_name)
            elif device_address:
                interface = BLEInterface(self.rns, device_address=device_address)
            else:
                # Auto-discover mode
                interface = BLEInterface(self.rns)
            
            self.rns.add_interface(interface)
            print("✅ RNode BLE interface added!")
            return True
            
        except ImportError:
            print("⚠️ BLEInterface not available in this RNS version")
            return False
        except Exception as e:
            print("⚠️ Could not add RNode BLE: " + str(e))
            print("💡 Make sure: 1) RNode is paired, 2) Location permission granted")
            return False
    
    def get_interface_status(self):
        """Return status of all interfaces for debugging"""
        status = []
        for iface in self.rns.get_interfaces():
            status.append({
                "name": getattr(iface, "name", "unknown"),
                "type": type(iface).__name__,
                "online": getattr(iface, "online", False)
            })
        return status
    
    def shutdown(self):
        print("Shutting down Reticulum...")
        self.rns.shutdown()


# ============= MODULE-LEVEL HELPER FUNCTIONS =============

def create_manager_with_tcp(host, port):
    """
    Helper function to create manager with TCP interface
    Expected by main.py
    """
    manager = ReticulumManager()
    manager.add_tcp_interface(host, port)
    return manager