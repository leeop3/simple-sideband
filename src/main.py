# src/main.py - SimpleSideband Chat App (CLEAN VERSION)
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

# Android path fixes (BEFORE importing RNS)
if platform == 'android':
    try:
        from android.storage import app_storage_path
        settings_path = app_storage_path()
        os.environ['KIVY_HOME'] = os.path.join(settings_path, '.kivy')
        os.environ["RNS_DATA_DIR"] = os.path.join(settings_path, ".reticulum")
        if not os.path.exists(os.environ["RNS_DATA_DIR"]):
            os.makedirs(os.environ["RNS_DATA_DIR"], exist_ok=True)
    except ImportError:
        pass

# Now import Reticulum
from networking.reticulum_manager import ReticulumManager
from networking.lxmf_client import LXMFClient, Message
from utils.image_handler import decode_and_save_image

# In SimpleChatApp.build(), after creating ret_manager:

# Try Classic BT first (RNode), then TCP fallback
bt_success = False

if platform == 'android':
    try:
        from jnius import autoclass
        
        # Get PythonActivity instance
        PythonActivity = autoclass('org.yourname.simplesideband.PythonActivity')
        activity = PythonActivity.getInstance()
        
        if activity:
            # Replace with your actual RNode MAC address
            RNODE_ADDRESS = "XX:XX:XX:XX:XX:XX"
            
            # Connect via PythonActivity bridge
            if activity.connectRNode(RNODE_ADDRESS):
                print("Connected to RNode at " + RNODE_ADDRESS)
                bt_success = self.ret_manager.add_rnode_classic_bt_interface(
                    activity.getBluetoothService(),
                    RNODE_ADDRESS
                )
            else:
                print("Failed to connect to RNode")
        else:
            print("PythonActivity instance not available")
            
    except Exception as e:
        print("BT setup error: " + str(e))

# Only try TCP if BT failed
if not bt_success:
    print("BT not available, trying TCP fallback...")
    try:
        self.ret_manager.add_tcp_interface("reticulum.meshchat.org", 4242)
    except Exception as e:
        print("TCP fallback skipped: " + str(e))


