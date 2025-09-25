"""
界面美化样式配置
提供统一的圆角设计和颜色主题
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk


class StyleConfig:
    """样式配置类"""
    
    # 颜色主题
    COLORS = {
        'primary': '#3498db',
        'primary_hover': '#2980b9',
        'secondary': '#2ecc71',
        'secondary_hover': '#27ae60',
        'accent': '#e74c3c',
        'accent_hover': '#c0392b',
        'warning': '#f39c12',
        'warning_hover': '#e67e22',
        'info': '#9b59b6',
        'info_hover': '#8e44ad',
        'success': '#27ae60',
        'success_hover': '#229954',
        'danger': '#e74c3c',
        'danger_hover': '#c0392b',
        
        # 背景色
        'bg_light': '#ffffff',
        'bg_dark': '#2b2b2b',
        'bg_card': '#f8f9fa',
        'bg_card_dark': '#3b3b3b',
        'bg_container': '#f0f0f0',
        'bg_container_dark': '#1e1e1e',
        
        # 文字色
        'text_primary': '#2c3e50',
        'text_primary_dark': '#ecf0f1',
        'text_secondary': '#34495e',
        'text_secondary_dark': '#bdc3c7',
        'text_muted': '#7f8c8d',
        'text_muted_dark': '#95a5a6',
        
        # 边框色
        'border': '#e0e0e0',
        'border_dark': '#404040',
        'border_light': '#f0f0f0',
        'border_light_dark': '#555555',
    }
    
    # 圆角半径
    CORNER_RADIUS = {
        'small': 8,
        'medium': 12,
        'large': 15,
        'xlarge': 20,
        'xxlarge': 25,
    }
    
    # 字体配置
    FONTS = {
        'title': ('Arial', 22, 'bold'),
        'subtitle': ('Arial', 18, 'bold'),
        'heading': ('Arial', 16, 'bold'),
        'body': ('Arial', 14),
        'small': ('Arial', 12),
        'tiny': ('Arial', 10),
    }
    
    # 间距配置
    SPACING = {
        'xs': 5,
        'sm': 10,
        'md': 15,
        'lg': 20,
        'xl': 25,
        'xxl': 30,
    }


def apply_rounded_theme():
    """应用圆角主题到CustomTkinter"""
    # 设置全局主题
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # 注意：CustomTkinter不支持类级别的configure方法
    # 样式需要在创建组件时单独设置
    print("✅ 圆角主题已应用")


def create_rounded_frame(parent, **kwargs):
    """创建圆角框架"""
    colors = StyleConfig.COLORS
    radius = StyleConfig.CORNER_RADIUS
    
    default_kwargs = {
        'corner_radius': radius['medium'],
        'fg_color': (colors['bg_light'], colors['bg_dark']),
        'border_width': 1,
        'border_color': (colors['border'], colors['border_dark']),
    }
    
    default_kwargs.update(kwargs)
    return ctk.CTkFrame(parent, **default_kwargs)


def create_rounded_button(parent, text, **kwargs):
    """创建圆角按钮"""
    colors = StyleConfig.COLORS
    radius = StyleConfig.CORNER_RADIUS
    
    default_kwargs = {
        'corner_radius': radius['medium'],
        'fg_color': (colors['primary'], colors['primary_hover']),
        'hover_color': (colors['primary_hover'], colors['primary']),
        'text_color': ('#ffffff', '#ffffff'),
        'font': StyleConfig.FONTS['body'],
    }
    
    default_kwargs.update(kwargs)
    return ctk.CTkButton(parent, text=text, **default_kwargs)


def create_rounded_entry(parent, **kwargs):
    """创建圆角输入框"""
    colors = StyleConfig.COLORS
    radius = StyleConfig.CORNER_RADIUS
    
    default_kwargs = {
        'corner_radius': radius['medium'],
        'fg_color': (colors['bg_card'], colors['bg_card_dark']),
        'border_width': 1,
        'border_color': (colors['border_light'], colors['border_light_dark']),
        'font': StyleConfig.FONTS['body'],
        'text_color': (colors['text_primary'], colors['text_primary_dark']),
    }
    
    default_kwargs.update(kwargs)
    return ctk.CTkEntry(parent, **default_kwargs)


def create_rounded_label(parent, text, **kwargs):
    """创建圆角标签"""
    colors = StyleConfig.COLORS
    
    default_kwargs = {
        'text_color': (colors['text_primary'], colors['text_primary_dark']),
        'font': StyleConfig.FONTS['body'],
    }
    
    default_kwargs.update(kwargs)
    return ctk.CTkLabel(parent, text=text, **default_kwargs)


def create_card_frame(parent, **kwargs):
    """创建卡片式框架"""
    colors = StyleConfig.COLORS
    radius = StyleConfig.CORNER_RADIUS
    
    default_kwargs = {
        'corner_radius': radius['large'],
        'fg_color': (colors['bg_card'], colors['bg_card_dark']),
        'border_width': 1,
        'border_color': (colors['border'], colors['border_dark']),
    }
    
    default_kwargs.update(kwargs)
    return ctk.CTkFrame(parent, **default_kwargs)


def create_accent_button(parent, text, color_type='primary', **kwargs):
    """创建强调色按钮"""
    colors = StyleConfig.COLORS
    radius = StyleConfig.CORNER_RADIUS
    
    color_map = {
        'primary': (colors['primary'], colors['primary_hover']),
        'secondary': (colors['secondary'], colors['secondary_hover']),
        'accent': (colors['accent'], colors['accent_hover']),
        'warning': (colors['warning'], colors['warning_hover']),
        'info': (colors['info'], colors['info_hover']),
        'success': (colors['success'], colors['success_hover']),
        'danger': (colors['danger'], colors['danger_hover']),
    }
    
    fg_color, hover_color = color_map.get(color_type, color_map['primary'])
    
    default_kwargs = {
        'corner_radius': radius['medium'],
        'fg_color': fg_color,
        'hover_color': hover_color,
        'text_color': ('#ffffff', '#ffffff'),
        'font': StyleConfig.FONTS['body'],
    }
    
    default_kwargs.update(kwargs)
    return ctk.CTkButton(parent, text=text, **default_kwargs)


def apply_ttk_styles():
    """应用TTK样式"""
    style = ttk.Style()
    
    # 配置样式
    style.configure('Rounded.TFrame', 
                   relief='solid', 
                   borderwidth=1,
                   background='#f8f9fa')
    
    style.configure('Rounded.TLabelFrame',
                   relief='solid',
                   borderwidth=1,
                   background='#f8f9fa')
    
    style.configure('Accent.TButton',
                   relief='flat',
                   borderwidth=0,
                   background='#3498db',
                   foreground='white',
                   font=('Arial', 12, 'bold'))
    
    style.map('Accent.TButton',
              background=[('active', '#2980b9'),
                         ('pressed', '#1f618d')])
    
    style.configure('Accent.TProgressbar',
                   background='#3498db',
                   troughcolor='#ecf0f1',
                   borderwidth=0,
                   lightcolor='#3498db',
                   darkcolor='#3498db')


def get_spacing(size='md'):
    """获取间距值"""
    return StyleConfig.SPACING.get(size, StyleConfig.SPACING['md'])


def get_font(font_type='body'):
    """获取字体配置"""
    return StyleConfig.FONTS.get(font_type, StyleConfig.FONTS['body'])


def get_color(color_name):
    """获取颜色值"""
    return StyleConfig.COLORS.get(color_name, StyleConfig.COLORS['text_primary'])


def get_radius(size='medium'):
    """获取圆角半径"""
    return StyleConfig.CORNER_RADIUS.get(size, StyleConfig.CORNER_RADIUS['medium'])


# 预定义的样式组合
STYLE_PRESETS = {
    'card': {
        'corner_radius': 20,
        'fg_color': ('#ffffff', '#3b3b3b'),
        'border_width': 1,
        'border_color': ('#e0e0e0', '#404040'),
    },
    'button_primary': {
        'corner_radius': 15,
        'fg_color': ('#3498db', '#2980b9'),
        'hover_color': ('#2980b9', '#1f618d'),
        'text_color': ('#ffffff', '#ffffff'),
    },
    'button_secondary': {
        'corner_radius': 15,
        'fg_color': ('#2ecc71', '#27ae60'),
        'hover_color': ('#27ae60', '#229954'),
        'text_color': ('#ffffff', '#ffffff'),
    },
    'button_accent': {
        'corner_radius': 15,
        'fg_color': ('#e74c3c', '#c0392b'),
        'hover_color': ('#c0392b', '#a93226'),
        'text_color': ('#ffffff', '#ffffff'),
    },
    'input_field': {
        'corner_radius': 12,
        'fg_color': ('#f8f9fa', '#404040'),
        'border_width': 1,
        'border_color': ('#e0e0e0', '#555555'),
    },
}


def apply_preset_style(widget, preset_name):
    """应用预设样式"""
    if preset_name in STYLE_PRESETS:
        style_config = STYLE_PRESETS[preset_name]
        for key, value in style_config.items():
            if hasattr(widget, key):
                setattr(widget, key, value)


if __name__ == "__main__":
    # 测试样式配置
    root = tk.Tk()
    root.title("样式测试")
    root.geometry("400x300")
    
    # 应用TTK样式
    apply_ttk_styles()
    
    # 创建测试框架
    main_frame = ttk.Frame(root, style='Rounded.TFrame')
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # 创建测试按钮
    test_button = ttk.Button(main_frame, text="测试按钮", style='Accent.TButton')
    test_button.pack(pady=10)
    
    # 创建测试标签框架
    test_frame = ttk.LabelFrame(main_frame, text="测试框架", style='Rounded.TLabelFrame')
    test_frame.pack(fill='both', expand=True, pady=10)
    
    test_label = ttk.Label(test_frame, text="这是一个测试标签")
    test_label.pack(pady=20)
    
    root.mainloop()
