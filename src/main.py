# src/main.py - Your First App Screen!
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

class ChatScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Title
        title = Label(text='📱 Simple Chat', size_hint_y=None, height=50, bold=True)
        self.add_widget(title)
        
        # Chat area (scrollable)
        self.chat_area = ScrollView()
        self.messages = BoxLayout(orientation='vertical', size_hint_y=None)
        self.messages.bind(minimum_height=self.messages.setter('height'))
        self.chat_area.add_widget(self.messages)
        self.add_widget(self.chat_area)
        
        # Input area
        input_box = BoxLayout(size_hint_y=None, height=50)
        self.msg_input = TextInput(hint_text='Type a message...', multiline=False)
        send_btn = Button(text='Send', size_hint_x=0.2)
        send_btn.bind(on_press=self.send_message)
        input_box.add_widget(self.msg_input)
        input_box.add_widget(send_btn)
        self.add_widget(input_box)
        
        # Add a welcome message
        self.add_message("👋 Welcome! This is your first chat app. 🎉", is_sent=False)
    
    def add_message(self, text, is_sent=True):
        """Add a message bubble to the chat"""
        bubble = Label(
            text=text,
            size_hint_y=None,
            height=40,
            text_size=(self.width-40, None),
            valign='middle',
            padding=(10, 10),
            color=(1,1,1,1) if is_sent else (0.9,0.9,1,1)
        )
        # Simple color coding: blue for sent, purple for received
        with bubble.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.2, 0.4, 0.8, 0.9 if is_sent else 0.3, 0.2, 0.6, 0.9)
            RoundedRectangle(pos=bubble.pos, size=bubble.size, radius=[10])
        self.messages.add_widget(bubble)
        self.chat_area.scroll_to(bubble)
    
    def send_message(self, instance):
        """What happens when you tap Send"""
        text = self.msg_input.text.strip()
        if text:
            self.add_message(text, is_sent=True)
            self.msg_input.text = ''
            # Later: we'll send this via Reticulum! 🛰️

class SimpleChatApp(App):
    def build(self):
        return ChatScreen()

if __name__ == '__main__':
    SimpleChatApp().run()