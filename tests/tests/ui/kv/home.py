# © 2025 AmirAli Kamrani. All rights reserved.

# ui/kv/home.kv
<HomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(8)
        
        Label:
            text: '♟ Chess Master Pro'
            font_size: dp(32)
            color: (1, 1, 0.6, 1)
            bold: True
            
        Label:
            text: 'Professional Chess Game'
            font_size: dp(16)
            color: (0.7, 0.7, 0.7, 1)
            
        Widget:
            size_hint_y: 0.05
            
        GridLayout:
            cols: 2
            spacing: dp(10)
            size_hint_y: 0.55
            
            Button:
                text: '🎮 Local Game'
                font_size: dp(18)
                size_hint_y: None
                height: dp(55)
                background_normal: ''
                background_color: (0.2, 0.2, 0.35, 1)
                on_release: app.root.current = 'local'
                
            Button:
                text: '🤖 Play vs AI'
                font_size: dp(18)
                size_hint_y: None
                height: dp(55)
                background_normal: ''
                background_color: (0.2, 0.2, 0.35, 1)
                on_release: app.root.current = 'board'
                
            Button:
                text: '🌐 Online Game'
                font_size: dp(18)
                size_hint_y: None
                height: dp(55)
                background_normal: ''
                background_color: (0.2, 0.2, 0.35, 1)
                on_release: app.root.current = 'online'
                
            Button:
                text: '👤 Profile'
                font_size: dp(18)
                size_hint_y: None
                height: dp(55)
                background_normal: ''
                background_color: (0.2, 0.2, 0.35, 1)
                on_release: app.root.current = 'profile'
                
            Button:
                text: '🛒 Shop'
                font_size: dp(18)
                size_hint_y: None
                height: dp(55)
                background_normal: ''
                background_color: (0.2, 0.2, 0.35, 1)
                on_release: app.root.current = 'shop'
                
            Button:
                text: '⚙️ Settings'
                font_size: dp(18)
                size_hint_y: None
                height: dp(55)
                background_normal: ''
                background_color: (0.2, 0.2, 0.35, 1)
                on_release: app.root.current = 'settings'
                
        Widget:
            size_hint_y: 0.02
            
        Button:
            text: '🚪 Exit'
            font_size: dp(20)
            size_hint_y: None
            height: dp(45)
            background_normal: ''
            background_color: (0.6, 0.1, 0.1, 1)
            on_release: app.stop()
            
        Label:
            text: 'Status: Ready'
            font_size: dp(12)
            color: (0.4, 0.4, 0.4, 1)