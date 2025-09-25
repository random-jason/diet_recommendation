"""
主GUI界面 - 基于CustomTkinter的现代化界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import customtkinter as ctk
from typing import Optional, Dict, Any, List
from datetime import datetime, date
import json
import threading
from core.base import AppCore, UserData, ModuleType
# 移除直接导入，改为通过应用核心调用
# from modules.data_collection import collect_questionnaire_data, record_meal, record_feedback
# from modules.ai_analysis import analyze_user_intent, analyze_nutrition, analyze_physiological_state
# from modules.recommendation_engine import generate_meal_recommendations, find_similar_foods

# 设置CustomTkinter主题
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MainWindow:
    """主窗口类"""
    
    def __init__(self, root: tk.Tk, app_core: AppCore):
        self.root = root
        self.app_core = app_core
        self.current_user_id: Optional[str] = None
        self.current_user_data: Optional[UserData] = None
        
        # 设置窗口属性
        self._setup_window()
        
        # 创建界面
        self._create_widgets()
        
        # 绑定事件
        self._bind_events()
        
        # 初始化界面状态
        self._initialize_ui_state()
    
    def _setup_window(self):
        """设置窗口属性"""
        self.root.title("个性化饮食推荐助手")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # 设置窗口图标（如果有的话）
        try:
            # self.root.iconbitmap("assets/icon.ico")
            pass
        except:
            pass
    
    def _create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建顶部导航栏
        self._create_navigation_bar()
        
        # 创建主内容区域
        self._create_main_content()
        
        # 创建状态栏
        self._create_status_bar()
    
    def _create_navigation_bar(self):
        """创建导航栏"""
        nav_frame = ctk.CTkFrame(self.main_frame)
        nav_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # 应用标题
        title_label = ctk.CTkLabel(
            nav_frame, 
            text="🍎 个性化饮食推荐助手", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=10)
        
        # 用户信息区域
        self.user_info_frame = ctk.CTkFrame(nav_frame)
        self.user_info_frame.pack(side="right", padx=20, pady=10)
        
        self.user_label = ctk.CTkLabel(
            self.user_info_frame, 
            text="未登录", 
            font=ctk.CTkFont(size=14)
        )
        self.user_label.pack(padx=10, pady=5)
        
        # 登录/注册按钮
        self.login_button = ctk.CTkButton(
            self.user_info_frame,
            text="登录/注册",
            command=self._show_login_dialog,
            width=100
        )
        self.login_button.pack(padx=10, pady=5)
    
    def _create_main_content(self):
        """创建主内容区域"""
        # 创建选项卡
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 添加选项卡
        self.tabview.add("数据采集")
        self.tabview.add("AI分析")
        self.tabview.add("推荐系统")
        self.tabview.add("历史推荐")
        self.tabview.add("个人中心")
        
        # 设置选项卡名称
        self.tabview.set("数据采集")
        
        # 创建各个选项卡的内容
        self._create_data_collection_tab()
        self._create_ai_analysis_tab()
        self._create_recommendation_tab()
        self._create_history_recommend_tab()
        self._create_profile_tab()
    
    def _create_data_collection_tab(self):
        """创建数据采集选项卡"""
        tab = self.tabview.tab("数据采集")
        
        # 创建滚动框架
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 问卷部分
        questionnaire_frame = ctk.CTkFrame(scroll_frame)
        questionnaire_frame.pack(fill="x", padx=10, pady=10)
        
        questionnaire_title = ctk.CTkLabel(
            questionnaire_frame, 
            text="📋 用户问卷", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        questionnaire_title.pack(pady=10)
        
        # 问卷类型选择
        self.questionnaire_type_var = tk.StringVar(value="basic")
        questionnaire_type_label = ctk.CTkLabel(questionnaire_frame, text="问卷类型:")
        questionnaire_type_label.pack(anchor="w", padx=20, pady=5)
        
        questionnaire_type_menu = ctk.CTkOptionMenu(
            questionnaire_frame,
            variable=self.questionnaire_type_var,
            values=["basic", "taste", "physiological"],
            command=self._on_questionnaire_type_changed
        )
        questionnaire_type_menu.pack(anchor="w", padx=20, pady=5)
        
        # 问卷内容区域
        self.questionnaire_content_frame = ctk.CTkFrame(questionnaire_frame)
        self.questionnaire_content_frame.pack(fill="x", padx=20, pady=10)
        
        # 餐食记录部分
        meal_frame = ctk.CTkFrame(scroll_frame)
        meal_frame.pack(fill="x", padx=10, pady=10)
        
        meal_title = ctk.CTkLabel(
            meal_frame, 
            text="🍽️ 餐食记录", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        meal_title.pack(pady=10)
        
        # 餐食记录表单
        self._create_meal_record_form(meal_frame)
        
        # 反馈记录部分
        feedback_frame = ctk.CTkFrame(scroll_frame)
        feedback_frame.pack(fill="x", padx=10, pady=10)
        
        feedback_title = ctk.CTkLabel(
            feedback_frame, 
            text="💬 用户反馈", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        feedback_title.pack(pady=10)
        
        # 反馈记录表单
        self._create_feedback_form(feedback_frame)
    
    def _create_meal_record_form(self, parent):
        """创建餐食记录表单"""
        form_frame = ctk.CTkFrame(parent)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # 日期选择
        date_label = ctk.CTkLabel(form_frame, text="日期:")
        date_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.meal_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        date_entry = ctk.CTkEntry(form_frame, textvariable=self.meal_date_var, width=150)
        date_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # 餐次选择
        meal_type_label = ctk.CTkLabel(form_frame, text="餐次:")
        meal_type_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.meal_type_var = tk.StringVar(value="breakfast")
        meal_type_menu = ctk.CTkOptionMenu(
            form_frame,
            variable=self.meal_type_var,
            values=["breakfast", "lunch", "dinner"]
        )
        meal_type_menu.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # 食物输入
        foods_label = ctk.CTkLabel(form_frame, text="食物:")
        foods_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        self.foods_text = ctk.CTkTextbox(form_frame, height=60, width=300)
        self.foods_text.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        self.foods_text.insert("1.0", "请输入食物名称，每行一个")
        self.foods_text.bind("<KeyRelease>", self._on_foods_changed)
        
        # 分量输入
        quantities_label = ctk.CTkLabel(form_frame, text="分量:")
        quantities_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        
        self.quantities_text = ctk.CTkTextbox(form_frame, height=60, width=300)
        self.quantities_text.grid(row=3, column=1, sticky="w", padx=10, pady=5)
        self.quantities_text.insert("1.0", "请输入对应分量，每行一个")
        self.quantities_text.bind("<KeyRelease>", self._on_quantities_changed)
        
        # 热量显示（自动估算）
        calories_label = ctk.CTkLabel(form_frame, text="预估热量:")
        calories_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        
        self.calories_display = ctk.CTkLabel(form_frame, text="系统将自动估算", width=150, anchor="w")
        self.calories_display.grid(row=4, column=1, sticky="w", padx=10, pady=5)
        
        # 满意度评分
        satisfaction_label = ctk.CTkLabel(form_frame, text="满意度:")
        satisfaction_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)
        
        self.satisfaction_var = tk.IntVar(value=3)
        satisfaction_slider = ctk.CTkSlider(
            form_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            variable=self.satisfaction_var
        )
        satisfaction_slider.grid(row=5, column=1, sticky="w", padx=10, pady=5)
        
        # 快速录入按钮
        quick_input_button = ctk.CTkButton(
            form_frame,
            text="🚀 快速录入",
            command=self._show_quick_input_dialog,
            width=150,
            fg_color="purple"
        )
        quick_input_button.grid(row=6, column=0, sticky="w", padx=10, pady=10)
        
        # 智能记录按钮
        smart_record_button = ctk.CTkButton(
            form_frame,
            text="智能记录餐食",
            command=self._show_smart_meal_record,
            width=150,
            fg_color="green"
        )
        smart_record_button.grid(row=6, column=1, sticky="w", padx=10, pady=10)
        
        # 传统记录按钮
        save_meal_button = ctk.CTkButton(
            form_frame,
            text="手动记录餐食",
            command=self._save_meal_record,
            width=150
        )
        save_meal_button.grid(row=6, column=1, sticky="w", padx=10, pady=10)
    
    def _create_feedback_form(self, parent):
        """创建反馈表单"""
        form_frame = ctk.CTkFrame(parent)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # 推荐食物
        recommended_label = ctk.CTkLabel(form_frame, text="推荐食物:")
        recommended_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.recommended_foods_text = ctk.CTkTextbox(form_frame, height=60, width=300)
        self.recommended_foods_text.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # 用户选择
        user_choice_label = ctk.CTkLabel(form_frame, text="用户选择:")
        user_choice_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.user_choice_var = tk.StringVar()
        user_choice_entry = ctk.CTkEntry(form_frame, textvariable=self.user_choice_var, width=300)
        user_choice_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # 反馈类型
        feedback_type_label = ctk.CTkLabel(form_frame, text="反馈类型:")
        feedback_type_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        self.feedback_type_var = tk.StringVar(value="like")
        feedback_type_menu = ctk.CTkOptionMenu(
            form_frame,
            variable=self.feedback_type_var,
            values=["like", "dislike", "ate"]
        )
        feedback_type_menu.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # 保存按钮
        save_feedback_button = ctk.CTkButton(
            form_frame,
            text="保存反馈",
            command=self._save_feedback,
            width=150
        )
        save_feedback_button.grid(row=3, column=1, sticky="w", padx=10, pady=10)
    
    def _create_ai_analysis_tab(self):
        """创建AI分析选项卡"""
        tab = self.tabview.tab("AI分析")
        
        # 创建滚动框架
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 用户意图分析
        intent_frame = ctk.CTkFrame(scroll_frame)
        intent_frame.pack(fill="x", padx=10, pady=10)
        
        intent_title = ctk.CTkLabel(
            intent_frame, 
            text="🧠 用户意图分析", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        intent_title.pack(pady=10)
        
        # 用户输入
        input_label = ctk.CTkLabel(intent_frame, text="用户输入:")
        input_label.pack(anchor="w", padx=20, pady=5)
        
        self.user_input_text = ctk.CTkTextbox(intent_frame, height=80, width=600)
        self.user_input_text.pack(fill="x", padx=20, pady=5)
        self.user_input_text.insert("1.0", "请输入用户的饮食需求或问题...")
        
        # 分析按钮
        analyze_button = ctk.CTkButton(
            intent_frame,
            text="分析用户意图",
            command=self._analyze_user_intent,
            width=150
        )
        analyze_button.pack(padx=20, pady=10)
        
        # 分析结果显示
        self.intent_result_text = ctk.CTkTextbox(intent_frame, height=200, width=600)
        self.intent_result_text.pack(fill="x", padx=20, pady=10)
        
        # 营养分析
        nutrition_frame = ctk.CTkFrame(scroll_frame)
        nutrition_frame.pack(fill="x", padx=10, pady=10)
        
        nutrition_title = ctk.CTkLabel(
            nutrition_frame, 
            text="🥗 营养分析", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        nutrition_title.pack(pady=10)
        
        # 营养分析按钮
        nutrition_button = ctk.CTkButton(
            nutrition_frame,
            text="分析最近餐食营养",
            command=self._analyze_nutrition,
            width=150
        )
        nutrition_button.pack(padx=20, pady=10)
        
        # 营养分析结果显示
        self.nutrition_result_text = ctk.CTkTextbox(nutrition_frame, height=200, width=600)
        self.nutrition_result_text.pack(fill="x", padx=20, pady=10)
    
    def _create_recommendation_tab(self):
        """创建推荐系统选项卡"""
        tab = self.tabview.tab("推荐系统")
        
        # 创建滚动框架
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 餐食推荐
        recommendation_frame = ctk.CTkFrame(scroll_frame)
        recommendation_frame.pack(fill="x", padx=10, pady=10)
        
        recommendation_title = ctk.CTkLabel(
            recommendation_frame, 
            text="🎯 个性化推荐", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        recommendation_title.pack(pady=10)
        
        # 推荐参数
        params_frame = ctk.CTkFrame(recommendation_frame)
        params_frame.pack(fill="x", padx=20, pady=10)
        
        # 餐次选择
        meal_type_label = ctk.CTkLabel(params_frame, text="餐次:")
        meal_type_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.recommendation_meal_type_var = tk.StringVar(value="lunch")
        meal_type_menu = ctk.CTkOptionMenu(
            params_frame,
            variable=self.recommendation_meal_type_var,
            values=["breakfast", "lunch", "dinner"]
        )
        meal_type_menu.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # 口味偏好
        taste_label = ctk.CTkLabel(params_frame, text="口味偏好:")
        taste_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.taste_preference_var = tk.StringVar(value="balanced")
        taste_menu = ctk.CTkOptionMenu(
            params_frame,
            variable=self.taste_preference_var,
            values=["balanced", "sweet", "salty", "spicy", "sour"]
        )
        taste_menu.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # 推荐按钮
        recommend_button = ctk.CTkButton(
            params_frame,
            text="生成推荐",
            command=self._generate_recommendations,
            width=150
        )
        recommend_button.grid(row=2, column=1, sticky="w", padx=10, pady=10)
        
        # 推荐结果显示
        self.recommendation_result_text = ctk.CTkTextbox(recommendation_frame, height=300, width=600)
        self.recommendation_result_text.pack(fill="x", padx=20, pady=10)
    
    def _create_history_recommend_tab(self):
        """创建历史数据驱动的推荐页签（前端仅展示推荐列表，训练在后台）"""
        tab = self.tabview.tab("历史推荐")
        
        # 创建滚动框架
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 标题
        title = ctk.CTkLabel(
            scroll_frame,
            text="📊 基于历史数据的个性化推荐",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(anchor="w", padx=10, pady=10)
        
        # 说明
        info = ctk.CTkLabel(
            scroll_frame,
            text="训练在后台自动进行，页面展示最新推荐结果。",
            font=ctk.CTkFont(size=12)
        )
        info.pack(anchor="w", padx=10, pady=5)
        
        # 控制区域
        control_frame = ctk.CTkFrame(scroll_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # 餐次选择
        meal_type_label = ctk.CTkLabel(control_frame, text="餐次:")
        meal_type_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.hist_meal_type_var = tk.StringVar(value="lunch")
        meal_menu = ctk.CTkOptionMenu(
            control_frame,
            variable=self.hist_meal_type_var,
            values=["breakfast", "lunch", "dinner", "snack"]
        )
        meal_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # 刷新按钮
        refresh_btn = ctk.CTkButton(
            control_frame,
            text="🔄 刷新推荐",
            command=self._refresh_history_recommendations
        )
        refresh_btn.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        # 结果显示区域
        self.history_rec_text = ctk.CTkTextbox(scroll_frame, height=420)
        self.history_rec_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 页面打开时自动触发一次刷新
        self.root.after(300, self._refresh_history_recommendations)
    
    def _refresh_history_recommendations(self):
        """刷新历史推荐"""
        if not self.current_user_id:
            self._update_status("请先登录")
            return
        
        meal_type = self.hist_meal_type_var.get()
        
        def work():
            try:
                # 启动后台训练（幂等）
                from modules.efficient_data_processing import training_pipeline
                training_pipeline.start_background_training()
                
                # 立即进行一次快速训练+推荐（内部做了缓存）
                recs = training_pipeline.predict_recommendations(self.current_user_id, meal_type)
                self.root.after(0, lambda: self._render_history_recs(recs))
            except Exception as e:
                self.root.after(0, lambda: self._update_status(f"历史推荐失败: {e}"))
        
        threading.Thread(target=work, daemon=True).start()
    
    def _render_history_recs(self, recs: List[Dict[str, Any]]):
        """渲染历史推荐结果"""
        self.history_rec_text.delete("1.0", "end")
        
        if not recs:
            self.history_rec_text.insert("1.0", "暂无推荐，请先记录一些餐食或稍后再试。")
            return
        
        lines = []
        for i, r in enumerate(recs, 1):
            food = r.get('food', '推荐项')
            confidence = r.get('confidence', 0)
            reason = r.get('reason', '-')
            lines.append(f"{i}. {food}  可信度: {confidence:.2f}  原因: {reason}")
        
        self.history_rec_text.insert("1.0", "\n".join(lines))
    
    def _create_profile_tab(self):
        """创建个人中心选项卡"""
        tab = self.tabview.tab("个人中心")
        
        # 创建滚动框架
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 用户信息
        profile_frame = ctk.CTkFrame(scroll_frame)
        profile_frame.pack(fill="x", padx=10, pady=10)
        
        profile_title = ctk.CTkLabel(
            profile_frame, 
            text="👤 个人信息", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        profile_title.pack(pady=10)
        
        # 用户信息显示
        self.profile_info_text = ctk.CTkTextbox(profile_frame, height=200, width=600)
        self.profile_info_text.pack(fill="x", padx=20, pady=10)
        
        # 刷新按钮
        refresh_button = ctk.CTkButton(
            profile_frame,
            text="刷新信息",
            command=self._refresh_profile_info,
            width=150
        )
        refresh_button.pack(padx=20, pady=10)
        
        # 数据统计
        stats_frame = ctk.CTkFrame(scroll_frame)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        stats_title = ctk.CTkLabel(
            stats_frame, 
            text="📊 数据统计", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        stats_title.pack(pady=10)
        
        # 统计数据
        self.stats_text = ctk.CTkTextbox(stats_frame, height=200, width=600)
        self.stats_text.pack(fill="x", padx=20, pady=10)
    
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="就绪", 
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # 模块状态
        self.module_status_label = ctk.CTkLabel(
            self.status_frame, 
            text="模块状态: 正常", 
            font=ctk.CTkFont(size=12)
        )
        self.module_status_label.pack(side="right", padx=10, pady=5)
    
    def _bind_events(self):
        """绑定事件"""
        pass
    
    def _initialize_ui_state(self):
        """初始化界面状态"""
        self._update_status("就绪")
        self._load_questionnaire_content("basic")
    
    def _update_status(self, message: str):
        """更新状态栏"""
        self.status_label.configure(text=message)
        self.root.update_idletasks()
    
    def _show_login_dialog(self):
        """显示登录对话框"""
        dialog = LoginDialog(self.root, self)
        self.root.wait_window(dialog.dialog)
    
    def _on_questionnaire_type_changed(self, value):
        """问卷类型改变事件"""
        self._load_questionnaire_content(value)
    
    def _load_questionnaire_content(self, questionnaire_type: str):
        """加载问卷内容"""
        # 清空现有内容
        for widget in self.questionnaire_content_frame.winfo_children():
            widget.destroy()
        
        # 根据问卷类型创建内容
        if questionnaire_type == "basic":
            self._create_basic_questionnaire()
        elif questionnaire_type == "taste":
            self._create_taste_questionnaire()
        elif questionnaire_type == "physiological":
            self._create_physiological_questionnaire()
    
    def _create_basic_questionnaire(self):
        """创建基础问卷"""
        # 姓名
        name_label = ctk.CTkLabel(self.questionnaire_content_frame, text="姓名:")
        name_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.name_var = tk.StringVar()
        name_entry = ctk.CTkEntry(self.questionnaire_content_frame, textvariable=self.name_var, width=200)
        name_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # 年龄范围选择
        age_label = ctk.CTkLabel(self.questionnaire_content_frame, text="年龄范围:")
        age_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.age_range_var = tk.StringVar(value="25-30岁")
        age_menu = ctk.CTkOptionMenu(
            self.questionnaire_content_frame,
            variable=self.age_range_var,
            values=["18-24岁", "25-30岁", "31-35岁", "36-40岁", "41-45岁", "46-50岁", "51-55岁", "56-60岁", "60岁以上"]
        )
        age_menu.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # 性别
        gender_label = ctk.CTkLabel(self.questionnaire_content_frame, text="性别:")
        gender_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        self.gender_var = tk.StringVar(value="女")
        gender_menu = ctk.CTkOptionMenu(
            self.questionnaire_content_frame,
            variable=self.gender_var,
            values=["男", "女"]
        )
        gender_menu.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # 身高范围
        height_label = ctk.CTkLabel(self.questionnaire_content_frame, text="身高范围:")
        height_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        
        self.height_range_var = tk.StringVar(value="160-165cm")
        height_menu = ctk.CTkOptionMenu(
            self.questionnaire_content_frame,
            variable=self.height_range_var,
            values=["150cm以下", "150-155cm", "155-160cm", "160-165cm", "165-170cm", "170-175cm", "175-180cm", "180cm以上"]
        )
        height_menu.grid(row=3, column=1, sticky="w", padx=10, pady=5)
        
        # 体重范围
        weight_label = ctk.CTkLabel(self.questionnaire_content_frame, text="体重范围:")
        weight_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        
        self.weight_range_var = tk.StringVar(value="50-55kg")
        weight_menu = ctk.CTkOptionMenu(
            self.questionnaire_content_frame,
            variable=self.weight_range_var,
            values=["40kg以下", "40-45kg", "45-50kg", "50-55kg", "55-60kg", "60-65kg", "65-70kg", "70-75kg", "75-80kg", "80kg以上"]
        )
        weight_menu.grid(row=4, column=1, sticky="w", padx=10, pady=5)
        
        # 活动水平
        activity_label = ctk.CTkLabel(self.questionnaire_content_frame, text="活动水平:")
        activity_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)
        
        self.activity_var = tk.StringVar(value="中等")
        activity_menu = ctk.CTkOptionMenu(
            self.questionnaire_content_frame,
            variable=self.activity_var,
            values=["久坐", "轻度活动", "中等", "高度活动", "极度活动"]
        )
        activity_menu.grid(row=5, column=1, sticky="w", padx=10, pady=5)
        
        # 保存按钮
        save_button = ctk.CTkButton(
            self.questionnaire_content_frame,
            text="保存基础信息",
            command=self._save_basic_questionnaire,
            width=150
        )
        save_button.grid(row=6, column=1, sticky="w", padx=10, pady=10)
    
    def _create_taste_questionnaire(self):
        """创建口味问卷"""
        # 甜味偏好
        sweet_label = ctk.CTkLabel(self.questionnaire_content_frame, text="甜味偏好:")
        sweet_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.sweet_var = tk.IntVar(value=3)
        sweet_slider = ctk.CTkSlider(
            self.questionnaire_content_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            variable=self.sweet_var
        )
        sweet_slider.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # 咸味偏好
        salty_label = ctk.CTkLabel(self.questionnaire_content_frame, text="咸味偏好:")
        salty_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.salty_var = tk.IntVar(value=3)
        salty_slider = ctk.CTkSlider(
            self.questionnaire_content_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            variable=self.salty_var
        )
        salty_slider.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # 辣味偏好
        spicy_label = ctk.CTkLabel(self.questionnaire_content_frame, text="辣味偏好:")
        spicy_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        self.spicy_var = tk.IntVar(value=3)
        spicy_slider = ctk.CTkSlider(
            self.questionnaire_content_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            variable=self.spicy_var
        )
        spicy_slider.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # 酸味偏好
        sour_label = ctk.CTkLabel(self.questionnaire_content_frame, text="酸味偏好:")
        sour_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        
        self.sour_var = tk.IntVar(value=3)
        sour_slider = ctk.CTkSlider(
            self.questionnaire_content_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            variable=self.sour_var
        )
        sour_slider.grid(row=3, column=1, sticky="w", padx=10, pady=5)
        
        # 苦味偏好
        bitter_label = ctk.CTkLabel(self.questionnaire_content_frame, text="苦味偏好:")
        bitter_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        
        self.bitter_var = tk.IntVar(value=3)
        bitter_slider = ctk.CTkSlider(
            self.questionnaire_content_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            variable=self.bitter_var
        )
        bitter_slider.grid(row=4, column=1, sticky="w", padx=10, pady=5)
        
        # 保存按钮
        save_button = ctk.CTkButton(
            self.questionnaire_content_frame,
            text="保存口味偏好",
            command=self._save_taste_questionnaire,
            width=150
        )
        save_button.grid(row=5, column=1, sticky="w", padx=10, pady=10)
    
    def _create_physiological_questionnaire(self):
        """创建生理问卷"""
        # 月经周期长度
        cycle_label = ctk.CTkLabel(self.questionnaire_content_frame, text="月经周期长度:")
        cycle_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.cycle_length_var = tk.StringVar(value="28")
        cycle_entry = ctk.CTkEntry(self.questionnaire_content_frame, textvariable=self.cycle_length_var, width=200)
        cycle_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # 保存按钮
        save_button = ctk.CTkButton(
            self.questionnaire_content_frame,
            text="保存生理信息",
            command=self._save_physiological_questionnaire,
            width=150
        )
        save_button.grid(row=1, column=1, sticky="w", padx=10, pady=10)
    
    def _save_basic_questionnaire(self):
        """保存基础问卷"""
        if not self.current_user_id:
            messagebox.showwarning("警告", "请先登录")
            return
        
        # 将范围转换为具体数值
        age_range = self.age_range_var.get()
        height_range = self.height_range_var.get()
        weight_range = self.weight_range_var.get()
        
        # 年龄范围转换
        age_mapping = {
            "18-24岁": 21, "25-30岁": 27, "31-35岁": 33, "36-40岁": 38,
            "41-45岁": 43, "46-50岁": 48, "51-55岁": 53, "56-60岁": 58, "60岁以上": 65
        }
        
        # 身高范围转换
        height_mapping = {
            "150cm以下": 150, "150-155cm": 152, "155-160cm": 157, "160-165cm": 162,
            "165-170cm": 167, "170-175cm": 172, "175-180cm": 177, "180cm以上": 180
        }
        
        # 体重范围转换
        weight_mapping = {
            "40kg以下": 40, "40-45kg": 42, "45-50kg": 47, "50-55kg": 52,
            "55-60kg": 57, "60-65kg": 62, "65-70kg": 67, "70-75kg": 72,
            "75-80kg": 77, "80kg以上": 80
        }
        
        # 活动水平转换
        activity_mapping = {
            "久坐": "sedentary", "轻度活动": "light", "中等": "moderate",
            "高度活动": "high", "极度活动": "very_high"
        }
        
        answers = {
            'name': self.name_var.get(),
            'age': age_mapping.get(age_range, 25),
            'gender': self.gender_var.get(),
            'height': height_mapping.get(height_range, 165),
            'weight': weight_mapping.get(weight_range, 55),
            'activity_level': activity_mapping.get(self.activity_var.get(), 'moderate')
        }
        
        try:
            # 通过应用核心调用数据收集模块
            if self.app_core and self.app_core.module_manager:
                result = self.app_core.process_user_request(
                    ModuleType.DATA_COLLECTION, 
                    {'type': 'questionnaire', 'questionnaire_type': 'basic', 'answers': answers},
                    self.current_user_id
                )
                
                if result and result.result.get('success'):
                    messagebox.showinfo("成功", "基础信息保存成功")
                else:
                    messagebox.showerror("错误", "基础信息保存失败")
            else:
                messagebox.showerror("错误", "应用核心未初始化")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def _save_taste_questionnaire(self):
        """保存口味问卷"""
        if not self.current_user_id:
            messagebox.showwarning("警告", "请先登录")
            return
        
        answers = {
            'sweet': self.sweet_var.get()
        }
        
        try:
            # 通过应用核心调用数据收集模块
            if self.app_core and self.app_core.module_manager:
                result = self.app_core.process_user_request(
                    ModuleType.DATA_COLLECTION,
                    {'type': 'questionnaire', 'questionnaire_type': 'taste', 'answers': answers},
                    self.current_user_id
                )
                
                if result and result.result.get('success'):
                    messagebox.showinfo("成功", "口味偏好保存成功")
                else:
                    messagebox.showerror("错误", "口味偏好保存失败")
            else:
                messagebox.showerror("错误", "应用核心未初始化")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def _save_physiological_questionnaire(self):
        """保存生理问卷"""
        if not self.current_user_id:
            messagebox.showwarning("警告", "请先登录")
            return
        
        answers = {
            'menstrual_cycle_length': int(self.cycle_length_var.get()) if self.cycle_length_var.get().isdigit() else 28
        }
        
        try:
            # 通过应用核心调用数据收集模块
            if self.app_core and self.app_core.module_manager:
                result = self.app_core.process_user_request(
                    ModuleType.DATA_COLLECTION,
                    {'type': 'questionnaire', 'questionnaire_type': 'physiological', 'answers': answers},
                    self.current_user_id
                )
                
                if result and result.result.get('success'):
                    messagebox.showinfo("成功", "生理信息保存成功")
                else:
                    messagebox.showerror("错误", "生理信息保存失败")
            else:
                messagebox.showerror("错误", "应用核心未初始化")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def _on_foods_changed(self, event=None):
        """食物输入改变事件"""
        self._update_calories_estimate()
    
    def _on_quantities_changed(self, event=None):
        """分量输入改变事件"""
        self._update_calories_estimate()
    
    def _update_calories_estimate(self):
        """更新热量估算"""
        try:
            foods_text = self.foods_text.get("1.0", "end-1c")
            quantities_text = self.quantities_text.get("1.0", "end-1c")
            
            foods = [food.strip() for food in foods_text.split('\n') if food.strip()]
            quantities = [qty.strip() for qty in quantities_text.split('\n') if qty.strip()]
            
            if not foods or not quantities or len(foods) != len(quantities):
                self.calories_display.configure(text="系统将自动估算")
                return
            
            # 估算热量
            from smart_food.smart_database import estimate_calories
            total_calories = 0
            
            for food, quantity in zip(foods, quantities):
                calories = estimate_calories(food, quantity)
                total_calories += calories
            
            self.calories_display.configure(text=f"约 {total_calories} 卡路里")
            
        except Exception:
            self.calories_display.configure(text="系统将自动估算")
    
    def _save_meal_record(self):
        """保存餐食记录"""
        if not self.current_user_id:
            messagebox.showwarning("警告", "请先登录")
            return
        
        foods_text = self.foods_text.get("1.0", "end-1c")
        quantities_text = self.quantities_text.get("1.0", "end-1c")
        
        foods = [food.strip() for food in foods_text.split('\n') if food.strip()]
        quantities = [qty.strip() for qty in quantities_text.split('\n') if qty.strip()]
        
        if not foods:
            messagebox.showwarning("警告", "请输入食物")
            return
        
        if len(foods) != len(quantities):
            messagebox.showwarning("警告", "食物和分量数量不匹配")
            return
        
        # 自动估算热量
        try:
            from smart_food.smart_database import estimate_calories
            total_calories = 0
            food_items = []
            
            for food, quantity in zip(foods, quantities):
                calories = estimate_calories(food, quantity)
                total_calories += calories
                food_items.append({
                    "name": food,
                    "portion": quantity,
                    "calories": calories
                })
            
            # 更新热量显示
            self.calories_display.configure(text=f"约 {total_calories} 卡路里")
            
        except Exception as e:
            messagebox.showwarning("警告", f"热量估算失败: {str(e)}")
            total_calories = None
            food_items = [{"name": food, "portion": qty} for food, qty in zip(foods, quantities)]
        
        meal_data = {
            'date': self.meal_date_var.get(),
            'meal_type': self.meal_type_var.get(),
            'foods': foods,
            'quantities': quantities,
            'calories': total_calories,
            'satisfaction_score': self.satisfaction_var.get(),
            'food_items': food_items
        }
        
        try:
            # 通过应用核心调用数据收集模块
            if self.app_core and self.app_core.module_manager:
                result = self.app_core.process_user_request(
                    ModuleType.DATA_COLLECTION,
                    {'type': 'meal_record', 'meal_data': meal_data},
                    self.current_user_id
                )
                
                if result and result.result.get('success'):
                    messagebox.showinfo("成功", "餐食记录保存成功")
                    # 清空表单
                    self.foods_text.delete("1.0", "end")
                    self.quantities_text.delete("1.0", "end")
                    self.calories_display.configure(text="系统将自动估算")
                else:
                    messagebox.showerror("错误", "餐食记录保存失败")
            else:
                messagebox.showerror("错误", "应用核心未初始化")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def _save_feedback(self):
        """保存反馈"""
        if not self.current_user_id:
            messagebox.showwarning("警告", "请先登录")
            return
        
        recommended_text = self.recommended_foods_text.get("1.0", "end-1c")
        recommended_foods = [food.strip() for food in recommended_text.split('\n') if food.strip()]
        
        feedback_data = {
            'recommended_foods': recommended_foods,
            'user_choice': self.user_choice_var.get(),
            'feedback_type': self.feedback_type_var.get()
        }
        
        try:
            # 通过应用核心调用数据收集模块
            if self.app_core and self.app_core.module_manager:
                result = self.app_core.process_user_request(
                    ModuleType.DATA_COLLECTION,
                    {'type': 'feedback', 'feedback_data': feedback_data},
                    self.current_user_id
                )
                
                if result and result.result.get('success'):
                    messagebox.showinfo("成功", "反馈保存成功")
                else:
                    messagebox.showerror("错误", "反馈保存失败")
            else:
                messagebox.showerror("错误", "应用核心未初始化")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def _analyze_user_intent(self):
        """分析用户意图"""
        if not self.current_user_id:
            messagebox.showwarning("警告", "请先登录")
            return
        
        user_input = self.user_input_text.get("1.0", "end-1c").strip()
        if not user_input:
            messagebox.showwarning("警告", "请输入用户输入内容")
            return
        
        self._update_status("正在分析用户意图...")
        
        def analyze_thread():
            try:
                # 直接使用千问API
                from llm_integration.qwen_client import analyze_user_intent_with_qwen
                
                # 获取用户数据
                user_data = self.app_core.get_user_data(self.current_user_id)
                if not user_data:
                    self.root.after(0, lambda: self._update_status("用户数据不存在"))
                    return
                
                # 构建用户上下文
                user_context = {
                    'name': user_data.profile.get('name', '未知'),
                    'age': user_data.profile.get('age', '未知'),
                    'gender': user_data.profile.get('gender', '未知'),
                    'height': user_data.profile.get('height', '未知'),
                    'weight': user_data.profile.get('weight', '未知'),
                    'activity_level': user_data.profile.get('activity_level', '未知'),
                    'taste_preferences': user_data.profile.get('taste_preferences', {}),
                    'allergies': user_data.profile.get('allergies', []),
                    'dislikes': user_data.profile.get('dislikes', []),
                    'dietary_preferences': user_data.profile.get('dietary_preferences', []),
                    'recent_meals': user_data.meals[-3:] if user_data.meals else [],
                    'feedback_history': user_data.feedback[-5:] if user_data.feedback else []
                }
                
                result = analyze_user_intent_with_qwen(user_input, user_context)
                if result:
                    self.root.after(0, lambda: self._display_intent_result(result))
                else:
                    self.root.after(0, lambda: self._update_status("分析失败"))
            except Exception as e:
                self.root.after(0, lambda: self._update_status(f"分析错误: {str(e)}"))
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def _display_intent_result(self, result: Dict):
        """显示意图分析结果"""
        self.intent_result_text.delete("1.0", "end")
        
        if result.get('success'):
            content = f"""
