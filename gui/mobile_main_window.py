"""
移动端界面设计 - 小程序/安卓App尺寸
适配手机屏幕的饮食推荐应用界面
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
import threading
from typing import Dict, List, Optional, Any
from core.base import AppCore, UserData, ModuleType
from gui.styles import StyleConfig, apply_rounded_theme, create_card_frame, create_accent_button, create_rounded_entry, create_rounded_label

class MobileMainWindow:
    """移动端主窗口 - 模拟小程序/安卓App界面"""
    
    def __init__(self, app_core=None):
        # 移动端尺寸设置
        self.width = 375  # iPhone标准宽度
        self.height = 812  # iPhone标准高度
        
        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("饮食推荐助手")
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.resizable(False, False)
        
        # 应用核心
        self.app_core = app_core
        self.current_user_id = None
        self.current_user_data = None
        
        # 当前页面
        self.current_page = "home"
        
        # 应用圆角主题
        apply_rounded_theme()
        
        # 创建界面
        self._create_mobile_ui()
        
        # 初始化应用
        self._initialize_app()
    
    def _create_mobile_ui(self):
        """创建移动端界面"""
        # 主容器 - 增加圆角和内边距
        self.main_container = ctk.CTkFrame(
            self.root,
            corner_radius=20,
            fg_color=("#f8f9fa", "#1e1e1e")
        )
        self.main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 状态栏（模拟手机状态栏）
        self._create_status_bar()
        
        # 页面容器 - 增加圆角和阴影效果
        self.page_container = ctk.CTkFrame(
            self.main_container,
            corner_radius=25,
            fg_color=("#ffffff", "#2b2b2b"),
            border_width=1,
            border_color=("#e0e0e0", "#404040")
        )
        self.page_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # 底部导航栏
        self._create_bottom_navigation()
        
        # 创建各个页面
        self._create_home_page()
        self._create_record_page()
        self._create_recommend_page()
        self._create_profile_page()
        
        # 默认显示首页
        self._show_page("home")
    
    def _create_status_bar(self):
        """创建状态栏"""
        status_frame = ctk.CTkFrame(
            self.main_container, 
            height=35, 
            corner_radius=15,
            fg_color=("transparent", "transparent")
        )
        status_frame.pack(fill="x", padx=10, pady=(5, 0))
        status_frame.pack_propagate(False)
        
        # 时间显示
        self.time_label = ctk.CTkLabel(
            status_frame, 
            text="12:34", 
            font=("Arial", 13, "bold"),
            text_color=("#333333", "#ffffff")
        )
        self.time_label.pack(side="left", padx=15, pady=8)
        
        # 信号和电池图标（模拟）
        signal_label = ctk.CTkLabel(
            status_frame, 
            text="📶", 
            font=("Arial", 12),
            text_color=("#333333", "#ffffff")
        )
        signal_label.pack(side="right", padx=8, pady=8)
        
        battery_label = ctk.CTkLabel(
            status_frame, 
            text="🔋", 
            font=("Arial", 12),
            text_color=("#333333", "#ffffff")
        )
        battery_label.pack(side="right", padx=8, pady=8)
    
    def _create_bottom_navigation(self):
        """创建底部导航栏"""
        nav_frame = ctk.CTkFrame(
            self.main_container, 
            height=70, 
            corner_radius=20,
            fg_color=("#ffffff", "#2b2b2b"),
            border_width=1,
            border_color=("#e0e0e0", "#404040")
        )
        nav_frame.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
        nav_frame.pack_propagate(False)
        
        # 导航按钮
        nav_buttons = [
            ("🏠", "home", "首页"),
            ("📝", "record", "记录"),
            ("🎯", "recommend", "推荐"),
            ("👤", "profile", "我的")
        ]
        
        for icon, page, text in nav_buttons:
            btn = ctk.CTkButton(
                nav_frame,
                text=f"{icon}\n{text}",
                font=("Arial", 10),
                height=55,
                width=75,
                corner_radius=15,
                fg_color=("transparent", "transparent"),
                hover_color=("#f0f0f0", "#404040"),
                command=lambda p=page: self._show_page(p)
            )
            btn.pack(side="left", padx=8, pady=8, expand=True, fill="x")
    
    def _create_home_page(self):
        """创建首页"""
        self.home_frame = ctk.CTkFrame(
            self.page_container,
            corner_radius=20,
            fg_color=("transparent", "transparent")
        )
        
        # 欢迎区域
        welcome_frame = ctk.CTkFrame(
            self.home_frame,
            corner_radius=25,
            fg_color=("#f8f9fa", "#2b2b2b"),
            border_width=1,
            border_color=("#e0e0e0", "#404040")
        )
        welcome_frame.pack(fill="x", padx=20, pady=(20, 15))
        
        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text="🍽️ 饮食推荐助手",
            font=("Arial", 22, "bold"),
            text_color=("#2c3e50", "#ecf0f1")
        )
        welcome_label.pack(pady=15)
        
        # 用户信息卡片
        self.user_card = ctk.CTkFrame(
            self.home_frame,
            corner_radius=20,
            fg_color=("#ffffff", "#3b3b3b"),
            border_width=1,
            border_color=("#e0e0e0", "#404040")
        )
        self.user_card.pack(fill="x", padx=20, pady=10)
        
        self.user_info_label = ctk.CTkLabel(
            self.user_card,
            text="请先登录",
            font=("Arial", 16),
            text_color=("#34495e", "#bdc3c7")
        )
        self.user_info_label.pack(pady=15)
        
        # 快速操作按钮
        quick_actions_frame = ctk.CTkFrame(
            self.home_frame,
            corner_radius=20,
            fg_color=("#f8f9fa", "#2b2b2b"),
            border_width=1,
            border_color=("#e0e0e0", "#404040")
        )
        quick_actions_frame.pack(fill="x", padx=20, pady=15)
        
        # 记录餐食按钮
        record_btn = ctk.CTkButton(
            quick_actions_frame,
            text="📝 记录餐食",
            font=("Arial", 15, "bold"),
            height=55,
            corner_radius=15,
            fg_color=("#3498db", "#2980b9"),
            hover_color=("#2980b9", "#1f618d"),
            text_color=("#ffffff", "#ffffff"),
            command=self._quick_record_meal
        )
        record_btn.pack(fill="x", padx=15, pady=(15, 8))
        
        # 获取推荐按钮
        recommend_btn = ctk.CTkButton(
            quick_actions_frame,
            text="🎯 获取推荐",
            font=("Arial", 15, "bold"),
            height=55,
            corner_radius=15,
            fg_color=("#e74c3c", "#c0392b"),
            hover_color=("#c0392b", "#a93226"),
            text_color=("#ffffff", "#ffffff"),
            command=self._quick_get_recommendation
        )
        recommend_btn.pack(fill="x", padx=15, pady=(8, 15))
        
        # 今日统计
        stats_frame = ctk.CTkFrame(
            self.home_frame,
            corner_radius=20,
            fg_color=("#ffffff", "#3b3b3b"),
            border_width=1,
            border_color=("#e0e0e0", "#404040")
        )
        stats_frame.pack(fill="x", padx=20, pady=15)
        
        stats_label = ctk.CTkLabel(
            stats_frame,
            text="📊 今日统计",
            font=("Arial", 16, "bold")
        )
        stats_label.pack(pady=5)
        
        self.stats_text = ctk.CTkTextbox(stats_frame, height=100)
        self.stats_text.pack(fill="x", padx=10, pady=5)
    
    def _create_record_page(self):
        """创建记录页面"""
        self.record_frame = ctk.CTkFrame(
            self.page_container,
            corner_radius=20,
            fg_color=("transparent", "transparent")
        )
        
        # 页面标题
        title_label = ctk.CTkLabel(
            self.record_frame,
            text="📝 记录餐食",
            font=("Arial", 20, "bold"),
            text_color=("#2c3e50", "#ecf0f1")
        )
        title_label.pack(pady=(20, 15))
        
        # 餐次选择
        meal_type_frame = ctk.CTkFrame(
            self.record_frame,
            corner_radius=15,
            fg_color=("#ffffff", "#3b3b3b"),
            border_width=1,
            border_color=("#e0e0e0", "#404040")
        )
        meal_type_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            meal_type_frame, 
            text="餐次:", 
            font=("Arial", 15),
            text_color=("#34495e", "#bdc3c7")
        ).pack(side="left", padx=15, pady=12)
        
        self.meal_type_var = ctk.StringVar(value="breakfast")
        meal_type_menu = ctk.CTkOptionMenu(
            meal_type_frame,
            variable=self.meal_type_var,
            values=["breakfast", "lunch", "dinner", "snack"],
            width=130,
            corner_radius=10,
            fg_color=("#3498db", "#2980b9"),
            button_color=("#2980b9", "#1f618d"),
            button_hover_color=("#1f618d", "#154360")
        )
        meal_type_menu.pack(side="right", padx=15, pady=8)
        
        # 食物输入
        food_frame = ctk.CTkFrame(
            self.record_frame,
            corner_radius=15,
            fg_color=("#ffffff", "#3b3b3b"),
            border_width=1,
            border_color=("#e0e0e0", "#404040")
        )
        food_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            food_frame, 
            text="食物:", 
            font=("Arial", 15),
            text_color=("#34495e", "#bdc3c7")
        ).pack(anchor="w", padx=15, pady=(12, 5))
        
        # 食物输入框和转盘按钮
        food_input_frame = ctk.CTkFrame(
            food_frame,
            corner_radius=10,
            fg_color=("transparent", "transparent")
        )
        food_input_frame.pack(fill="x", padx=15, pady=(5, 12))
        
        self.food_entry = ctk.CTkEntry(
            food_input_frame, 
            placeholder_text="输入食物名称",
            corner_radius=12,
            height=40,
            font=("Arial", 14),
            fg_color=("#f8f9fa", "#404040"),
            border_width=1,
            border_color=("#e0e0e0", "#555555")
        )
        self.food_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        # 转盘按钮和OCR按钮
        button_frame = ctk.CTkFrame(
            food_input_frame,
            corner_radius=10,
            fg_color=("transparent", "transparent")
        )
        button_frame.pack(side="right")
        
        roulette_btn = ctk.CTkButton(
            button_frame, 
            text="🎲", 
            width=40, 
            height=40,
            corner_radius=12,
            fg_color=("#f39c12", "#e67e22"),
            hover_color=("#e67e22", "#d35400"),
            command=self._show_food_roulette
        )
        roulette_btn.pack(side="left", padx=(0, 4))
        
        ocr_btn = ctk.CTkButton(
            button_frame, 
            text="📷", 
            width=40, 
            height=40,
            corner_radius=12,
            fg_color=("#9b59b6", "#8e44ad"),
            hover_color=("#8e44ad", "#7d3c98"),
            command=self._show_ocr_recognition
        )
        ocr_btn.pack(side="right", padx=(4, 0))
        
        # 分量输入
        quantity_frame = ctk.CTkFrame(self.record_frame)
        quantity_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(quantity_frame, text="分量:", font=("Arial", 14)).pack(anchor="w", padx=10, pady=5)
        self.quantity_entry = ctk.CTkEntry(quantity_frame, placeholder_text="如：1碗、200g")
        self.quantity_entry.pack(fill="x", padx=10, pady=5)
        
        # 热量显示
        calorie_frame = ctk.CTkFrame(self.record_frame)
        calorie_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(calorie_frame, text="热量:", font=("Arial", 14)).pack(anchor="w", padx=10, pady=5)
        self.calorie_display = ctk.CTkLabel(calorie_frame, text="0 卡路里", font=("Arial", 16, "bold"))
        self.calorie_display.pack(anchor="w", padx=10, pady=5)
        
        # 满意度评分
        satisfaction_frame = ctk.CTkFrame(self.record_frame)
        satisfaction_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(satisfaction_frame, text="满意度:", font=("Arial", 14)).pack(anchor="w", padx=10, pady=5)
        
        self.satisfaction_var = ctk.IntVar(value=4)
        satisfaction_slider = ctk.CTkSlider(
            satisfaction_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            variable=self.satisfaction_var
        )
        satisfaction_slider.pack(fill="x", padx=10, pady=5)
        
        satisfaction_label = ctk.CTkLabel(satisfaction_frame, text="4分")
        satisfaction_label.pack()
        
        # 保存按钮
        save_btn = ctk.CTkButton(
            self.record_frame,
            text="💾 保存记录",
            font=("Arial", 14, "bold"),
            height=50,
            command=self._save_meal_record
        )
        save_btn.pack(fill="x", padx=15, pady=15)
        
        # 绑定食物输入变化事件
        self.food_entry.bind("<KeyRelease>", self._on_food_input_change)
        self.quantity_entry.bind("<KeyRelease>", self._on_food_input_change)
    
    def _show_ocr_recognition(self):
        """显示OCR识别界面"""
        try:
            # 创建OCR识别窗口
            ocr_window = ctk.CTkToplevel(self.root)
            ocr_window.title("📷 OCR热量识别")
            ocr_window.geometry("400x500")
            ocr_window.resizable(False, False)
            
            # 居中显示
            ocr_window.transient(self.root)
            ocr_window.grab_set()
            
            # 创建OCR界面
            from gui.ocr_calorie_gui import OCRCalorieGUI
            ocr_gui = OCRCalorieGUI(ocr_window, self.app_core)
            
        except Exception as e:
            messagebox.showerror("错误", f"打开OCR识别界面失败: {str(e)}")
    
    def _create_recommend_page(self):
        """创建推荐页面"""
        self.recommend_frame = ctk.CTkFrame(self.page_container)
        
        # 页面标题
        title_label = ctk.CTkLabel(
            self.recommend_frame,
            text="🎯 个性化推荐",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=15)
        
        # 推荐设置
        settings_frame = ctk.CTkFrame(self.recommend_frame)
        settings_frame.pack(fill="x", padx=15, pady=10)
        
        # 餐次选择
        meal_type_row = ctk.CTkFrame(settings_frame)
        meal_type_row.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(meal_type_row, text="餐次:", font=("Arial", 14)).pack(side="left")
        
        self.rec_meal_type_var = ctk.StringVar(value="lunch")
        rec_meal_type_menu = ctk.CTkOptionMenu(
            meal_type_row,
            variable=self.rec_meal_type_var,
            values=["breakfast", "lunch", "dinner", "snack"],
            width=120
        )
        rec_meal_type_menu.pack(side="right")
        
        # 口味偏好
        taste_row = ctk.CTkFrame(settings_frame)
        taste_row.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(taste_row, text="口味:", font=("Arial", 14)).pack(side="left")
        
        self.taste_var = ctk.StringVar(value="balanced")
        taste_menu = ctk.CTkOptionMenu(
            taste_row,
            variable=self.taste_var,
            values=["balanced", "sweet", "salty", "spicy", "sour"],
            width=120
        )
        taste_menu.pack(side="right")
        
        # 生成推荐按钮
        generate_btn = ctk.CTkButton(
            self.recommend_frame,
            text="🎲 生成推荐",
            font=("Arial", 14, "bold"),
            height=50,
            command=self._generate_recommendations
        )
        generate_btn.pack(fill="x", padx=15, pady=15)
        
        # 推荐结果
        result_frame = ctk.CTkFrame(self.recommend_frame)
        result_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.recommendation_text = ctk.CTkTextbox(result_frame, height=300)
        self.recommendation_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _create_profile_page(self):
        """创建个人中心页面"""
        self.profile_frame = ctk.CTkFrame(self.page_container)
        
        # 页面标题
        title_label = ctk.CTkLabel(
            self.profile_frame,
            text="👤 个人中心",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=15)
        
        # 用户信息卡片
        user_info_frame = ctk.CTkFrame(self.profile_frame)
        user_info_frame.pack(fill="x", padx=15, pady=10)
        
        self.profile_user_label = ctk.CTkLabel(
            user_info_frame,
            text="请先登录",
            font=("Arial", 16, "bold")
        )
        self.profile_user_label.pack(pady=10)
        
        # 登录/注册按钮
        login_btn = ctk.CTkButton(
            self.profile_frame,
            text="🔑 登录/注册",
            font=("Arial", 14, "bold"),
            height=50,
            command=self._show_login_dialog
        )
        login_btn.pack(fill="x", padx=15, pady=10)
        
        # 功能菜单
        menu_frame = ctk.CTkFrame(self.profile_frame)
        menu_frame.pack(fill="x", padx=15, pady=10)
        
        menu_items = [
            ("📊 数据统计", self._show_data_stats),
            ("⚙️ 设置", self._show_settings),
            ("❓ 帮助", self._show_help),
            ("📞 联系我们", self._show_contact)
        ]
        
        for text, command in menu_items:
            btn = ctk.CTkButton(
                menu_frame,
                text=text,
                font=("Arial", 14),
                height=40,
                command=command
            )
            btn.pack(fill="x", pady=2)
    
    def _show_page(self, page_name: str):
        """显示指定页面"""
        # 隐藏所有页面
        for frame in [self.home_frame, self.record_frame, self.recommend_frame, self.profile_frame]:
            frame.pack_forget()
        
        # 显示指定页面
        if page_name == "home":
            self.home_frame.pack(fill="both", expand=True)
        elif page_name == "record":
            self.record_frame.pack(fill="both", expand=True)
        elif page_name == "recommend":
            self.recommend_frame.pack(fill="both", expand=True)
        elif page_name == "profile":
            self.profile_frame.pack(fill="both", expand=True)
        
        self.current_page = page_name
    
    def _initialize_app(self):
        """初始化应用"""
        if self.app_core:
            self._update_status("应用核心已就绪")
        else:
            self._update_status("应用核心未初始化")
    
    def _update_status(self, message: str):
        """更新状态信息"""
        print(f"状态: {message}")
    
    def _quick_record_meal(self):
        """快速记录餐食"""
        self._show_page("record")
    
    def _quick_get_recommendation(self):
        """快速获取推荐"""
        self._show_page("recommend")
    
    def _save_meal_record(self):
        """保存餐食记录"""
        if not self.current_user_id:
            messagebox.showwarning("警告", "请先登录")
            return
        
        food = self.food_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        meal_type = self.meal_type_var.get()
        satisfaction = self.satisfaction_var.get()
        
        if not food or not quantity:
            messagebox.showwarning("警告", "请填写完整信息")
            return
        
        try:
            meal_data = {
                'meal_type': meal_type,
                'foods': [food],
                'quantities': [quantity],
                'satisfaction_score': satisfaction
            }
            
            if self.app_core and self.app_core.module_manager:
                result = self.app_core.process_user_request(
                    ModuleType.DATA_COLLECTION,
                    {'type': 'meal_record', 'meal_data': meal_data},
                    self.current_user_id
                )
                
                if result and result.result.get('success'):
                    messagebox.showinfo("成功", "餐食记录保存成功")
                    self.food_entry.delete(0, "end")
                    self.quantity_entry.delete(0, "end")
                    
                    # 同步更新用户数据
                    self._refresh_user_data()
                    
                    # 如果当前在首页，更新统计信息
                    if self.current_page == "home":
                        self._update_stats()
                        
                else:
                    messagebox.showerror("错误", "餐食记录保存失败")
            else:
                messagebox.showerror("错误", "应用核心未初始化")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def _generate_recommendations(self):
        """生成推荐"""
        if not self.current_user_id:
            messagebox.showwarning("警告", "请先登录")
            return
        
        self.recommendation_text.delete("1.0", "end")
        self.recommendation_text.insert("1.0", "正在生成推荐...")
        
        def recommend_thread():
            try:
                meal_type = self.rec_meal_type_var.get()
                preferences = {'taste': self.taste_var.get()}
                
                if self.app_core and self.app_core.module_manager:
                    result = self.app_core.process_user_request(
                        ModuleType.RECOMMENDATION,
                        {
                            'type': 'meal_recommendation',
                            'meal_type': meal_type,
                            'preferences': preferences,
                            'context': {}
                        },
                        self.current_user_id
                    )
                    
                    if result and result.result.get('success'):
                        recommendations = result.result.get('recommendations', [])
                        reasoning = result.result.get('reasoning', '无')
                        confidence = result.result.get('confidence', 0)
                        
                        content = f"推荐理由: {reasoning}\n\n"
                        content += f"置信度: {confidence:.2f}\n\n"
                        content += "推荐餐食搭配:\n\n"
                        
                        for i, combo in enumerate(recommendations, 1):
                            content += f"{i}. {combo.get('name', '搭配')}\n"
                            foods = [f['name'] for f in combo.get('foods', [])]
                            content += f"   食物: {', '.join(foods)}\n"
                            content += f"   热量: {combo.get('total_calories', 0):.0f}卡路里\n\n"
                        
                        self.root.after(0, lambda: self.recommendation_text.delete("1.0", "end"))
                        self.root.after(0, lambda: self.recommendation_text.insert("1.0", content))
                    else:
                        error_msg = result.result.get('error', '未知错误') if result else '无结果'
                        self.root.after(0, lambda: self.recommendation_text.delete("1.0", "end"))
                        self.root.after(0, lambda: self.recommendation_text.insert("1.0", f"推荐失败: {error_msg}"))
                else:
                    self.root.after(0, lambda: self.recommendation_text.delete("1.0", "end"))
                    self.root.after(0, lambda: self.recommendation_text.insert("1.0", "应用核心未初始化"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.recommendation_text.delete("1.0", "end"))
                self.root.after(0, lambda: self.recommendation_text.insert("1.0", f"推荐生成错误: {str(e)}"))
        
        threading.Thread(target=recommend_thread, daemon=True).start()
    
    def _show_login_dialog(self):
        """显示登录对话框"""
        dialog = MobileLoginDialog(self.root, self)
        dialog.show()
    
    def _show_data_stats(self):
        """显示数据统计"""
        if not self.current_user_data:
            messagebox.showwarning("警告", "请先登录")
            return
        
        # 创建统计窗口
        stats_window = ctk.CTkToplevel(self.root)
        stats_window.title("数据统计")
        stats_window.geometry("350x500")
        stats_window.resizable(False, False)
        
        # 主容器
        main_frame = ctk.CTkScrollableFrame(stats_window, width=320, height=450)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 标题
        title_label = ctk.CTkLabel(main_frame, text="📊 数据统计", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # 基础统计
        basic_frame = ctk.CTkFrame(main_frame)
        basic_frame.pack(fill="x", pady=(0, 10))
        
        basic_title = ctk.CTkLabel(basic_frame, text="基础统计", font=ctk.CTkFont(size=16, weight="bold"))
        basic_title.pack(pady=10)
        
        # 餐食记录统计
        meal_count = len(self.current_user_data.meals)
        meal_label = ctk.CTkLabel(basic_frame, text=f"餐食记录: {meal_count}条")
        meal_label.pack(pady=2)
        
        # 反馈记录统计
        feedback_count = len(self.current_user_data.feedback)
        feedback_label = ctk.CTkLabel(basic_frame, text=f"反馈记录: {feedback_count}条")
        feedback_label.pack(pady=2)
        
        # 满意度统计
        if self.current_user_data.meals:
            satisfaction_scores = [meal.get('satisfaction_score', 0) for meal in self.current_user_data.meals if meal.get('satisfaction_score')]
            if satisfaction_scores:
                avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)
                satisfaction_label = ctk.CTkLabel(basic_frame, text=f"平均满意度: {avg_satisfaction:.1f}分")
                satisfaction_label.pack(pady=2)
        
        # 餐次分布统计
        meal_dist_frame = ctk.CTkFrame(main_frame)
        meal_dist_frame.pack(fill="x", pady=(0, 10))
        
        meal_dist_title = ctk.CTkLabel(meal_dist_frame, text="餐次分布", font=ctk.CTkFont(size=16, weight="bold"))
        meal_dist_title.pack(pady=10)
        
        meal_types = {}
        for meal in self.current_user_data.meals:
            meal_type = meal.get('meal_type', 'unknown')
            meal_types[meal_type] = meal_types.get(meal_type, 0) + 1
        
        for meal_type, count in meal_types.items():
            type_label = ctk.CTkLabel(meal_dist_frame, text=f"{meal_type}: {count}次")
            type_label.pack(pady=2)
        
        # 最近餐食
        recent_frame = ctk.CTkFrame(main_frame)
        recent_frame.pack(fill="x", pady=(0, 10))
        
        recent_title = ctk.CTkLabel(recent_frame, text="最近餐食", font=ctk.CTkFont(size=16, weight="bold"))
        recent_title.pack(pady=10)
        
        recent_meals = sorted(self.current_user_data.meals, key=lambda x: x.get('date', ''), reverse=True)[:5]
        for meal in recent_meals:
            meal_text = f"{meal.get('date', '未知日期')} - {meal.get('meal_type', '未知餐次')}"
            if meal.get('foods'):
                meal_text += f" ({', '.join(meal['foods'])})"
            meal_label = ctk.CTkLabel(recent_frame, text=meal_text, wraplength=300)
            meal_label.pack(pady=2)
        
        # 关闭按钮
        close_btn = ctk.CTkButton(main_frame, text="关闭", command=stats_window.destroy)
        close_btn.pack(pady=20)
    
    def _show_settings(self):
        """显示设置"""
        if not self.current_user_data:
            messagebox.showwarning("警告", "请先登录")
            return
        
        # 创建设置窗口
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("350x400")
        settings_window.resizable(False, False)
        
        # 主容器
        main_frame = ctk.CTkScrollableFrame(settings_window, width=320, height=350)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 标题
        title_label = ctk.CTkLabel(main_frame, text="⚙️ 设置", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # 用户偏好设置
        pref_frame = ctk.CTkFrame(main_frame)
        pref_frame.pack(fill="x", pady=(0, 10))
        
        pref_title = ctk.CTkLabel(pref_frame, text="用户偏好", font=ctk.CTkFont(size=16, weight="bold"))
        pref_title.pack(pady=10)
        
        # 口味偏好
        taste_label = ctk.CTkLabel(pref_frame, text="口味偏好:")
        taste_label.pack(pady=(10, 5))
        
        taste_var = ctk.StringVar(value="balanced")
        taste_options = ["清淡", "适中", "重口味", "甜食", "咸食", "辣食"]
        taste_menu = ctk.CTkOptionMenu(pref_frame, variable=taste_var, values=taste_options)
        taste_menu.pack(pady=5)
        
        # 饮食目标
        goal_label = ctk.CTkLabel(pref_frame, text="饮食目标:")
        goal_label.pack(pady=(10, 5))
        
        goal_var = ctk.StringVar(value="maintain")
        goal_options = ["维持体重", "减重", "增重", "增肌", "健康饮食"]
        goal_menu = ctk.CTkOptionMenu(pref_frame, variable=goal_var, values=goal_options)
        goal_menu.pack(pady=5)
        
        # 过敏食物
        allergy_label = ctk.CTkLabel(pref_frame, text="过敏食物:")
        allergy_label.pack(pady=(10, 5))
        
        allergy_entry = ctk.CTkEntry(pref_frame, placeholder_text="请输入过敏食物，用逗号分隔")
        allergy_entry.pack(pady=5, fill="x")
        
        # 保存设置按钮
        def save_settings():
            try:
                preferences = {
                    'taste_preference': taste_var.get(),
                    'diet_goal': goal_var.get(),
                    'allergies': allergy_entry.get().strip()
                }
                
                # 保存到用户数据
                if self.app_core and self.app_core.data_manager:
                    # 更新用户偏好
                    self.current_user_data.preferences.update(preferences)
                    
                    # 保存到数据库
                    self.app_core.data_manager.save_user_data(self.current_user_data)
                    
                    messagebox.showinfo("成功", "设置保存成功")
                    settings_window.destroy()
                else:
                    messagebox.showerror("错误", "应用核心未初始化")
                    
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
        
        save_btn = ctk.CTkButton(pref_frame, text="保存设置", command=save_settings)
        save_btn.pack(pady=20)
        
        # 关闭按钮
        close_btn = ctk.CTkButton(main_frame, text="关闭", command=settings_window.destroy)
        close_btn.pack(pady=10)
    
    def _show_help(self):
        """显示帮助"""
        # 创建帮助窗口
        help_window = ctk.CTkToplevel(self.root)
        help_window.title("帮助")
        help_window.geometry("350x500")
        help_window.resizable(False, False)
        
        # 主容器
        main_frame = ctk.CTkScrollableFrame(help_window, width=320, height=450)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 标题
        title_label = ctk.CTkLabel(main_frame, text="❓ 使用帮助", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # 功能介绍
        features_frame = ctk.CTkFrame(main_frame)
        features_frame.pack(fill="x", pady=(0, 10))
        
        features_title = ctk.CTkLabel(features_frame, text="功能介绍", font=ctk.CTkFont(size=16, weight="bold"))
        features_title.pack(pady=10)
        
        features_text = """
