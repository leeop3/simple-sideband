# src/networking/reticulum_manager.py
# FIXED: Correct interface imports for newer RNS versions

import RNS
import LXMF
import os
from pathlib import Path

class ReticulumManager:
    """Manages Reticulum network connection and identity"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = str(Path.home() / ".simple_sideband")
        
        os.makedirs(config_path, exist_ok=True)
        
        print("🔌 Initializing Reticulum...")
        
        # Initialize Reticulum
        self.rns = RNS.Reticulum(
            configdir=config_path,
            loglevel=RNS.LOG_VERBOSE
        )
        
        # Create or load our unique identity
        self.identity = self._load_or_create_identity(config_path)
        
        # Initialize LXMF router
        self.lxmf_router = LXMF.LXMRouter(
            identity=self.identity,
            storagepath=os.path.join(config_path, "lxmf")
        )
        
        print(f"✅ Reticulum ready! My address: {self.get_address_hex()}")
    
    def _load_or_create_identity(self, config_path):
        """Load existing identity or create a new one"""
        identity_file = os.path.join(config_path, "identity")
        
        if os.path.exists(identity_file):
            print("📦 Loading saved identity...")
            return RNS.Identity.from_file(identity_file)
        else:
            print("🆕 Creating new identity...")
            new_identity = RNS.Identity()
            new_identity.to_file(identity_file)
            return new_identity
    
    def get_address_hex(self):
        """Get our human-readable LXMF address"""
        return self.identity.hash.hex()
    
    def add_tcp_interface(self, host, port):
        """Connect to a Reticulum hub over internet (for testing)"""
        try:
            # ✅ FIXED: Try multiple import paths for TCP interface
            tcp_interface = None
            
            # Try newer RNS versions first
            try:
                from RNS.Transport import TCPClientInterface
                tcp_interface = TCPClientInterface
            except ImportError:
                pass
            
            # Try older path
            if tcp_interface is None:
                try:
                    from RNS.Interfaces.TCPInterface import TCPClientInterface
                    tcp_interface = TCPClientInterface
                except ImportError:
                    pass
            
            # Last resort: direct module import
            if tcp_interface is None:
                try:
                    import RNS.Interfaces.TCPInterface as tcp_module
                    tcp_interface = tcp_module.TCPClientInterface
                except (ImportError, AttributeError):
                    pass
            
            if tcp_interface is None:
                print("⚠️ TCP interface not available in this RNS version")
                print("💡 Local messaging will still work!")
                return False
            
            # Create and add the interface
            print(f"🌐 Connecting to {host}:{port}...")
            interface = tcp_interface(self.rns, host, port)
            self.rns.add_interface(interface)
            print("✅ TCP interface added!")
            return True
            
        except Exception as e:
            print(f"⚠️ Could not add TCP interface: {e}")
            print("💡 Local messaging will still work without internet hub!")
            return False
    
    def shutdown(self):
        """Cleanly shut down Reticulum"""
        print("🔌 Shutting down Reticulum...")
        self.rns.shutdown()