用户意图: {result.get('user_intent', '未知')}
情绪状态: {result.get('emotional_state', '未知')}
营养需求: {', '.join(result.get('nutritional_needs', []))}
推荐食物: {', '.join(result.get('recommended_foods', []))}
推荐理由: {result.get('reasoning', '无')}
置信度: {result.get('confidence', 0):.2f}
"""
        else:
            content = f"分析失败: {result.get('error', '未知错误')}"
        
        self.intent_result_text.insert("1.0", content)
        self._update_status("用户意图分析完成")
    
    def _analyze_nutrition(self):
        """分析营养"""
        if not self.current_user_id:
            messagebox.showwarning("警告", "请先登录")
            return
        
        # 获取最近的餐食数据
        user_data = self.app_core.get_user_data(self.current_user_id)
        if not user_data or not user_data.meals:
            messagebox.showwarning("警告", "没有餐食记录")
            return
        
        latest_meal = user_data.meals[-1]
        
        self._update_status("正在分析营养...")
        
        def analyze_thread():
            try:
                # 直接使用千问API
                from llm_integration.qwen_client import analyze_nutrition_with_qwen
                
                # 获取用户数据
                user_data = self.app_core.get_user_data(self.current_user_id)
                if not user_data:
                    self.root.after(0, lambda: self._update_status("用户数据不存在"))
                    return
                
                # 构建用户上下文
                user_context = {
                    'age': user_data.profile.get('age', '未知'),
                    'gender': user_data.profile.get('gender', '未知'),
                    'height': user_data.profile.get('height', '未知'),
                    'weight': user_data.profile.get('weight', '未知'),
                    'activity_level': user_data.profile.get('activity_level', '未知'),
                    'health_goals': user_data.profile.get('health_goals', [])
                }
                
                result = analyze_nutrition_with_qwen(latest_meal, user_context)
                if result:
                    self.root.after(0, lambda: self._display_nutrition_result(result))
                else:
                    self.root.after(0, lambda: self._update_status("营养分析失败"))
            except Exception as e:
                self.root.after(0, lambda: self._update_status(f"营养分析错误: {str(e)}"))
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def _display_nutrition_result(self, result: Dict):
        """显示营养分析结果"""
        self.nutrition_result_text.delete("1.0", "end")
        
        if result.get('success'):
            content = f"""