🏠 首页
• 查看今日统计信息
• 快速记录餐食
• 获取个性化推荐

📝 记录
• 记录餐食信息
• 设置满意度评分
• 自动计算热量

🎯 推荐
• 个性化餐食推荐
• 基于历史数据
• 营养搭配建议

👤 个人中心
• 查看详细统计
• 设置个人偏好
• 管理账户信息
        """
        
        features_label = ctk.CTkLabel(features_frame, text=features_text, justify="left")
        features_label.pack(pady=10)
        
        # 使用说明
        usage_frame = ctk.CTkFrame(main_frame)
        usage_frame.pack(fill="x", pady=(0, 10))
        
        usage_title = ctk.CTkLabel(usage_frame, text="使用说明", font=ctk.CTkFont(size=16, weight="bold"))
        usage_title.pack(pady=10)
        
        usage_text = """
1. 首次使用请先登录
2. 在记录页面输入餐食信息
3. 在推荐页面获取建议
4. 定期查看统计了解饮食情况
5. 在设置中调整个人偏好
        """
        
        usage_label = ctk.CTkLabel(usage_frame, text=usage_text, justify="left")
        usage_label.pack(pady=10)
        
        # 关闭按钮
        close_btn = ctk.CTkButton(main_frame, text="关闭", command=help_window.destroy)
        close_btn.pack(pady=20)
    
    def _show_contact(self):
        """显示联系我们"""
        # 创建联系窗口
        contact_window = ctk.CTkToplevel(self.root)
        contact_window.title("联系我们")
        contact_window.geometry("350x300")
        contact_window.resizable(False, False)
        
        # 主容器
        main_frame = ctk.CTkFrame(contact_window)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # 标题
        title_label = ctk.CTkLabel(main_frame, text="📞 联系我们", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 30))
        
        # 联系方式
        contact_info = """
