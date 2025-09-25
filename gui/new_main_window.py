"""
新的界面设计 - 信息录入/修改 + 随机转盘/扭蛋机
基于用户需求重新设计的界面
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Dict, List, Optional, Any
import random
import math
import threading
import time
from datetime import datetime
import json

# 设置CustomTkinter主题
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SpinWheel(ctk.CTkCanvas):
    """随机转盘/扭蛋机组件"""
    
    def __init__(self, parent, width=300, height=300, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.radius = min(width, height) // 2 - 20
        
        # 转盘状态
        self.is_spinning = False
        self.current_angle = 0
        self.spin_speed = 0
        self.target_angle = 0
        
        # 转盘选项
        self.options = [
            {"text": "早餐推荐", "color": "#FF6B6B", "value": "breakfast"},
            {"text": "午餐推荐", "color": "#4ECDC4", "value": "lunch"},
            {"text": "晚餐推荐", "color": "#45B7D1", "value": "dinner"},
            {"text": "健康建议", "color": "#96CEB4", "value": "health"},
            {"text": "营养分析", "color": "#FFEAA7", "value": "nutrition"},
            {"text": "运动建议", "color": "#DDA0DD", "value": "exercise"}
        ]
        
        # 绑定点击事件
        self.bind("<Button-1>", self._on_click)
        
        # 绘制转盘
        self._draw_wheel()
    
    def _draw_wheel(self):
        """绘制转盘"""
        self.delete("all")
        
        # 绘制转盘背景
        self.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            fill="#2B2B2B",
            outline="#FFFFFF",
            width=3
        )
        
        # 绘制扇形区域
        angle_per_section = 360 / len(self.options)
        
        for i, option in enumerate(self.options):
            start_angle = i * angle_per_section + self.current_angle
            end_angle = (i + 1) * angle_per_section + self.current_angle
            
            # 绘制扇形
            self.create_arc(
                self.center_x - self.radius + 10,
                self.center_y - self.radius + 10,
                self.center_x + self.radius - 10,
                self.center_y + self.radius - 10,
                start=start_angle,
                extent=angle_per_section,
                fill=option["color"],
                outline="#FFFFFF",
                width=2
            )
            
            # 绘制文字
            text_angle = start_angle + angle_per_section / 2
            text_radius = self.radius * 0.7
            
            text_x = self.center_x + text_radius * math.cos(math.radians(text_angle))
            text_y = self.center_y + text_radius * math.sin(math.radians(text_angle))
            
            self.create_text(
                text_x, text_y,
                text=option["text"],
                fill="#FFFFFF",
                font=("Arial", 10, "bold"),
                angle=text_angle
            )
        
        # 绘制中心圆
        self.create_oval(
            self.center_x - 20,
            self.center_y - 20,
            self.center_x + 20,
            self.center_y + 20,
            fill="#FF6B6B",
            outline="#FFFFFF",
            width=2
        )
        
        # 绘制指针
        pointer_length = self.radius - 30
        pointer_x = self.center_x + pointer_length * math.cos(math.radians(self.current_angle))
        pointer_y = self.center_y + pointer_length * math.sin(math.radians(self.current_angle))
        
        self.create_line(
            self.center_x, self.center_y,
            pointer_x, pointer_y,
            fill="#FFFFFF",
            width=4
        )
    
    def _on_click(self, event):
        """点击转盘开始旋转"""
        if not self.is_spinning:
            self.spin()
    
    def spin(self):
        """开始旋转"""
        if self.is_spinning:
            return
        
        self.is_spinning = True
        self.spin_speed = random.uniform(15, 25)  # 初始速度
        self.target_angle = random.uniform(720, 1440)  # 随机旋转角度
        
        self._animate_spin()
    
    def _animate_spin(self):
        """动画旋转"""
        if not self.is_spinning:
            return
        
        # 更新角度
        self.current_angle += self.spin_speed
        self.current_angle %= 360
        
        # 减速
        self.spin_speed *= 0.95
        
        # 重绘转盘
        self._draw_wheel()
        
        # 检查是否停止
        if self.spin_speed < 0.1:
            self.is_spinning = False
            self._on_spin_complete()
        else:
            self.after(50, self._animate_spin)
    
    def _on_spin_complete(self):
        """旋转完成回调"""
        # 计算选中的选项
        angle_per_section = 360 / len(self.options)
        selected_index = int(self.current_angle // angle_per_section)
        selected_option = self.options[selected_index]
        
        # 触发回调
        if hasattr(self, 'on_spin_complete'):
            self.on_spin_complete(selected_option)


class UserInfoForm(ctk.CTkFrame):
    """用户信息录入/修改表单"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.user_data = {}
        self._create_widgets()
    
    def _create_widgets(self):
        """创建表单组件"""
        # 标题
        title_label = ctk.CTkLabel(
            self,
            text="📝 个人信息管理",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # 表单框架
        form_frame = ctk.CTkScrollableFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 基本信息
        self._create_basic_info_section(form_frame)
        
        # 健康信息
        self._create_health_info_section(form_frame)
        
        # 饮食偏好
        self._create_diet_preferences_section(form_frame)
        
        # 按钮区域
        self._create_buttons(form_frame)
    
    def _create_basic_info_section(self, parent):
        """创建基本信息区域"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # 标题
        title = ctk.CTkLabel(
            section_frame,
            text="👤 基本信息",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # 信息网格
        info_frame = ctk.CTkFrame(section_frame)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        # 姓名
        name_label = ctk.CTkLabel(info_frame, text="姓名:")
        name_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.name_var = tk.StringVar()
        name_entry = ctk.CTkEntry(info_frame, textvariable=self.name_var, width=200)
        name_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # 年龄
        age_label = ctk.CTkLabel(info_frame, text="年龄:")
        age_label.grid(row=0, column=2, sticky="w", padx=10, pady=5)
        
        self.age_var = tk.StringVar(value="25")
        age_entry = ctk.CTkEntry(info_frame, textvariable=self.age_var, width=100)
        age_entry.grid(row=0, column=3, sticky="w", padx=10, pady=5)
        
        # 性别
        gender_label = ctk.CTkLabel(info_frame, text="性别:")
        gender_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.gender_var = tk.StringVar(value="女")
        gender_menu = ctk.CTkOptionMenu(
            info_frame,
            variable=self.gender_var,
            values=["男", "女"]
        )
        gender_menu.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # 身高体重
        height_label = ctk.CTkLabel(info_frame, text="身高(cm):")
        height_label.grid(row=1, column=2, sticky="w", padx=10, pady=5)
        
        self.height_var = tk.StringVar(value="165")
        height_entry = ctk.CTkEntry(info_frame, textvariable=self.height_var, width=100)
        height_entry.grid(row=1, column=3, sticky="w", padx=10, pady=5)
        
        weight_label = ctk.CTkLabel(info_frame, text="体重(kg):")
        weight_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        self.weight_var = tk.StringVar(value="55")
        weight_entry = ctk.CTkEntry(info_frame, textvariable=self.weight_var, width=100)
        weight_entry.grid(row=2, column=1, sticky="w", padx=10, pady=5)
    
    def _create_health_info_section(self, parent):
        """创建健康信息区域"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # 标题
        title = ctk.CTkLabel(
            section_frame,
            text="🏥 健康信息",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # 健康信息网格
        health_frame = ctk.CTkFrame(section_frame)
        health_frame.pack(fill="x", padx=20, pady=10)
        
        # 活动水平
        activity_label = ctk.CTkLabel(health_frame, text="活动水平:")
        activity_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.activity_var = tk.StringVar(value="中等")
        activity_menu = ctk.CTkOptionMenu(
            health_frame,
            variable=self.activity_var,
            values=["久坐", "轻度活动", "中等", "高度活动", "极度活动"]
        )
        activity_menu.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # 健康目标
        goal_label = ctk.CTkLabel(health_frame, text="健康目标:")
        goal_label.grid(row=0, column=2, sticky="w", padx=10, pady=5)
        
        self.goal_var = tk.StringVar(value="保持健康")
        goal_menu = ctk.CTkOptionMenu(
            health_frame,
            variable=self.goal_var,
            values=["保持健康", "减重", "增重", "增肌", "改善消化", "提高免疫力"]
        )
        goal_menu.grid(row=0, column=3, sticky="w", padx=10, pady=5)
        
        # 过敏信息
        allergy_label = ctk.CTkLabel(health_frame, text="过敏食物:")
        allergy_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.allergy_var = tk.StringVar(value="无")
        allergy_entry = ctk.CTkEntry(health_frame, textvariable=self.allergy_var, width=200)
        allergy_entry.grid(row=1, column=1, columnspan=2, sticky="w", padx=10, pady=5)
    
    def _create_diet_preferences_section(self, parent):
        """创建饮食偏好区域"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # 标题
        title = ctk.CTkLabel(
            section_frame,
            text="🍽️ 饮食偏好",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # 偏好网格
        pref_frame = ctk.CTkFrame(section_frame)
        pref_frame.pack(fill="x", padx=20, pady=10)
        
        # 口味偏好
        taste_label = ctk.CTkLabel(pref_frame, text="主要口味:")
        taste_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.taste_var = tk.StringVar(value="均衡")
        taste_menu = ctk.CTkOptionMenu(
            pref_frame,
            variable=self.taste_var,
            values=["均衡", "偏甜", "偏咸", "偏辣", "偏酸", "偏清淡"]
        )
        taste_menu.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # 饮食类型
        diet_label = ctk.CTkLabel(pref_frame, text="饮食类型:")
        diet_label.grid(row=0, column=2, sticky="w", padx=10, pady=5)
        
        self.diet_var = tk.StringVar(value="普通饮食")
        diet_menu = ctk.CTkOptionMenu(
            pref_frame,
            variable=self.diet_var,
            values=["普通饮食", "素食", "低脂饮食", "低糖饮食", "高蛋白饮食"]
        )
        diet_menu.grid(row=0, column=3, sticky="w", padx=10, pady=5)
        
        # 不喜欢食物
        dislike_label = ctk.CTkLabel(pref_frame, text="不喜欢食物:")
        dislike_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.dislike_var = tk.StringVar(value="无")
        dislike_entry = ctk.CTkEntry(pref_frame, textvariable=self.dislike_var, width=200)
        dislike_entry.grid(row=1, column=1, columnspan=2, sticky="w", padx=10, pady=5)
    
    def _create_buttons(self, parent):
        """创建按钮区域"""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", padx=10, pady=20)
        
        # 保存按钮
        save_button = ctk.CTkButton(
            button_frame,
            text="💾 保存信息",
            command=self._save_data,
            width=150,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        save_button.pack(side="left", padx=20, pady=10)
        
        # 加载按钮
        load_button = ctk.CTkButton(
            button_frame,
            text="📂 加载信息",
            command=self._load_data,
            width=150,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        load_button.pack(side="left", padx=20, pady=10)
        
        # 重置按钮
        reset_button = ctk.CTkButton(
            button_frame,
            text="🔄 重置表单",
            command=self._reset_form,
            width=150,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        reset_button.pack(side="right", padx=20, pady=10)
    
    def _save_data(self):
        """保存数据"""
        try:
            self.user_data = {
                'basic_info': {
                    'name': self.name_var.get(),
                    'age': int(self.age_var.get()),
                    'gender': self.gender_var.get(),
                    'height': int(self.height_var.get()),
                    'weight': int(self.weight_var.get())
                },
                'health_info': {
                    'activity_level': self.activity_var.get(),
                    'health_goal': self.goal_var.get(),
                    'allergies': self.allergy_var.get()
                },
                'diet_preferences': {
                    'taste': self.taste_var.get(),
                    'diet_type': self.diet_var.get(),
                    'dislikes': self.dislike_var.get()
                },
                'saved_at': datetime.now().isoformat()
            }
            
            # 保存到文件
            with open('data/user_info.json', 'w', encoding='utf-8') as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("成功", "信息保存成功！")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def _load_data(self):
        """加载数据"""
        try:
            with open('data/user_info.json', 'r', encoding='utf-8') as f:
                self.user_data = json.load(f)
            
            # 填充表单
            basic_info = self.user_data.get('basic_info', {})
            self.name_var.set(basic_info.get('name', ''))
            self.age_var.set(str(basic_info.get('age', 25)))
            self.gender_var.set(basic_info.get('gender', '女'))
            self.height_var.set(str(basic_info.get('height', 165)))
            self.weight_var.set(str(basic_info.get('weight', 55)))
            
            health_info = self.user_data.get('health_info', {})
            self.activity_var.set(health_info.get('activity_level', '中等'))
            self.goal_var.set(health_info.get('health_goal', '保持健康'))
            self.allergy_var.set(health_info.get('allergies', '无'))
            
            diet_prefs = self.user_data.get('diet_preferences', {})
            self.taste_var.set(diet_prefs.get('taste', '均衡'))
            self.diet_var.set(diet_prefs.get('diet_type', '普通饮食'))
            self.dislike_var.set(diet_prefs.get('dislikes', '无'))
            
            messagebox.showinfo("成功", "信息加载成功！")
            
        except FileNotFoundError:
            messagebox.showwarning("警告", "未找到保存的信息文件")
        except Exception as e:
            messagebox.showerror("错误", f"加载失败: {str(e)}")
    
    def _reset_form(self):
        """重置表单"""
        self.name_var.set("")
        self.age_var.set("25")
        self.gender_var.set("女")
        self.height_var.set("165")
        self.weight_var.set("55")
        self.activity_var.set("中等")
        self.goal_var.set("保持健康")
        self.allergy_var.set("无")
        self.taste_var.set("均衡")
        self.diet_var.set("普通饮食")
        self.dislike_var.set("无")


class NewMainWindow(ctk.CTk):
    """新的主窗口 - 信息录入/修改 + 随机转盘/扭蛋机"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口
        self.title("🍎 智能饮食推荐助手")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # 创建界面
        self._create_widgets()
        
        # 设置转盘回调
        self.spin_wheel.on_spin_complete = self._on_spin_complete
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主标题
        title_label = ctk.CTkLabel(
            self,
            text="🎯 智能饮食推荐助手",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=20)
        
        # 主内容区域
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 左侧 - 信息录入区域
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.user_info_form = UserInfoForm(left_frame)
        self.user_info_form.pack(fill="both", expand=True)
        
        # 右侧 - 转盘区域
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", padx=(10, 0))
        
        # 转盘标题
        wheel_title = ctk.CTkLabel(
            right_frame,
            text="🎰 随机推荐转盘",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        wheel_title.pack(pady=20)
        
        # 转盘说明
        wheel_desc = ctk.CTkLabel(
            right_frame,
            text="点击转盘开始随机推荐！",
            font=ctk.CTkFont(size=14)
        )
        wheel_desc.pack(pady=10)
        
        # 转盘组件
        self.spin_wheel = SpinWheel(right_frame, width=350, height=350)
        self.spin_wheel.pack(pady=20)
        
        # 结果显示区域
        self.result_frame = ctk.CTkFrame(right_frame)
        self.result_frame.pack(fill="x", padx=20, pady=20)
        
        self.result_label = ctk.CTkLabel(
            self.result_frame,
            text="等待转盘结果...",
            font=ctk.CTkFont(size=16),
            wraplength=300
        )
        self.result_label.pack(pady=20)
        
        # 底部状态栏
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.pack(fill="x", padx=20, pady=10)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="就绪",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)
    
    def _on_spin_complete(self, selected_option):
        """转盘完成回调"""
        self._update_status(f"转盘选中: {selected_option['text']}")
        
        # 显示结果
        result_text = f"🎯 推荐结果: {selected_option['text']}\n\n"
        
        # 根据选中的选项生成具体建议
        if selected_option['value'] == 'breakfast':
            result_text += "🌅 早餐建议:\n"
            result_text += "• 燕麦粥 + 牛奶 + 香蕉\n"
            result_text += "• 全麦面包 + 鸡蛋 + 蔬菜\n"
            result_text += "• 小米粥 + 咸菜 + 煮蛋"
        elif selected_option['value'] == 'lunch':
            result_text += "🌞 午餐建议:\n"
            result_text += "• 米饭 + 鸡肉 + 青菜\n"
            result_text += "• 面条 + 牛肉 + 西红柿\n"
            result_text += "• 饺子 + 汤"
        elif selected_option['value'] == 'dinner':
            result_text += "🌙 晚餐建议:\n"
            result_text += "• 粥 + 咸菜 + 豆腐\n"
            result_text += "• 蒸蛋 + 青菜 + 汤\n"
            result_text += "• 面条 + 蔬菜"
        elif selected_option['value'] == 'health':
            result_text += "🏥 健康建议:\n"
            result_text += "• 多喝水，保持水分平衡\n"
            result_text += "• 适量运动，增强体质\n"
            result_text += "• 规律作息，保证睡眠"
        elif selected_option['value'] == 'nutrition':
            result_text += "🥗 营养建议:\n"
            result_text += "• 多吃蔬菜水果\n"
            result_text += "• 适量蛋白质摄入\n"
            result_text += "• 控制糖分和盐分"
        elif selected_option['value'] == 'exercise':
            result_text += "🏃 运动建议:\n"
            result_text += "• 每天30分钟有氧运动\n"
            result_text += "• 适量力量训练\n"
            result_text += "• 注意运动前后拉伸"
        
        self.result_label.configure(text=result_text)
    
    def _update_status(self, message):
        """更新状态栏"""
        self.status_label.configure(text=f"{datetime.now().strftime('%H:%M:%S')} - {message}")


def main():
    """主函数"""
    app = NewMainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
