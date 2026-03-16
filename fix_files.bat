@echo off
echo ========================================
echo  AUTO-FIX: Creating Clean Python Files
echo ========================================
echo.

cd /d F:\simple-sideband\src

:: Create __init__.py files
echo Creating __init__.py files...
echo. > __init__.py
echo. > networking\__init__.py
echo. > utils\__init__.py

:: Create main.py using PowerShell
echo Creating main.py...
powershell -Command "$content = @'
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

from networking.reticulum_manager import ReticulumManager
from networking.lxmf_client import LXMFClient, Message
from utils.image_handler import decode_and_save_image

import os
import tempfile


class ChatBubble(BoxLayout):
    def __init__(self, text, is_sent=True, source=\"\"):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 45
        self.padding = [10, 5]
        
        display_text = text if len(text) < 100 else text[:97] + '...'
        
        bubble = Label(
            text=display_text,
            size_hint_y=None,
            height=45,
            text_size=(self.width - 30, None),
            valign='middle',
            padding=(12, 12),
            font_size='11sp',
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
    def __init__(self, image_path, is_sent=True, source=\"\", filename=\"image.jpg\"):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 250
        self.padding = [10, 5]
        
        name_label = Label(
            text=filename,
            size_hint_y=None,
            height=25,
            font_size='9sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        self.add_widget(name_label)
        
        from kivy.uix.image import AsyncImage
        img = AsyncImage(
            source=image_path,
            size_hint_y=None,
            height=200,
            allow_stretch=True,
            keep_ratio=True
        )
        
        with img.canvas.before:
            Color(0.15, 0.15, 0.15, 0.8)
            RoundedRectangle(
                pos=img.pos,
                size=img.size,
                radius=[8]
            )
        
        self.add_widget(img)


class ChatScreen(BoxLayout):
    def __init__(self, lxmf_client, my_address, **kwargs):
        super().__init__(**kwargs)
        self.lxmf = lxmf_client
        self.my_address = my_address
        self.orientation = 'vertical'
        self.padding = [10, 10, 10, 10]
        self.spacing = 5
        
        Window.size = (450, 650)
        
        header_text = 'Simple Chat - My Address: ' + my_address
        header = Label(
            text=header_text,
            size_hint_y=None,
            height=70,
            bold=True,
            font_size='10sp',
            color=(0.9, 1, 0.9, 1)
        )
        header.canvas.before.add(Color(0.1, 0.2, 0.1, 1))
        header.canvas.before.add(Rectangle(pos=header.pos, size=header.size))
        self.add_widget(header)
        
        self.chat_scroll = ScrollView()
        self.messages_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[5, 5],
            spacing=3
        )
        self.messages_box.bind(minimum_height=self.messages_box.setter('height'))
        self.chat_scroll.add_widget(self.messages_box)
        self.add_widget(self.chat_scroll)
        
        dest_label = Label(text='Send to (LXMF address):', size_hint_y=None, height=25, font_size='9sp')
        self.dest_input = TextInput(
            hint_text=\"Paste address here...\",
            multiline=False,
            size_hint_y=None,
            height=35,
            font_size='10sp'
        )
        self.add_widget(dest_label)
        self.add_widget(self.dest_input)
        
        input_row = BoxLayout(size_hint_y=None, height=50, spacing=5)
        
        self.msg_input = TextInput(
            hint_text='Type message...',
            multiline=False,
            font_size='11sp'
        )
        self.msg_input.bind(on_text_validate=self.on_send_text)
        
        img_btn = Button(
            text='Image',
            size_hint_x=0.15,
            background_color=(0.3, 0.3, 0.5, 1)
        )
        img_btn.bind(on_press=self.open_image_picker)
        
        send_btn = Button(
            text='Send',
            size_hint_x=0.25,
            background_color=(0.2, 0.7, 0.2, 1)
        )
        send_btn.bind(on_press=self.on_send_text)
        
        input_row.add_widget(self.msg_input)
        input_row.add_widget(img_btn)
        input_row.add_widget(send_btn)
        self.add_widget(input_row)
        
        self.add_message('Welcome! Send text or images!', is_sent=False)
    
    def add_message(self, text, is_sent=True):
        bubble = ChatBubble(text=text, is_sent=is_sent)
        self.messages_box.add_widget(bubble)
        Clock.schedule_once(lambda dt: self.chat_scroll.scroll_to(bubble), 0.01)
    
    def add_image(self, image_path, is_sent=True, filename=\"image.jpg\"):
        bubble = ImageBubble(image_path=image_path, is_sent=is_sent, filename=filename)
        self.messages_box.add_widget(bubble)
        Clock.schedule_once(lambda dt: self.chat_scroll.scroll_to(bubble), 0.01)
    
    def on_send_text(self, instance):
        destination = self.dest_input.text.strip()
        text = self.msg_input.text.strip()
        
        if not destination:
            self.add_message('Enter destination address first!', is_sent=False)
            return
        if not text:
            return
        
        self.add_message(text, is_sent=True)
        self.msg_input.text = ''
        self.lxmf.send_text(destination, text)
    
    def open_image_picker(self, instance):
        content = BoxLayout(orientation='vertical')
        
        file_chooser = FileChooserIconView(
            path=os.path.expanduser('~'),
            filters=['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
        )
        
        btn_row = BoxLayout(size_hint_y=None, height=50)
        
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=lambda x: self.popup.dismiss())
        
        select_btn = Button(text='Send Image', background_color=(0.2, 0.7, 0.2, 1))
        select_btn.bind(on_press=lambda x: self.send_selected_image(file_chooser.selection))
        
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(select_btn)
        
        content.add_widget(file_chooser)
        content.add_widget(btn_row)
        
        self.popup = Popup(
            title='Select Image',
            content=content,
            size_hint=(0.9, 0.8)
        )
        self.popup.open()
    
    def send_selected_image(self, selection):
        self.popup.dismiss()
        
        if not selection:
            return
        
        image_path = selection[0]
        destination = self.dest_input.text.strip()
        
        if not destination:
            self.add_message('Enter destination address first!', is_sent=False)
            return
        
        self.add_image(image_path, is_sent=True, filename=os.path.basename(image_path))
        self.lxmf.send_image(destination, image_path)
    
    def handle_incoming_message(self, message):
        Clock.schedule_once(lambda dt: self._add_incoming(message), 0)
    
    def _add_incoming(self, message):
        if message.is_image:
            parts = message.content.split(':', 2)
            if len(parts) == 3:
                filename = parts[1]
                encoded_data = parts[2]
                
                temp_path = os.path.join(tempfile.gettempdir(), 'msg_' + str(message.timestamp) + '.jpg')
                decode_and_save_image(encoded_data, temp_path)
                
                prefix = '[' + message.source_hash + '] '
                self.add_image(temp_path, is_sent=False, filename=prefix + filename)
        else:
            prefix = '[' + message.source_hash + '] '
            self.add_message(prefix + message.content, is_sent=False)


class SimpleChatApp(App):
    def build(self):
        self.ret_manager = ReticulumManager()
        
        try:
            self.ret_manager.add_tcp_interface('reticulum.meshchat.org', 4242)
        except Exception as e:
            print('Hub connection skipped: ' + str(e))
        
        self.lxmf = LXMFClient(self.ret_manager.lxmf_router)
        my_address = self.lxmf.create_destination()
        
        if not my_address:
            my_address = self.ret_manager.get_address_hex()
        
        self.chat_screen = ChatScreen(self.lxmf, my_address)
        self.lxmf.set_message_callback(self.chat_screen.handle_incoming_message)
        
        return self.chat_screen
    
    def on_stop(self):
        if hasattr(self, 'ret_manager'):
            self.ret_manager.shutdown()


if __name__ == '__main__':
    SimpleChatApp().run()
'@
Set-Content -Path 'main.py' -Value $content -Encoding UTF8"

echo Creating lxmf_client.py...
powershell -Command "$content = @'
import LXMF
import RNS
from typing import Callable, Optional

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
    
    def create_destination(self, app_name=\"SimpleSideband\"):
        try:
            print(\"Creating destination for: \" + app_name)
            self.destination = self.router.register_delivery_destination(
                app_name=app_name,
                app_data=b\"v1.0\"
            )
            if self.destination:
                address = self.destination.hash.hex()
                print(\"Destination created! Address: \" + address)
                return address
            else:
                print(\"Failed to create destination\")
                return None
        except Exception as e:
            print(\"Error creating destination: \" + str(e))
            return self.router.identity.hash.hex()
    
    def send_text(self, destination_address, text):
        if not self.destination:
            print(\"Error: Destination not created yet!\")
            return False
        if len(destination_address) != 32:
            print(\"Invalid destination address length\")
            return False
        try:
            print(\"Sending to \" + destination_address[:8] + \"...\")
            target_bytes = bytes.fromhex(destination_address)
            message = LXMF.LXMessage(
                destination=self.destination,
                target=target_bytes,
                content=text.encode(\"utf-8\"),
                fields=LXMF.LXMessage.TEXT_FIELD
            )
            message.register_delivery_callback(self._on_delivery_status)
            self.router.handle_outbound(message)
            return True
        except Exception as e:
            print(\"Error sending message: \" + str(e))
            return False
    
    def _handle_incoming(self, message):
        try:
            if isinstance(message.content, bytes):
                text = message.content.decode(\"utf-8\")
            else:
                text = str(message.content)
            msg = Message(
                timestamp=message.timestamp,
                source_hash=message.source_hash.hex()[:8],
                content=text,
                is_image=text.startswith(\"IMAGE:\")
            )
            if self.on_message_received:
                print(\"Received from \" + msg.source_hash)
                self.on_message_received(msg)
        except Exception as e:
            print(\"Error processing message: \" + str(e))
    
    def _on_delivery_status(self, message, status):
        if status == LXMF.LXMessage.DELIVERED:
            print(\"Message delivered!\")
        elif status == LXMF.LXMessage.FAILED:
            print(\"Message delivery failed\")
        elif status == LXMF.LXMessage.PENDING:
            print(\"Message pending delivery...\")
    
    def send_image(self, destination_address, image_path):
        if not self.destination:
            print(\"Error: Destination not created yet!\")
            return False
        from utils.image_handler import compress_and_encode_image
        encoded_data, metadata = compress_and_encode_image(image_path)
        if not encoded_data:
            print(\"Failed to process image\")
            return False
        message_content = \"IMAGE:\" + metadata[\"filename\"] + \":\" + encoded_data
        if len(destination_address) != 32:
            print(\"Invalid destination address length\")
            return False
        try:
            print(\"Sending image...\")
            target_bytes = bytes.fromhex(destination_address)
            message = LXMF.LXMessage(
                destination=self.destination,
                target=target_bytes,
                content=message_content.encode(\"utf-8\"),
                fields=LXMF.LXMessage.TEXT_FIELD
            )
            message.register_delivery_callback(self._on_delivery_status)
            self.router.handle_outbound(message)
            return True
        except Exception as e:
            print(\"Error sending image: \" + str(e))
            return False
    
    def set_message_callback(self, callback_function):
        self.on_message_received = callback_function
'@
Set-Content -Path 'networking\lxmf_client.py' -Value $content -Encoding UTF8"

echo Creating image_handler.py...
powershell -Command "$content = @'
import base64
from PIL import Image
from io import BytesIO
import os

def compress_and_encode_image(image_path, max_size_kb=200, quality=75, max_dimension=800):
    try:
        img = Image.open(image_path)
        if img.mode in (\"RGBA\", \"P\", \"LA\"):
            background = Image.new(\"RGB\", img.size, (255, 255, 255))
            if img.mode == \"P\":
                img = img.convert(\"RGBA\")
            background.paste(img, mask=img.split()[-1] if img.mode in (\"RGBA\", \"LA\") else None)
            img = background
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        current_quality = quality
        while current_quality > 10:
            buffer = BytesIO()
            img.save(buffer, format=\"JPEG\", quality=current_quality, optimize=True)
            size_kb = buffer.tell() / 1024
            if size_kb <= max_size_kb:
                break
            current_quality -= 10
        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode(\"ascii\")
        metadata = {
            \"filename\": os.path.basename(image_path),
            \"original_size\": os.path.getsize(image_path),
            \"compressed_size\": len(encoded),
            \"dimensions\": img.size,
            \"quality_used\": current_quality
        }
        print(\"Image compressed successfully\")
        return encoded, metadata
    except Exception as e:
        print(\"Error processing image: \" + str(e))
        return None, None

def decode_and_save_image(encoded_data, output_path):
    try:
        image_data = base64.b64decode(encoded_data)
        with open(output_path, \"wb\") as f:
            f.write(image_data)
        print(\"Image saved: \" + output_path)
        return True
    except Exception as e:
        print(\"Error saving image: \" + str(e))
        return False
'@
Set-Content -Path 'utils\image_handler.py' -Value $content -Encoding UTF8"

echo.
echo ========================================
echo  ALL FILES CREATED SUCCESSFULLY!
echo ========================================
echo.
echo  Next steps:
echo  1. cd F:\simple-sideband\src
echo  2. python -m py_compile main.py
echo  3. python main.py
echo.
pause