📧 邮箱支持
support@dietapp.com

📱 客服电话
400-123-4567
工作时间：9:00-18:00

💬 在线客服
微信：DietApp_Support

🌐 官方网站
www.dietapp.com

📝 意见反馈
feedback@dietapp.com
        """
        
        contact_label = ctk.CTkLabel(main_frame, text=contact_info, justify="left")
        contact_label.pack(pady=20)
        
        # 关闭按钮
        close_btn = ctk.CTkButton(main_frame, text="关闭", command=contact_window.destroy)
        close_btn.pack(pady=20)
    
    def set_current_user(self, user_id: str, user_data: UserData):
        """设置当前用户"""
        self.current_user_id = user_id
        self.current_user_data = user_data
        
        # 更新用户信息显示
        profile = user_data.profile
        user_info = f"👤 {profile.get('name', '未知用户')}\n"
        user_info += f"📊 餐食记录: {len(user_data.meals)}条\n"
        user_info += f"💬 反馈记录: {len(user_data.feedback)}条"
        
        self.user_info_label.configure(text=user_info)
        self.profile_user_label.configure(text=f"欢迎，{profile.get('name', '用户')}！")
        
        # 更新统计信息
        self._update_stats()
    
    def _refresh_user_data(self):
        """刷新用户数据"""
        if self.current_user_id and self.app_core:
            try:
                self.current_user_data = self.app_core.data_manager.get_user_data(self.current_user_id)
                self._update_status("用户数据已刷新")
            except Exception as e:
                self._update_status(f"数据刷新失败: {e}")
    
    def _on_food_input_change(self, event=None):
        """食物输入变化时更新热量"""
        food = self.food_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        
        if food and quantity and self.app_core:
            try:
                # 使用AI分析获取热量
                result = self.app_core.process_user_request(
                    ModuleType.USER_ANALYSIS,
                    {'type': 'calorie_estimation', 'food_data': {'food_name': food, 'quantity': quantity}},
                    self.current_user_id or "test"
                )
                
                if result and result.result.get('success'):
                    calories = result.result.get('calories', 0)
                    self.calorie_display.configure(text=f"{calories:.0f} 卡路里")
                else:
                    self.calorie_display.configure(text="热量计算中...")
                    
            except Exception as e:
                self.calorie_display.configure(text="热量计算失败")
    
    def _save_meal_record(self):
        """保存餐食记录"""
        if not self.current_user_id:
            messagebox.showwarning("警告", "请先登录")
            return
        
        food = self.food_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        meal_type = self.meal_type_var.get()
        satisfaction = self.satisfaction_var.get()
        
        if not food or not quantity:
            messagebox.showwarning("警告", "请填写完整信息")
            return
        
        try:
            meal_data = {
                'meal_type': meal_type,
                'foods': [food],
                'quantities': [quantity],
                'satisfaction_score': satisfaction
            }
            
            if self.app_core and self.app_core.module_manager:
                result = self.app_core.process_user_request(
                    ModuleType.DATA_COLLECTION,
                    {'type': 'meal_record', 'meal_data': meal_data},
                    self.current_user_id
                )
                
                if result and result.result.get('success'):
                    messagebox.showinfo("成功", "餐食记录保存成功")
                    self.food_entry.delete(0, "end")
                    self.quantity_entry.delete(0, "end")
                    
                    # 同步更新用户数据
                    self._refresh_user_data()
                    
                    # 如果当前在首页，更新统计信息
                    if self.current_page == "home":
                        self._update_stats()
                        
                else:
                    messagebox.showerror("错误", "餐食记录保存失败")
            else:
                messagebox.showerror("错误", "应用核心未初始化")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def _show_food_roulette(self):
        """显示食物转盘"""
        # 创建转盘窗口
        roulette_window = ctk.CTkToplevel(self.root)
        roulette_window.title("食物转盘")
        roulette_window.geometry("300x400")
        roulette_window.resizable(False, False)
        
        # 主容器
        main_frame = ctk.CTkFrame(roulette_window)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # 标题
        title_label = ctk.CTkLabel(main_frame, text="🎲 食物转盘", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # 转盘显示区域
        roulette_frame = ctk.CTkFrame(main_frame)
        roulette_frame.pack(fill="x", pady=20)
        
        self.roulette_display = ctk.CTkLabel(roulette_frame, text="点击开始转盘", font=ctk.CTkFont(size=16))
        self.roulette_display.pack(pady=20)
        
        # 食物列表
        food_list = [
            "米饭", "面条", "包子", "饺子", "馒头", "面包",
            "鸡蛋", "牛奶", "豆浆", "酸奶", "苹果", "香蕉",
            "鸡肉", "牛肉", "猪肉", "鱼肉", "豆腐", "青菜",
            "西红柿", "黄瓜", "胡萝卜", "土豆", "红薯", "玉米"
        ]
        
        # 转盘按钮
        def spin_roulette():
            import random
            import time
            
            self.roulette_display.configure(text="转盘中...")
            roulette_window.update()
            
            # 模拟转盘效果
            for _ in range(10):
                random_food = random.choice(food_list)
                self.roulette_display.configure(text=f"🎯 {random_food}")
                roulette_window.update()
                time.sleep(0.1)
            
            # 最终结果
            final_food = random.choice(food_list)
            self.roulette_display.configure(text=f"🎉 {final_food}")
            
            # 自动填入食物输入框
            self.food_entry.delete(0, "end")
            self.food_entry.insert(0, final_food)
            
            # 触发热量计算
            self._on_food_input_change()
        
        spin_btn = ctk.CTkButton(main_frame, text="🎲 开始转盘", command=spin_roulette, height=40)
        spin_btn.pack(pady=20)
        
        # 关闭按钮
        close_btn = ctk.CTkButton(main_frame, text="关闭", command=roulette_window.destroy)
        close_btn.pack(pady=10)
    
    def _update_stats(self):
        """更新统计信息"""
        if not self.current_user_data:
            return
        
        stats = f"📊 今日统计\n\n"
        stats += f"餐食记录: {len(self.current_user_data.meals)}条\n"
        stats += f"反馈记录: {len(self.current_user_data.feedback)}条\n"
        
        # 计算平均满意度
        if self.current_user_data.meals:
            satisfaction_scores = [meal.get('satisfaction_score', 0) for meal in self.current_user_data.meals if meal.get('satisfaction_score')]
            if satisfaction_scores:
                avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)
                stats += f"平均满意度: {avg_satisfaction:.1f}分\n"
        
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", stats)
    
    def _generate_recommendations(self):
        """生成推荐"""
        if not self.current_user_id:
            messagebox.showwarning("警告", "请先登录")
            return
        
        try:
            input_data = {
                'meal_type': self.rec_meal_type_var.get(),
                'preferences': {
                    'taste': self.taste_var.get(),
                    'health_goal': 'maintain'
                },
                'context': {
                    'time': '12:00',
                    'weather': 'sunny'
                }
            }
            
            if self.app_core and self.app_core.module_manager:
                result = self.app_core.process_user_request(
                    ModuleType.RECOMMENDATION,
                    {'type': 'meal_recommendation', 'input_data': input_data},
                    self.current_user_id
                )
                
                if result and result.result.get('success'):
                    recommendations = result.result.get('recommendations', [])
                    reasoning = result.result.get('reasoning', '无')
                    confidence = result.result.get('confidence', 0)
                    
                    # 显示推荐结果
                    self.recommendation_text.delete("1.0", "end")
                    content = f"推荐理由: {reasoning}\n\n"
                    content += f"置信度: {confidence:.2f}\n\n"
                    content += "推荐餐食搭配:\n\n"
                    
                    for i, combo in enumerate(recommendations[:3], 1):
                        content += f"{i}. {combo.get('name', '搭配')}\n"
                        content += f"   食物: {', '.join([f['name'] for f in combo.get('foods', [])])}\n"
                        content += f"   总热量: {combo.get('total_calories', 0):.0f}卡路里\n"
                        content += f"   营养得分: {combo.get('nutrition_score', 0):.2f}\n\n"
                    
                    self.recommendation_text.insert("1.0", content)
                else:
                    self.recommendation_text.delete("1.0", "end")
                    self.recommendation_text.insert("1.0", f"推荐失败: {result.result.get('error', '未知错误') if result else '无结果'}")
            else:
                messagebox.showerror("错误", "应用核心未初始化")
                
        except Exception as e:
            messagebox.showerror("错误", f"推荐生成失败: {str(e)}")
    
    def _quick_record_meal(self):
        """快速记录餐食"""
        self._show_page("record")
    
    def _quick_get_recommendation(self):
        """快速获取推荐"""
        self._show_page("recommend")
    
    def run(self):
        """运行应用"""
        self.root.mainloop()


class MobileLoginDialog:
    """移动端登录对话框"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        
        # 创建对话框
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("登录")
        self.dialog.geometry("300x400")
        self.dialog.resizable(False, False)
        
        # 居中显示
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_login_ui()
    
    def _create_login_ui(self):
        """创建登录界面"""
        # 标题
        title_label = ctk.CTkLabel(
            self.dialog,
            text="🔑 用户登录",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)
        
        # 用户ID输入
        user_id_frame = ctk.CTkFrame(self.dialog)
        user_id_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(user_id_frame, text="用户ID:", font=("Arial", 14)).pack(anchor="w", padx=10, pady=5)
        self.user_id_entry = ctk.CTkEntry(user_id_frame, placeholder_text="输入用户ID")
        self.user_id_entry.pack(fill="x", padx=10, pady=5)
        
        # 姓名输入
        name_frame = ctk.CTkFrame(self.dialog)
        name_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(name_frame, text="姓名:", font=("Arial", 14)).pack(anchor="w", padx=10, pady=5)
        self.name_entry = ctk.CTkEntry(name_frame, placeholder_text="输入姓名")
        self.name_entry.pack(fill="x", padx=10, pady=5)
        
        # 登录按钮
        login_btn = ctk.CTkButton(
            self.dialog,
            text="🚀 登录",
            font=("Arial", 14, "bold"),
            height=50,
            command=self._login
        )
        login_btn.pack(fill="x", padx=20, pady=20)
        
        # 测试用户按钮
        test_users_frame = ctk.CTkFrame(self.dialog)
        test_users_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(test_users_frame, text="测试用户:", font=("Arial", 12)).pack(pady=5)
        
        test_users = ["user001", "user002", "user003"]
        for user_id in test_users:
            btn = ctk.CTkButton(
                test_users_frame,
                text=f"👤 {user_id}",
                font=("Arial", 12),
                height=30,
                command=lambda u=user_id: self._quick_login(u)
            )
            btn.pack(fill="x", pady=2)
    
    def _login(self):
        """登录"""
        user_id = self.user_id_entry.get().strip()
        name = self.name_entry.get().strip()
        
        if not user_id or not name:
            messagebox.showwarning("警告", "请填写完整信息")
            return
        
        try:
            # 获取或创建用户数据
            user_data = self.main_window.app_core.get_user_data(user_id)
            if not user_data:
                # 创建新用户
                from core.base import UserData
                user_data = UserData(
                    user_id=user_id,
                    profile={'name': name, 'age': 25, 'gender': '女', 'height': 165, 'weight': 55, 'activity_level': 'moderate'},
                    meals=[],
                    feedback=[],
                    preferences={}
                )
                self.main_window.app_core.data_manager.save_user_data(user_data)
            
            # 设置当前用户
            self.main_window.set_current_user(user_id, user_data)
            
            # 关闭对话框
            self.dialog.destroy()
            
            messagebox.showinfo("成功", f"欢迎，{name}！")
            
        except Exception as e:
            messagebox.showerror("错误", f"登录失败: {str(e)}")
    
    def _quick_login(self, user_id: str):
        """快速登录测试用户"""
        self.user_id_entry.delete(0, "end")
        self.user_id_entry.insert(0, user_id)
        
        # 设置默认姓名
        names = {"user001": "张三", "user002": "李四", "user003": "王五"}
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, names.get(user_id, "测试用户"))
    
    def show(self):
        """显示对话框"""
        self.dialog.wait_window()


def main():
    """主函数"""
    app = MobileMainWindow()
    app.run()


if __name__ == "__main__":
    main()