营养均衡性: {result.get('nutrition_balance', '未知')}
热量评估: {result.get('calorie_assessment', '未知')}
缺少营养素: {', '.join(result.get('missing_nutrients', []))}
改进建议: {', '.join(result.get('improvements', []))}
个性化建议: {', '.join(result.get('recommendations', []))}
置信度: {result.get('confidence', 0):.2f}
"""
        else:
            content = f"分析失败: {result.get('error', '未知错误')}"
        
        self.nutrition_result_text.insert("1.0", content)
        self._update_status("营养分析完成")
    
    def _generate_recommendations(self):
        """生成推荐"""
        if not self.current_user_id:
            messagebox.showwarning("警告", "请先登录")
            return
        
        meal_type = self.recommendation_meal_type_var.get()
        preferences = {'taste': self.taste_preference_var.get()}
        
        self._update_status("正在生成推荐...")
        
        def recommend_thread():
            try:
                # 通过应用核心调用推荐引擎
                if self.app_core and self.app_core.module_manager:
                    result = self.app_core.process_user_request(
                        ModuleType.RECOMMENDATION,
                        {'type': 'meal_recommendation', 'meal_type': meal_type, 'preferences': preferences},
                        self.current_user_id
                    )
                    
                    if result and result.result:
                        self.root.after(0, lambda: self._display_recommendation_result(result.result))
                    else:
                        self.root.after(0, lambda: self._update_status("推荐生成失败"))
                else:
                    self.root.after(0, lambda: self._update_status("应用核心未初始化"))
            except Exception as e:
                self.root.after(0, lambda: self._update_status(f"推荐生成错误: {str(e)}"))
        
        threading.Thread(target=recommend_thread, daemon=True).start()
    
    def _display_recommendation_result(self, result: Dict):
        """显示推荐结果"""
        self.recommendation_result_text.delete("1.0", "end")
        
        if result.get('success'):
            recommendations = result.get('recommendations', [])
            content = f"推荐理由: {result.get('reasoning', '无')}\n\n"
            content += f"置信度: {result.get('confidence', 0):.2f}\n\n"
            content += "推荐餐食搭配:\n\n"
            
            for i, combo in enumerate(recommendations, 1):
                content += f"{i}. {combo.get('name', '搭配')}\n"
                content += f"   描述: {combo.get('description', '')}\n"
                content += f"   食物: {', '.join([f['name'] for f in combo.get('foods', [])])}\n"
                content += f"   总热量: {combo.get('total_calories', 0):.0f}卡路里\n"
                content += f"   个性化得分: {combo.get('personalization_score', 0):.2f}\n"
                content += f"   营养得分: {combo.get('nutrition_score', 0):.2f}\n"
                content += f"   来源: {combo.get('source', 'unknown')}\n\n"
        else:
            content = f"推荐失败: {result.get('error', '未知错误')}"
        
        self.recommendation_result_text.insert("1.0", content)
        self._update_status("推荐生成完成")
    
    def _refresh_profile_info(self):
        """刷新个人信息"""
        if not self.current_user_id:
            messagebox.showwarning("警告", "请先登录")
            return
        
        user_data = self.app_core.get_user_data(self.current_user_id)
        if user_data:
            self._display_profile_info(user_data)
            self._display_stats_info(user_data)
        else:
            messagebox.showerror("错误", "无法获取用户信息")
    
    def _display_profile_info(self, user_data: UserData):
        """显示个人信息"""
        self.profile_info_text.delete("1.0", "end")
        
        profile = user_data.profile
        content = f"""
