# networking/lxmf_client.py
import LXMF
import RNS
import time


class Message:
    def __init__(self, timestamp, source_hash, content, is_image=False):
        self.timestamp = timestamp
        self.source_hash = source_hash  # full hex string
        self.content = content
        self.is_image = is_image


class LXMFClient:
    def __init__(self, lxmf_router):
        self.router = lxmf_router
        self.destination = None
        self.on_message_received = None
        # Register delivery callback immediately so messages arriving before
        # create_destination() is called are still queued by the router
        self.router.register_delivery_callback(self._handle_incoming)

    def create_destination(self, app_name="SimpleSideband"):
        try:
            print("Creating destination for: " + app_name)
            # FIX: correct method is register_delivery_identity(), not
            # register_delivery_destination() which does not exist in LXMF
            self.destination = self.router.register_delivery_identity(
                self.router.identity,
                display_name=app_name
            )
            if self.destination:
                address = RNS.hexrep(self.destination.hash, delimit=False)
                print("Destination created! Address: " + address)
                return address
            else:
                print("Failed to create destination")
                return None
        except Exception as e:
            print("Error creating destination: " + str(e))
            # Fallback: return identity hash so the UI still has something to show
            return RNS.hexrep(self.router.identity.hash, delimit=False)

    def send_text(self, destination_address, text):
        if not self.destination:
            print("Error: Destination not created yet!")
            return False
        if len(destination_address) != 32:
            print("Invalid destination address (expected 32 hex chars, got "
                  + str(len(destination_address)) + ")")
            return False
        try:
            print("Sending to " + destination_address[:8] + "...")
            # FIX: LXMessage positional args are (destination, source, title, content)
            # 'destination' here is a Destination object resolved from the hash,
            # 'source' is our local delivery destination
            dest_hash = bytes.fromhex(destination_address)
            message = LXMF.LXMessage(
                RNS.Destination.recall(dest_hash),  # resolved remote destination
                self.destination,                    # our source
                "",                                  # title
                text,                                # content (str)
                desired_method=LXMF.LXMessage.OPPORTUNISTIC
            )
            message.register_delivery_callback(self._on_delivery_status)
            self.router.handle_outbound(message)
            return True
        except Exception as e:
            print("Error sending message: " + str(e))
            return False

    def send_image(self, destination_address, image_path):
        if not self.destination:
            print("Error: Destination not created yet!")
            return False
        if len(destination_address) != 32:
            print("Invalid destination address (expected 32 hex chars, got "
                  + str(len(destination_address)) + ")")
            return False
        try:
            from utils.image_handler import compress_and_encode_image
            encoded_data, metadata = compress_and_encode_image(image_path)
            if not encoded_data:
                print("Failed to process image")
                return False

            # FIX: use lowercase "image:" prefix to match main.py's _add_incoming()
            # which checks message.is_image and splits on "image:<filename>:<data>"
            message_content = "image:" + metadata["filename"] + ":" + encoded_data

            print("Sending image " + metadata["filename"] + "...")
            dest_hash = bytes.fromhex(destination_address)
            message = LXMF.LXMessage(
                RNS.Destination.recall(dest_hash),
                self.destination,
                "",
                message_content,
                desired_method=LXMF.LXMessage.OPPORTUNISTIC
            )
            message.register_delivery_callback(self._on_delivery_status)
            self.router.handle_outbound(message)
            return True
        except Exception as e:
            print("Error sending image: " + str(e))
            return False

    def set_message_callback(self, callback_function):
        self.on_message_received = callback_function

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _handle_incoming(self, message):
        try:
            if isinstance(message.content, bytes):
                text = message.content.decode("utf-8")
            else:
                text = str(message.content)

            # FIX: keep full source hash (not truncated to 8 chars) so the
            # address can be reused to reply; main.py truncates for display itself
            source_hash = RNS.hexrep(message.source_hash, delimit=False)

            timestamp = message.timestamp if message.timestamp else time.time()

            # FIX: normalise prefix to lowercase to match main.py expectation
            text_lower = text.lower()
            is_image = text_lower.startswith("image:")
            if is_image and not text.startswith("image:"):
                # Ensure consistent casing for the split in _add_incoming()
                text = "image:" + text[len("image:"):]

            msg = Message(
                timestamp=timestamp,
                source_hash=source_hash,
                content=text,
                is_image=is_image
            )

            if self.on_message_received:
                print("Received from " + source_hash[:8] + "...")
                self.on_message_received(msg)
            else:
                print("Received message but no callback set")
        except Exception as e:
            print("Error processing message: " + str(e))

    def _on_delivery_status(self, message, status):
        if status == LXMF.LXMessage.DELIVERED:
            print("Message delivered!")
        elif status == LXMF.LXMessage.FAILED:
            print("Message delivery failed")
        elif status == LXMF.LXMessage.PENDING:
            print("Message pending delivery...")
