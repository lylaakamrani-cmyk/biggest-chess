# © 2025 AmirAli Kamrani. All rights reserved.

# ui/widgets.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.metrics import dp

class ChessWidgets:
    @staticmethod
    def create_button(text, action=None, bg_color=(0.97, 0.59, 0.12, 1)):
        btn = Button(text=text, font_size=dp(18), size_hint_y=None, height=dp(45),
                    background_normal='', background_color=bg_color)
        if action:
            btn.bind(on_release=action)
        return btn