class ChatBubble(BoxLayout):
    def __init__(self, text, is_sent=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = 45
        self.padding = [10, 5]
        
        display_text = text if len(text) < 100 else text[:97] + "..."
        
        bubble = Label(
            text=display_text,
            size_hint_y=None,
            height=45,
            text_size=(Window.width * 0.7 if platform not in ['android', 'ios'] else None, None),
            valign="middle",
            padding=(12, 12),
            font_size="11sp",
            color=(1, 1, 1, 1)
        )
        
        with bubble.canvas.before:
            if is_sent:
                Color(0.2, 0.5, 0.9, 0.95)
            else:
                Color(0.6, 0.3, 0.8, 0.95)
            RoundedRectangle(
                pos=(bubble.x + 2, bubble.y + 2),
                size=(bubble.width - 4, bubble.height - 4),
                radius=[12]
            )
        
        self.add_widget(bubble)


class ImageBubble(BoxLayout):
    def __init__(self, image_path, is_sent=True, filename="image.jpg", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = 250
        self.padding = [10, 5]
        
        from kivy.uix.image import AsyncImage
        
        self.add_widget(Label(
            text=filename,
            size_hint_y=None,
            height=25,
            font_size="9sp",
            color=(0.8, 0.8, 0.8, 1)
        ))
        
        img = AsyncImage(
            source=image_path,
            size_hint_y=None,
            height=200,
            allow_stretch=True,
            keep_ratio=True
        )
        
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
        
        if platform not in ['android', 'ios']:
            Window.size = (450, 650)
        
        header_text = "Simple Chat - My Address: " + my_address[:16] + "..."
        header = Label(
            text=header_text,
            size_hint_y=None,
            height=70,
            bold=True,
            font_size="10sp",
            color=(0.9, 1, 0.9, 1)
        )
        with header.canvas.before:
            Color(0.1, 0.2, 0.1, 1)
            Rectangle(pos=header.pos, size=header.size)
        self.add_widget(header)
        
        self.chat_scroll = ScrollView()
        self.messages_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[5, 5],
            spacing=3
        )
        self.messages_box.bind(minimum_height=self.messages_box.setter("height"))
        self.chat_scroll.add_widget(self.messages_box)
        self.add_widget(self.chat_scroll)
        
        self.dest_input = TextInput(
            hint_text="Destination LXMF address...",
            multiline=False,
            size_hint_y=None,
            height=40,
            font_size="10sp"
        )
        self.add_widget(self.dest_input)
        
        input_row = BoxLayout(size_hint_y=None, height=50, spacing=5)
        self.msg_input = TextInput(
            hint_text="Type message...",
            multiline=False,
            font_size="11sp"
        )
        self.msg_input.bind(on_text_validate=self.on_send_text)
        
        img_btn = Button(
            text="Img",
            size_hint_x=0.2,
            background_color=(0.3, 0.3, 0.5, 1)
        )
        img_btn.bind(on_press=self.open_image_picker)
        
        send_btn = Button(
            text="Send",
            size_hint_x=0.25,
            background_color=(0.2, 0.7, 0.2, 1)
        )
        send_btn.bind(on_press=self.on_send_text)
        
        input_row.add_widget(self.msg_input)
        input_row.add_widget(img_btn)
        input_row.add_widget(send_btn)
        self.add_widget(input_row)
        
        self.add_message("Welcome! Send text or images!", is_sent=False)
    
    def add_message(self, text, is_sent=True):
        bubble = ChatBubble(text=text, is_sent=is_sent)
        self.messages_box.add_widget(bubble)
        Clock.schedule_once(lambda dt: self.chat_scroll.scroll_to(bubble), 0.1)
    
    def add_image(self, image_path, is_sent=True, filename="image.jpg"):
        bubble = ImageBubble(image_path=image_path, is_sent=is_sent, filename=filename)
        self.messages_box.add_widget(bubble)
        Clock.schedule_once(lambda dt: self.chat_scroll.scroll_to(bubble), 0.1)
    
    def on_send_text(self, instance):
        destination = self.dest_input.text.strip()
        text = self.msg_input.text.strip()
        if not destination or not text:
            return
        self.add_message(text, is_sent=True)
        self.msg_input.text = ""
        try:
            self.lxmf.send_text(destination, text)
        except Exception as e:
            self.add_message("Send failed: " + str(e), is_sent=False)
    
    def open_image_picker(self, instance):
        initial_path = "/sdcard/Pictures" if platform == 'android' else os.path.expanduser("~")
        
        content = BoxLayout(orientation="vertical")
        file_chooser = FileChooserIconView(
            path=initial_path,
            filters=["*.jpg", "*.jpeg", "*.png", "*.gif"]
        )
        
        btn_row = BoxLayout(size_hint_y=None, height=50)
        cancel_btn = Button(text="Cancel")
        cancel_btn.bind(on_press=lambda x: self.popup.dismiss())
        select_btn = Button(text="Select", background_color=(0.2, 0.7, 0.2, 1))
        select_btn.bind(on_press=lambda x: self.send_selected_image(file_chooser.selection))
        
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(select_btn)
        content.add_widget(file_chooser)
        content.add_widget(btn_row)
        
        self.popup = Popup(title="Select Image", content=content, size_hint=(0.9, 0.9))
        self.popup.open()
    
    def send_selected_image(self, selection):
        self.popup.dismiss()
        if not selection:
            return
        try:
            image_path = selection[0]
            destination = self.dest_input.text.strip()
            if not destination:
                self.add_message("Need destination!", is_sent=False)
                return
            self.add_image(image_path, is_sent=True, filename=os.path.basename(image_path))
            self.lxmf.send_image(destination, image_path)
        except Exception as e:
            self.add_message("Image send failed: " + str(e), is_sent=False)
    
    def handle_incoming_message(self, message):
        Clock.schedule_once(lambda dt: self._add_incoming(message), 0)
    
    def _add_incoming(self, message):
        prefix = "[" + message.source_hash[:8] + "] "
        if message.is_image:
            try:
                parts = message.content.split(":", 2)
                if len(parts) == 3:
                    filename = parts[1]
                    encoded_data = parts[2]
                    temp_path = os.path.join(tempfile.gettempdir(), "msg_" + str(message.timestamp) + ".jpg")
                    if decode_and_save_image(encoded_data, temp_path):
                        self.add_image(temp_path, is_sent=False, filename=prefix + filename)
                    else:
                        self.add_message(prefix + "Image decode failed", is_sent=False)
            except Exception as e:
                self.add_message(prefix + "Image error: " + str(e), is_sent=False)
        else:
            self.add_message(prefix + message.content, is_sent=False)


class SimpleChatApp(App):
    def build(self):
        self.title = "SimpleSideband"
        
        # Android permissions
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.INTERNET,
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.CAMERA,
                    Permission.BLUETOOTH,
                    Permission.BLUETOOTH_ADMIN,
                    Permission.BLUETOOTH_CONNECT,
                    Permission.BLUETOOTH_SCAN,
                    Permission.ACCESS_FINE_LOCATION,
                    Permission.ACCESS_COARSE_LOCATION
                ])
            except ImportError:
                pass
        
        # Initialize Reticulum (TCP fallback only for now)
        self.ret_manager = ReticulumManager()
        
        try:
            self.ret_manager.add_tcp_interface("reticulum.meshchat.org", 4242)
        except Exception as e:
            print("TCP connection skipped: " + str(e))
        
        self.lxmf = LXMFClient(self.ret_manager.lxmf_router)
        my_address = self.lxmf.create_destination()
        if not my_address:
            my_address = self.ret_manager.get_address_hex()
        
        self.chat_screen = ChatScreen(self.lxmf, my_address)
        self.lxmf.set_message_callback(self.chat_screen.handle_incoming_message)
        
        return self.chat_screen
    
    def on_stop(self):
        if hasattr(self, "ret_manager"):
            self.ret_manager.shutdown()


if __name__ == "__main__":
    SimpleChatApp().run()