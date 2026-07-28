# © 2025 AmirAli Kamrani. All rights reserved.

# ui/widgets.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp

class ChessWidgets:
    """Collection of custom widgets"""
    
    @staticmethod
    def create_header(text, back_action=None):
        header = BoxLayout(size_hint_y=0.07, spacing=dp(10))
        
        if back_action:
            back = Button(
                text='< Back',
                font_size=dp(18),
                size_hint_x=0.2,
                background_normal='',
                background_color=(0.2, 0.2, 0.35, 1)
            )
            back.bind(on_release=back_action)
            header.add_widget(back)
            
        title = Label(text=text, font_size=dp(24), color=(1, 1, 1, 1), bold=True)
        header.add_widget(title)
        
        return header
        
    @staticmethod
    def create_card(content, bg_color=(0.15, 0.15, 0.25, 1)):
        card = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
        with card.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*bg_color)
            rect = RoundedRectangle(size=card.size, pos=card.pos, radius=[dp(10)])
            card.bind(size=lambda i, v: setattr(rect, 'size', v))
            card.bind(pos=lambda i, v: setattr(rect, 'pos', v))
        card.add_widget(content)
        return card
        
    @staticmethod
    def create_button(text, action=None, bg_color=(0.97, 0.59, 0.12, 1)):
        btn = Button(
            text=text,
            font_size=dp(18),
            size_hint_y=None,
            height=dp(45),
            background_normal='',
            background_color=bg_color
        )
        if action:
            btn.bind(on_release=action)
        return btn