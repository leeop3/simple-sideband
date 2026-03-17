# src/networking/lxmf_client.py
import LXMF
import RNS

class Message:
    def __init__(self, timestamp, source_hash, content, is_image=False):
        self.timestamp = timestamp
        self.source_hash = source_hash
        self.content = content
        self.is_image = is_image

class LXMFClient:
    def __init__(self, lxmf_router):
        self.router = lxmf_router
        self.destination = None
        self.on_message_received = None
        self.router.register_delivery_callback(self._handle_incoming)
    
    def create_destination(self, app_name="SimpleSideband"):
        try:
            print("Creating destination for: " + app_name)
            self.destination = self.router.register_delivery_destination(
                app_name=app_name,
                app_data=b"v1.0"
            )
            if self.destination:
                address = self.destination.hash.hex()
                print("Destination created! Address: " + address)
                return address
            else:
                print("Failed to create destination")
                return None
        except Exception as e:
            print("Error creating destination: " + str(e))
            return self.router.identity.hash.hex()
    
    def send_text(self, destination_address, text):
        if not self.destination:
            print("Error: Destination not created yet!")
            return False
        if len(destination_address) != 32:
            print("Invalid destination address length")
            return False
        try:
            print("Sending to " + destination_address[:8] + "...")
            target_bytes = bytes.fromhex(destination_address)
            message = LXMF.LXMessage(
                destination=self.destination,
                target=target_bytes,
                content=text.encode("utf-8"),
                fields=LXMF.LXMessage.TEXT_FIELD
            )
            message.register_delivery_callback(self._on_delivery_status)
            self.router.handle_outbound(message)
            return True
        except Exception as e:
            print("Error sending message: " + str(e))
            return False
    
    def _handle_incoming(self, message):
        try:
            if isinstance(message.content, bytes):
                text = message.content.decode("utf-8")
            else:
                text = str(message.content)
            msg = Message(
                timestamp=message.timestamp,
                source_hash=message.source_hash.hex()[:8],
                content=text,
                is_image=text.startswith("IMAGE:")
            )
            if self.on_message_received:
                print("Received from " + msg.source_hash)
                self.on_message_received(msg)
        except Exception as e:
            print("Error processing message: " + str(e))
    
    def _on_delivery_status(self, message, status):
        if status == LXMF.LXMessage.DELIVERED:
            print("Message delivered!")
        elif status == LXMF.LXMessage.FAILED:
            print("Message delivery failed")
        elif status == LXMF.LXMessage.PENDING:
            print("Message pending delivery...")
    
    def send_image(self, destination_address, image_path):
        if not self.destination:
            print("Error: Destination not created yet!")
            return False
        from utils.image_handler import compress_and_encode_image
        encoded_data, metadata = compress_and_encode_image(image_path)
        if not encoded_data:
            print("Failed to process image")
            return False
        message_content = "IMAGE:" + metadata["filename"] + ":" + encoded_data
        if len(destination_address) != 32:
            print("Invalid destination address length")
            return False
        try:
            print("Sending image...")
            target_bytes = bytes.fromhex(destination_address)
            message = LXMF.LXMessage(
                destination=self.destination,
                target=target_bytes,
                content=message_content.encode("utf-8"),
                fields=LXMF.LXMessage.TEXT_FIELD
            )
            message.register_delivery_callback(self._on_delivery_status)
            self.router.handle_outbound(message)
            return True
        except Exception as e:
            print("Error sending image: " + str(e))
            return False
    
    def set_message_callback(self, callback_function):
        self.on_message_received = callback_function