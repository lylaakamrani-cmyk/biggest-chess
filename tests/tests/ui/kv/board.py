# © 2025 AmirAli Kamrani. All rights reserved.

# ui/kv/board.kv
<BoardScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(8)
        spacing: dp(5)
        
        BoxLayout:
            size_hint_y: 0.07
            
            Button:
                text: '< Back'
                font_size: dp(18)
                size_hint_x: 0.2
                background_normal: ''
                background_color: (0.2, 0.2, 0.35, 1)
                on_release: app.root.current = 'home'
                
            Label:
                text: '♟ Chess Board'
                font_size: dp(24)
                color: (1, 1, 1, 1)
                bold: True
                
        GridLayout:
            id: board_grid
            cols: 8
            rows: 8
            size_hint: (1, 0.7)
            
        BoxLayout:
            size_hint_y: 0.05
            spacing: dp(10)
            
            Label:
                id: status_label
                text: 'Turn: White'
                font_size: dp(16)
                color: (0.7, 0.7, 0.7, 1)
                
            Label:
                id: move_count_label
                text: 'Moves: 0'
                font_size: dp(16)
                color: (0.7, 0.7, 0.7, 1)
                
        BoxLayout:
            size_hint_y: 0.08
            spacing: dp(8)
            
            Button:
                text: '↩ Undo'
                font_size: dp(16)
                background_normal: ''
                background_color: (0.2, 0.2, 0.35, 1)
                on_release: root.do_undo()
                
            Button:
                text: '🔄 Reset'
                font_size: dp(16)
                background_normal: ''
                background_color: (0.2, 0.2, 0.35, 1)
                on_release: root.do_reset()
                
            Button:
                text: '🔃 Flip'
                font_size: dp(16)
                background_normal: ''
                background_color: (0.2, 0.2, 0.35, 1)
                on_release: root.do_flip()