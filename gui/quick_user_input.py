"""
快速用户需求录入界面
优化用户录入流程，提高效率
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import Dict, List, Optional
from datetime import datetime
import json


class QuickUserInputDialog:
    """快速用户需求录入对话框"""
    
    def __init__(self, parent, user_id: str):
        self.parent = parent
        self.user_id = user_id
        self.input_data = {}
        
        # 创建对话框
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("快速需求录入")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🚀 快速需求录入", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # 步骤1：基础信息
        self._create_basic_info_section(main_frame)
        
        # 步骤2：饮食偏好
        self._create_preferences_section(main_frame)
        
        # 步骤3：健康目标
        self._create_health_goals_section(main_frame)
        
        # 步骤4：快速餐食记录
        self._create_quick_meal_section(main_frame)
        
        # 按钮区域
        self._create_buttons(main_frame)
    
    def _create_basic_info_section(self, parent):
        """创建基础信息区域"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # 标题
        title = ctk.CTkLabel(
            section_frame, 
            text="1️⃣ 基础信息", 
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
        
        # 年龄范围
        age_label = ctk.CTkLabel(info_frame, text="年龄范围:")
        age_label.grid(row=0, column=2, sticky="w", padx=10, pady=5)
        
        self.age_var = tk.StringVar(value="25-30岁")
        age_menu = ctk.CTkOptionMenu(
            info_frame,
            variable=self.age_var,
            values=["18-24岁", "25-30岁", "31-35岁", "36-40岁", "41-45岁", "46-50岁", "51-55岁", "56-60岁", "60岁以上"]
        )
        age_menu.grid(row=0, column=3, sticky="w", padx=10, pady=5)
        
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
        
        # 身高体重范围
        height_label = ctk.CTkLabel(info_frame, text="身高范围:")
        height_label.grid(row=1, column=2, sticky="w", padx=10, pady=5)
        
        self.height_var = tk.StringVar(value="160-165cm")
        height_menu = ctk.CTkOptionMenu(
            info_frame,
            variable=self.height_var,
            values=["150cm以下", "150-155cm", "155-160cm", "160-165cm", "165-170cm", "170-175cm", "175-180cm", "180cm以上"]
        )
        height_menu.grid(row=1, column=3, sticky="w", padx=10, pady=5)
        
        weight_label = ctk.CTkLabel(info_frame, text="体重范围:")
        weight_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        self.weight_var = tk.StringVar(value="50-55kg")
        weight_menu = ctk.CTkOptionMenu(
            info_frame,
            variable=self.weight_var,
            values=["40kg以下", "40-45kg", "45-50kg", "50-55kg", "55-60kg", "60-65kg", "65-70kg", "70-75kg", "75-80kg", "80kg以上"]
        )
        weight_menu.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # 活动水平
        activity_label = ctk.CTkLabel(info_frame, text="活动水平:")
        activity_label.grid(row=2, column=2, sticky="w", padx=10, pady=5)
        
        self.activity_var = tk.StringVar(value="中等")
        activity_menu = ctk.CTkOptionMenu(
            info_frame,
            variable=self.activity_var,
            values=["久坐", "轻度活动", "中等", "高度活动", "极度活动"]
        )
        activity_menu.grid(row=2, column=3, sticky="w", padx=10, pady=5)
    
    def _create_preferences_section(self, parent):
        """创建饮食偏好区域"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # 标题
        title = ctk.CTkLabel(
            section_frame, 
            text="2️⃣ 饮食偏好", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # 偏好网格
        pref_frame = ctk.CTkFrame(section_frame)
        pref_frame.pack(fill="x", padx=20, pady=10)
        
        # 口味偏好
        taste_label = ctk.CTkLabel(pref_frame, text="主要口味偏好:")
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
            values=["普通饮食", "素食", "低脂饮食", "低糖饮食", "高蛋白饮食", "地中海饮食"]
        )
        diet_menu.grid(row=0, column=3, sticky="w", padx=10, pady=5)
        
        # 过敏食物
        allergy_label = ctk.CTkLabel(pref_frame, text="过敏食物:")
        allergy_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.allergy_var = tk.StringVar(value="无")
        allergy_menu = ctk.CTkOptionMenu(
            pref_frame,
            variable=self.allergy_var,
            values=["无", "花生", "海鲜", "牛奶", "鸡蛋", "坚果", "大豆", "小麦", "其他"]
        )
        allergy_menu.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # 不喜欢食物
        dislike_label = ctk.CTkLabel(pref_frame, text="不喜欢食物:")
        dislike_label.grid(row=1, column=2, sticky="w", padx=10, pady=5)
        
        self.dislike_var = tk.StringVar(value="无")
        dislike_menu = ctk.CTkOptionMenu(
            pref_frame,
            variable=self.dislike_var,
            values=["无", "内脏", "辛辣", "油腻", "甜食", "酸味", "苦味", "其他"]
        )
        dislike_menu.grid(row=1, column=3, sticky="w", padx=10, pady=5)
    
    def _create_health_goals_section(self, parent):
        """创建健康目标区域"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # 标题
        title = ctk.CTkLabel(
            section_frame, 
            text="3️⃣ 健康目标", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # 目标选择
        goals_frame = ctk.CTkFrame(section_frame)
        goals_frame.pack(fill="x", padx=20, pady=10)
        
        # 主要目标
        main_goal_label = ctk.CTkLabel(goals_frame, text="主要目标:")
        main_goal_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.main_goal_var = tk.StringVar(value="保持健康")
        main_goal_menu = ctk.CTkOptionMenu(
            goals_frame,
            variable=self.main_goal_var,
            values=["保持健康", "减重", "增重", "增肌", "改善消化", "提高免疫力", "控制血糖", "降低血压"]
        )
        main_goal_menu.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # 次要目标
        sub_goal_label = ctk.CTkLabel(goals_frame, text="次要目标:")
        sub_goal_label.grid(row=0, column=2, sticky="w", padx=10, pady=5)
        
        self.sub_goal_var = tk.StringVar(value="无")
        sub_goal_menu = ctk.CTkOptionMenu(
            goals_frame,
            variable=self.sub_goal_var,
            values=["无", "改善睡眠", "提高精力", "美容养颜", "延缓衰老", "改善皮肤", "增强记忆", "缓解压力"]
        )
        sub_goal_menu.grid(row=0, column=3, sticky="w", padx=10, pady=5)
    
    def _create_quick_meal_section(self, parent):
        """创建快速餐食记录区域"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # 标题
        title = ctk.CTkLabel(
            section_frame, 
            text="4️⃣ 快速餐食记录", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # 餐食选择
        meal_frame = ctk.CTkFrame(section_frame)
        meal_frame.pack(fill="x", padx=20, pady=10)
        
        # 餐次选择
        meal_type_label = ctk.CTkLabel(meal_frame, text="餐次:")
        meal_type_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.meal_type_var = tk.StringVar(value="午餐")
        meal_type_menu = ctk.CTkOptionMenu(
            meal_frame,
            variable=self.meal_type_var,
            values=["早餐", "午餐", "晚餐", "加餐"]
        )
        meal_type_menu.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # 快速食物选择
        food_label = ctk.CTkLabel(meal_frame, text="快速选择食物:")
        food_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.quick_food_var = tk.StringVar(value="米饭+鸡肉+蔬菜")
        quick_food_menu = ctk.CTkOptionMenu(
            meal_frame,
            variable=self.quick_food_var,
            values=[
                "米饭+鸡肉+蔬菜",
                "面条+鸡蛋+青菜",
                "馒头+豆腐+白菜",
                "粥+咸菜+鸡蛋",
                "面包+牛奶+水果",
                "饺子+汤",
                "包子+豆浆",
                "其他"
            ]
        )
        quick_food_menu.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # 分量选择
        portion_label = ctk.CTkLabel(meal_frame, text="分量:")
        portion_label.grid(row=1, column=2, sticky="w", padx=10, pady=5)
        
        self.portion_var = tk.StringVar(value="正常")
        portion_menu = ctk.CTkOptionMenu(
            meal_frame,
            variable=self.portion_var,
            values=["少量", "正常", "较多", "很多"]
        )
        portion_menu.grid(row=1, column=3, sticky="w", padx=10, pady=5)
        
        # 满意度
        satisfaction_label = ctk.CTkLabel(meal_frame, text="满意度:")
        satisfaction_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        self.satisfaction_var = tk.IntVar(value=3)
        satisfaction_slider = ctk.CTkSlider(
            meal_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            variable=self.satisfaction_var
        )
        satisfaction_slider.grid(row=2, column=1, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # 满意度标签
        self.satisfaction_display = ctk.CTkLabel(meal_frame, text="3分 - 一般")
        self.satisfaction_display.grid(row=2, column=3, sticky="w", padx=10, pady=5)
        
        # 绑定滑块事件
        satisfaction_slider.configure(command=self._on_satisfaction_changed)
    
    def _create_buttons(self, parent):
        """创建按钮区域"""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", padx=10, pady=20)
        
        # 保存按钮
        save_button = ctk.CTkButton(
            button_frame,
            text="💾 保存所有信息",
            command=self._save_all_data,
            width=200,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        save_button.pack(side="left", padx=20, pady=10)
        
        # 取消按钮
        cancel_button = ctk.CTkButton(
            button_frame,
            text="❌ 取消",
            command=self._cancel,
            width=150,
            height=50
        )
        cancel_button.pack(side="right", padx=20, pady=10)
    
    def _on_satisfaction_changed(self, value):
        """满意度改变事件"""
        score = int(float(value))
        score_texts = {
            1: "1分 - 很不满意",
            2: "2分 - 不满意", 
            3: "3分 - 一般",
            4: "4分 - 满意",
            5: "5分 - 很满意"
        }
        self.satisfaction_display.configure(text=score_texts.get(score, "3分 - 一般"))
    
    def _save_all_data(self):
        """保存所有数据"""
        try:
            # 收集所有数据
            self.input_data = {
                'basic_info': {
                    'name': self.name_var.get(),
                    'age_range': self.age_var.get(),
                    'gender': self.gender_var.get(),
                    'height_range': self.height_var.get(),
                    'weight_range': self.weight_var.get(),
                    'activity_level': self.activity_var.get()
                },
                'preferences': {
                    'taste': self.taste_var.get(),
                    'diet_type': self.diet_var.get(),
                    'allergies': self.allergy_var.get(),
                    'dislikes': self.dislike_var.get()
                },
                'health_goals': {
                    'main_goal': self.main_goal_var.get(),
                    'sub_goal': self.sub_goal_var.get()
                },
                'quick_meal': {
                    'meal_type': self.meal_type_var.get(),
                    'food_combo': self.quick_food_var.get(),
                    'portion': self.portion_var.get(),
                    'satisfaction': self.satisfaction_var.get()
                }
            }
            
            # 保存到数据库
            if self._save_to_database():
                messagebox.showinfo("成功", "所有信息保存成功！")
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "保存失败，请重试")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def _save_to_database(self) -> bool:
        """保存到数据库"""
        try:
            from modules.data_collection import collect_questionnaire_data, record_meal
            
            # 保存基础信息
            basic_data = self.input_data['basic_info']
            age_mapping = {
                "18-24岁": 21, "25-30岁": 27, "31-35岁": 33, "36-40岁": 38,
                "41-45岁": 43, "46-50岁": 48, "51-55岁": 53, "56-60岁": 58, "60岁以上": 65
            }
            height_mapping = {
                "150cm以下": 150, "150-155cm": 152, "155-160cm": 157, "160-165cm": 162,
                "165-170cm": 167, "170-175cm": 172, "175-180cm": 177, "180cm以上": 180
            }
            weight_mapping = {
                "40kg以下": 40, "40-45kg": 42, "45-50kg": 47, "50-55kg": 52,
                "55-60kg": 57, "60-65kg": 62, "65-70kg": 67, "70-75kg": 72,
                "75-80kg": 77, "80kg以上": 80
            }
            activity_mapping = {
                "久坐": "sedentary", "轻度活动": "light", "中等": "moderate",
                "高度活动": "high", "极度活动": "very_high"
            }
            
            basic_answers = {
                'name': basic_data['name'],
                'age': age_mapping.get(basic_data['age_range'], 25),
                'gender': basic_data['gender'],
                'height': height_mapping.get(basic_data['height_range'], 165),
                'weight': weight_mapping.get(basic_data['weight_range'], 55),
                'activity_level': activity_mapping.get(basic_data['activity_level'], 'moderate')
            }
            
            collect_questionnaire_data(self.user_id, 'basic', basic_answers)
            
            # 保存口味偏好
            preferences_data = self.input_data['preferences']
            taste_answers = {
                'taste_preference': preferences_data['taste'],
                'diet_type': preferences_data['diet_type'],
                'allergies': [preferences_data['allergies']] if preferences_data['allergies'] != "无" else [],
                'dislikes': [preferences_data['dislikes']] if preferences_data['dislikes'] != "无" else []
            }
            
            collect_questionnaire_data(self.user_id, 'taste', taste_answers)
            
            # 保存健康目标
            health_data = self.input_data['health_goals']
            health_answers = {
                'main_goal': health_data['main_goal'],
                'sub_goal': health_data['sub_goal']
            }
            
            collect_questionnaire_data(self.user_id, 'health', health_answers)
            
            # 保存快速餐食记录
            meal_data = self.input_data['quick_meal']
            meal_type_mapping = {
                "早餐": "breakfast", "午餐": "lunch", "晚餐": "dinner", "加餐": "snack"
            }
            
            # 解析食物组合
            food_combo = meal_data['food_combo']
            if "+" in food_combo:
                foods = [food.strip() for food in food_combo.split("+")]
            else:
                foods = [food_combo]
            
            # 估算分量
            portion_mapping = {
                "少量": "1小份", "正常": "1份", "较多": "1大份", "很多": "2份"
            }
            quantities = [portion_mapping.get(meal_data['portion'], "1份")] * len(foods)
            
            meal_record = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'meal_type': meal_type_mapping.get(meal_data['meal_type'], 'lunch'),
                'foods': foods,
                'quantities': quantities,
                'satisfaction_score': meal_data['satisfaction']
            }
            
            record_meal(self.user_id, meal_record)
            
            return True
            
        except Exception as e:
            print(f"保存到数据库失败: {e}")
            return False
    
    def _cancel(self):
        """取消录入"""
        self.dialog.destroy()


# 便捷函数
def show_quick_user_input_dialog(parent, user_id: str):
    """显示快速用户需求录入对话框"""
    dialog = QuickUserInputDialog(parent, user_id)
    parent.wait_window(dialog.dialog)


if __name__ == "__main__":
    # 测试快速录入对话框
    root = tk.Tk()
    root.title("测试快速录入")
    def test_dialog():
        show_quick_user_input_dialog(root, "test_user")
    test_button = tk.Button(root, text="测试快速录入", command=test_dialog)
    test_button.pack(pady=20)
    root.mainloop()
