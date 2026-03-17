# src/main.py - SimpleSideband Chat App
import os
import tempfile
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.utils import platform

# --- 1. ANDROID PATH FIXES (Must happen BEFORE importing RNS) ---
if platform == 'android':
    try:
        from android.storage import app_storage_path
        settings_path = app_storage_path()
        # Fix Kivy Icon Permission Error
        os.environ['KIVY_HOME'] = os.path.join(settings_path, '.kivy')
        # Fix Reticulum Permission Error
        os.environ["RNS_DATA_DIR"] = os.path.join(settings_path, ".reticulum")
        os.makedirs(os.environ["RNS_DATA_DIR"], exist_ok=True)
        os.makedirs(os.environ['KIVY_HOME'], exist_ok=True)
    except Exception as e:
        print(f"Path setup failed: {e}")

# Now safe to import networking
from networking.reticulum_manager import ReticulumManager
from networking.lxmf_client import LXMFClient, Message
from utils.image_handler import decode_and_save_image

# ... [ChatBubble and ImageBubble classes remain the same as your version] ...

class ChatBubble(BoxLayout):
    def __init__(self, text, is_sent=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = 45
        self.padding = [10, 5]
        display_text = text if len(text) < 100 else text[:97] + "..."
        bubble = Label(
            text=display_text, size_hint_y=None, height=45,
            text_size=(Window.width * 0.7, None), valign="middle",
            padding=(12, 12), font_size="11sp", color=(1, 1, 1, 1)
        )
        def update_bg(inst, val):
            inst.canvas.before.clear()
            with inst.canvas.before:
                Color(0.2, 0.5, 0.9, 0.95) if is_sent else Color(0.6, 0.3, 0.8, 0.95)
                RoundedRectangle(pos=(inst.x + 2, inst.y + 2), size=(inst.width - 4, inst.height - 4), radius=[12])
        bubble.bind(pos=update_bg, size=update_bg)
        self.add_widget(bubble)

class ImageBubble(BoxLayout):
    def __init__(self, image_path, is_sent=True, filename="image.jpg", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = 250
        self.padding = [10, 5]
        from kivy.uix.image import AsyncImage
        self.add_widget(Label(text=filename, size_hint_y=None, height=25, font_size="9sp", color=(0.8, 0.8, 0.8, 1)))
        img = AsyncImage(source=image_path, size_hint_y=None, height=200, allow_stretch=True, keep_ratio=True)
        with img.canvas.before:
            Color(0.15, 0.15, 0.15, 0.8)
            RoundedRectangle(pos=img.pos, size=img.size, radius=[8])
        self.add_widget(img)

class ChatScreen(BoxLayout):
    def __init__(self, lxmf_client, my_address, **kwargs):
        super().__init__(**kwargs)
        self.lxmf = lxmf_client
        self.my_address = my_address
        self.orientation = "vertical"
        self.padding = [10, 10, 10, 10]
        self.spacing = 5
        
        header_text = f"My Address: {my_address[:16]}..."
        header = Label(text=header_text, size_hint_y=None, height=70, bold=True, font_size="10sp")
        with header.canvas.before:
            Color(0.1, 0.2, 0.1, 1)
            Rectangle(pos=header.pos, size=header.size)
        self.add_widget(header)
        
        self.chat_scroll = ScrollView()
        self.messages_box = BoxLayout(orientation="vertical", size_hint_y=None, padding=[5, 5], spacing=3)
        self.messages_box.bind(minimum_height=self.messages_box.setter("height"))
        self.chat_scroll.add_widget(self.messages_box)
        self.add_widget(self.chat_scroll)
        
        self.dest_input = TextInput(hint_text="Destination Address...", multiline=False, size_hint_y=None, height=40, font_size="10sp")
        self.add_widget(self.dest_input)
        
        row = BoxLayout(size_hint_y=None, height=50, spacing=5)
        self.msg_input = TextInput(hint_text="Type message...", multiline=False)
        self.msg_input.bind(on_text_validate=self.on_send_text)
        send_btn = Button(text="Send", size_hint_x=0.3, on_press=self.on_send_text)
        row.add_widget(self.msg_input); row.add_widget(send_btn)
        self.add_widget(row)

    def add_message(self, text, is_sent=True):
        bubble = ChatBubble(text=text, is_sent=is_sent)
        self.messages_box.add_widget(bubble)
        Clock.schedule_once(lambda dt: self.chat_scroll.scroll_to(bubble), 0.1)

    def on_send_text(self, instance):
        dest = self.dest_input.text.strip()
        msg = self.msg_input.text.strip()
        if dest and msg:
            self.add_message(msg, is_sent=True)
            self.msg_input.text = ""
            self.lxmf.send_text(dest, msg)

    def handle_incoming_message(self, message):
        Clock.schedule_once(lambda dt: self.add_message(f"[{message.source_hash[:8]}] {message.content}", False), 0)


class SimpleChatApp(App):
    def build(self):
        self.title = "SimpleSideband"
        
        # 1. Request Permissions
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.INTERNET, Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE, Permission.BLUETOOTH_CONNECT,
                Permission.BLUETOOTH_SCAN, Permission.ACCESS_FINE_LOCATION
            ])

        # 2. Initialize Reticulum Manager
        self.ret_manager = ReticulumManager()
        
        # 3. Setup Connectivity (Bluetooth with TCP Fallback)
        bt_success = False
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.simplesideband.simplesideband.PythonActivity')
                activity = PythonActivity.getInstance()
                
                if activity:
                    RNODE_ADDRESS = "XX:XX:XX:XX:XX:XX" # Replace with your MAC
                    if activity.connectRNode(RNODE_ADDRESS):
                        print(f"Connected to RNode {RNODE_ADDRESS}")
                        # Ensure your reticulum_manager.py has this method!
                        bt_success = self.ret_manager.add_tcp_interface("127.0.0.1", 4242) 
                else:
                    print("Activity instance not found")
            except Exception as e:
                print(f"BT setup error: {e}")

        if not bt_success:
            print("Trying TCP fallback...")
            self.ret_manager.add_tcp_interface("reticulum.meshchat.org", 4242)

        # 4. Initialize LXMF
        self.lxmf = LXMFClient(self.ret_manager.lxmf_router)
        my_addr = self.lxmf.create_destination() or self.ret_manager.get_address_hex()
        
        self.chat_screen = ChatScreen(self.lxmf, my_addr)
        self.lxmf.set_message_callback(self.chat_screen.handle_incoming_message)
        
        return self.chat_screen

    def on_stop(self):
        if hasattr(self, "ret_manager"):
            self.ret_manager.shutdown()

if __name__ == "__main__":
    SimpleChatApp().run()