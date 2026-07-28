# © 2025 AmirAli Kamrani. All rights reserved.

# ui/kv/login.kv
<LoginScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(30)
        spacing: dp(15)
        
        Button:
            text: '< Back'
            font_size: dp(18)
            size_hint_y: None
            height: dp(40)
            background_normal: ''
            background_color: (0.2, 0.2, 0.35, 1)
            on_release: app.root.current = 'home'
            
        Widget:
            size_hint_y: 0.1
            
        Label:
            text: '🔐 Login'
            font_size: dp(32)
            color: (1, 1, 1, 1)
            bold: True
            
        Label:
            text: 'Sign in to your account'
            font_size: dp(16)
            color: (0.7, 0.7, 0.7, 1)
            
        Widget:
            size_hint_y: 0.05
            
        TextInput:
            id: username
            hint_text: 'Username'
            font_size: dp(18)
            size_hint_y: None
            height: dp(50)
            background_color: (0.15, 0.15, 0.25, 1)
            foreground_color: (1, 1, 1, 1)
            
        TextInput:
            id: password
            hint_text: 'Password'
            font_size: dp(18)
            size_hint_y: None
            height: dp(50)
            password: True
            background_color: (0.15, 0.15, 0.25, 1)
            foreground_color: (1, 1, 1, 1)
            
        Widget:
            size_hint_y: 0.05
            
        Button:
            text: 'Login'
            font_size: dp(20)
            size_hint_y: None
            height: dp(50)
            background_normal: ''
            background_color: (0.97, 0.59, 0.12, 1)
            on_release: root.do_login()
            
        Button:
            text: 'Create Account'
            font_size: dp(16)
            size_hint_y: None
            height: dp(40)
            background_normal: ''
            background_color: (0.2, 0.2, 0.35, 1)
            
        Label:
            id: status
            text: ''
            font_size: dp(14)
            color: (0.8, 0.2, 0.2, 1)