用户ID: {user_data.user_id}
姓名: {profile.get('name', '未设置')}
年龄: {profile.get('age', '未设置')}
性别: {profile.get('gender', '未设置')}
身高: {profile.get('height', '未设置')}cm
体重: {profile.get('weight', '未设置')}kg
活动水平: {profile.get('activity_level', '未设置')}
口味偏好: {json.dumps(profile.get('taste_preferences', {}), ensure_ascii=False)}
过敏食物: {', '.join(profile.get('allergies', []))}
不喜欢的食物: {', '.join(profile.get('dislikes', []))}
健康目标: {', '.join(profile.get('health_goals', []))}
创建时间: {user_data.created_at}
更新时间: {user_data.updated_at}
"""
        
        self.profile_info_text.insert("1.0", content)
    
    def _display_stats_info(self, user_data: UserData):
        """显示统计信息"""
        self.stats_text.delete("1.0", "end")
        
        meal_count = len(user_data.meals)
        feedback_count = len(user_data.feedback)
        
        # 计算平均满意度
        satisfaction_scores = [meal.get('satisfaction_score', 0) for meal in user_data.meals if meal.get('satisfaction_score')]
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
        
        content = f"""
数据统计:
- 餐食记录数: {meal_count}
- 反馈记录数: {feedback_count}
- 平均满意度: {avg_satisfaction:.2f}

