# © 2025 AmirAli Kamrani. All rights reserved.

# ui/dialogs.py
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.metrics import dp

class DialogManager:
    """Manage dialog popups"""
    
    @staticmethod
    def show_message(text, title='Message', button_text='OK'):
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(Label(text=text, font_size=dp(16)))
        
        btn = Button(text=button_text, size_hint_y=None, height=dp(40))
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.3))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()
        
    @staticmethod
    def show_confirm(text, title='Confirm', on_confirm=None):
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(Label(text=text, font_size=dp(16)))
        
        buttons = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        yes_btn = Button(text='Yes')
        no_btn = Button(text='No')
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.3))
        
        yes_btn.bind(on_release=lambda x: (popup.dismiss(), on_confirm() if on_confirm else None))
        no_btn.bind(on_release=popup.dismiss)
        
        buttons.add_widget(yes_btn)
        buttons.add_widget(no_btn)
        content.add_widget(buttons)
        popup.open()
        
    @staticmethod
    def show_input(title='Input', hint='Enter value', on_submit=None):
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        text_input = TextInput(hint_text=hint, multiline=False)
        content.add_widget(text_input)
        
        buttons = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        ok_btn = Button(text='OK')
        cancel_btn = Button(text='Cancel')
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.35))
        
        def submit():
            popup.dismiss()
            if on_submit and text_input.text:
                on_submit(text_input.text)
                
        ok_btn.bind(on_release=lambda x: submit())
        cancel_btn.bind(on_release=popup.dismiss)
        
        buttons.add_widget(ok_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)
        popup.open()
        
    @staticmethod
    def show_loading(message='Loading...'):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        content.add_widget(Label(text=message, font_size=dp(16)))
        
        popup = Popup(title='Please wait', content=content, size_hint=(0.6, 0.25))
        popup.open()
        return popup