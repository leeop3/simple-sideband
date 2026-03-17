# src/utils/bt_wrapper.py
# Bridge Kotlin BluetoothService to Python RNS Interface

from RNS.Interfaces import Interface
from RNS import KISS
import time
import threading


class AndroidBTInterface(Interface):
    """RNS Interface that wraps Kotlin BluetoothService via PyJNIus"""
    
    BITRATE_GUESS = 64000  # Conservative guess for LoRa/BT link
    
    def __init__(self, owner, name, bt_service):
        super().__init__()
        self.owner = owner
        self.name = name
        self.bt_service = bt_service  # Kotlin BluetoothService via PyJNIus
        self.rxb = 0
        self.txb = 0
        self.online = False
        self.IN = True
        self.OUT = True
        self.FWD = False
        self.RPT = False
        self.bitrate = self.BITRATE_GUESS
        self.kiss_enc = KISS.KISSInterface.KISS_ENCODER
        self.kiss_dec = KISS.KISSInterface.KISS_DECODER
        
        # Start read thread
        self.read_thread = None
        self._read_running = False
        
    def attach(self, rns_instance):
        """Attach to RNS instance"""
        self.rns = rns_instance
        self.online = True
        self._start_read_loop()
        return True
        
    def _start_read_loop(self):
        """Start background thread to read from BT"""
        self._read_running = True
        
        def read_loop():
            while self._read_running and self.online:
                try:
                    # Read up to 4KB non-blocking
                    data = self.bt_service.read(4096)
                    if data and len(data) > 0:
                        # Convert Java byte[] to Python bytes
                        python_data = bytes(data)
                        self.rxb += len(python_data)
                        # Pass to RNS KISS decoder
                        self.data_received(python_data)
                    else:
                        # Nothing available - sleep briefly
                        time.sleep(0.01)
                except Exception as e:
                    print("BT read error: " + str(e))
                    time.sleep(0.1)
                    
        self.read_thread = threading.Thread(target=read_loop, daemon=True)
        self.read_thread.start()
        
    def data_received(self, data):
        """Process received KISS frames"""
        frames = self.kiss_dec.process(data)
        for frame in frames:
            if frame and len(frame) > 0:
                self.rns.inbound(frame, self)
                
    def process_outgoing(self, data):
        """Send data via Kotlin BT service"""
        if not self.online or not self.bt_service:
            return False
        try:
            # Encode as KISS frame
            kiss_frame = self.kiss_enc.process(data)
            if kiss_frame:
                # Convert Python bytes to Java byte[] via PyJNIus
                from jnius import cast, ByteArray
                java_bytes = cast("byte[]", ByteArray(kiss_frame))
                self.bt_service.write(java_bytes)
                self.txb += len(kiss_frame)
                return True
        except Exception as e:
            print("BT write error: " + str(e))
            self.online = False
        return False
        
    def shutdown(self):
        """Clean shutdown"""
        self._read_running = False
        self.online = False
        if self.bt_service:
            self.bt_service.disconnect()