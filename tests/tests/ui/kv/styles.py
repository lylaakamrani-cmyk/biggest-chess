# © 2025 AmirAli Kamrani. All rights reserved.

# ui/kv/styles.kv
<CustomButton@Button>:
    background_normal: ''
    background_color: (0.2, 0.2, 0.35, 1)
    color: (1, 1, 1, 1)
    font_size: '18sp'

<PrimaryButton@CustomButton>:
    background_color: (0.97, 0.59, 0.12, 1)

<DangerButton@CustomButton>:
    background_color: (0.6, 0.1, 0.1, 1)

<SuccessButton@CustomButton>:
    background_color: (0.2, 0.7, 0.2, 1)

<Card@BoxLayout>:
    orientation: 'vertical'
    padding: '10dp'
    spacing: '5dp'
    canvas.before:
        Color:
            rgba: (0.15, 0.15, 0.25, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [('10dp',)]

<Screen>:
    canvas.before:
        Color:
            rgba: (0.08, 0.08, 0.15, 1)
        Rectangle:
            pos: self.pos
            size: self.size