最近餐食:
"""
        
        for meal in user_data.meals[-5:]:  # 显示最近5餐
            content += f"- {meal.get('date', '')} {meal.get('meal_type', '')}: {', '.join(meal.get('foods', []))}\n"
        
        self.stats_text.insert("1.0", content)
    
    def set_current_user(self, user_id: str, user_data: UserData):
        """设置当前用户"""
        self.current_user_id = user_id
        self.current_user_data = user_data
        
        # 更新用户信息显示
        self.user_label.configure(text=f"用户: {user_data.profile.get('name', user_id)}")
        self.login_button.configure(text="切换用户")
        
        # 刷新个人信息
        self._refresh_profile_info()
    
    def destroy(self):
        """销毁窗口"""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def _show_quick_input_dialog(self):
        """显示快速录入对话框"""
        if not self.current_user_id:
            messagebox.showwarning("警告", "请先登录")
            return
        
        try:
            from gui.quick_user_input import show_quick_user_input_dialog
            show_quick_user_input_dialog(self.root, self.current_user_id)
        except Exception as e:
            messagebox.showerror("错误", f"打开快速录入失败: {str(e)}")
    
    def _show_smart_meal_record(self):
        """显示智能餐食记录对话框"""
        if not self.current_user_id:
            messagebox.showwarning("警告", "请先登录")
            return
        
        try:
            from gui.smart_meal_record import show_smart_meal_record_dialog
            show_smart_meal_record_dialog(self.root, self.current_user_id, self.meal_type_var.get())
        except Exception as e:
            messagebox.showerror("错误", f"打开智能记录失败: {str(e)}")


class LoginDialog:
    """登录对话框"""
    
    def __init__(self, parent, main_window):
        self.main_window = main_window
        
        # 创建对话框
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("用户登录/注册")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建对话框组件"""
        # 标题
        title_label = ctk.CTkLabel(
            self.dialog, 
            text="用户登录/注册", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20)
        
        # 用户ID输入
        user_id_label = ctk.CTkLabel(self.dialog, text="用户ID:")
        user_id_label.pack(pady=5)
        
        self.user_id_var = tk.StringVar()
        user_id_entry = ctk.CTkEntry(self.dialog, textvariable=self.user_id_var, width=250)
        user_id_entry.pack(pady=5)
        
        # 用户名输入
        name_label = ctk.CTkLabel(self.dialog, text="姓名:")
        name_label.pack(pady=5)
        
        self.name_var = tk.StringVar()
        name_entry = ctk.CTkEntry(self.dialog, textvariable=self.name_var, width=250)
        name_entry.pack(pady=5)
        
        # 按钮框架
        button_frame = ctk.CTkFrame(self.dialog)
        button_frame.pack(pady=20)
        
        # 登录按钮
        login_button = ctk.CTkButton(
            button_frame,
            text="登录/注册",
            command=self._login,
            width=100
        )
        login_button.pack(side="left", padx=10)
        
        # 取消按钮
        cancel_button = ctk.CTkButton(
            button_frame,
            text="取消",
            command=self._cancel,
            width=100
        )
        cancel_button.pack(side="left", padx=10)
    
    def _login(self):
        """登录处理"""
        user_id = self.user_id_var.get().strip()
        name = self.name_var.get().strip()
        
        if not user_id:
            messagebox.showwarning("警告", "请输入用户ID")
            return
        
        if not name:
            messagebox.showwarning("警告", "请输入姓名")
            return
        
        try:
            # 创建或获取用户数据
            user_data = self.main_window.app_core.get_user_data(user_id)
            
            if not user_data:
                # 创建新用户
                initial_data = {
                    'profile': {
                        'name': name,
                        'age': 25,
                        'gender': '女',
                        'height': 165,
                        'weight': 55,
                        'activity_level': 'moderate'
                    },
                    'preferences': {}
                }
                
                if self.main_window.app_core.create_user(user_id, initial_data):
                    user_data = self.main_window.app_core.get_user_data(user_id)
                    messagebox.showinfo("成功", "新用户创建成功")
                else:
                    messagebox.showerror("错误", "用户创建失败")
                    return
            
            # 设置当前用户
            self.main_window.set_current_user(user_id, user_data)
            
            # 关闭对话框
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"登录失败: {str(e)}")
    
    def _cancel(self):
        """取消登录"""
        self.dialog.destroy()


if __name__ == "__main__":
    # 测试GUI
    root = tk.Tk()
    app = MainWindow(root, None)
    root.mainloop()
