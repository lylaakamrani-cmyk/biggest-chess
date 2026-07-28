# © 2025 AmirAli Kamrani. All rights reserved.

# ui/dialogs.py
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp

class DialogManager:
    @staticmethod
    def show_message(text, title='Message'):
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(Label(text=text, font_size=dp(16)))
        btn = Button(text='OK', size_hint_y=None, height=dp(40))
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.3))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()