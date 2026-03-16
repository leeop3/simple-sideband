# src/networking/reticulum_manager.py
# FIXED: Clean version with RNode support

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
    
    def add_rnode_serial_interface(self, port, baudrate=9600):
        """Add RNode over serial (USB)"""
        try:
            from RNS.Interfaces import SerialInterface
            print("Adding RNode serial interface on " + port + "...")
            interface = SerialInterface(self.rns, port=port, baudrate=baudrate)
            self.rns.add_interface(interface)
            print("RNode serial interface added!")
            return True
        except Exception as e:
            print("Could not add RNode serial: " + str(e))
            return False
    
    def add_rnode_ble_interface(self, device_address=None):
        """Add RNode over Bluetooth LE (Android)"""
        try:
            from RNS.Interfaces import BLEInterface
            print("Adding RNode BLE interface...")
            interface = BLEInterface(self.rns, device_address=device_address)
            self.rns.add_interface(interface)
            print("RNode BLE interface added!")
            return True
        except Exception as e:
            print("Could not add RNode BLE: " + str(e))
            return False
    
    def scan_for_rnode_ble_devices(self):
        """Scan for nearby RNode BLE devices"""
        try:
            import bluetooth
            print("Scanning for BLE devices...")
            nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True)
            rnode_devices = []
            for addr, name in nearby_devices:
                if "RNode" in name or "reticulum" in name.lower():
                    rnode_devices.append((addr, name))
                    print("Found RNode: " + name + " (" + addr + ")")
            return rnode_devices
        except Exception as e:
            print("BLE scan error: " + str(e))
            return []
    
    def shutdown(self):
        print("Shutting down Reticulum...")
        self.rns.shutdown()
