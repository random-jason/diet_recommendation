"""
简化的餐食记录界面
使用选择式输入，减少用户负担
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import Dict, List, Optional
from smart_food.smart_database import (
    search_foods, get_food_categories, get_foods_by_category, 
    get_portion_options, estimate_calories, record_meal_smart
)


class SmartMealRecordDialog:
    """智能餐食记录对话框"""
    
    def __init__(self, parent, user_id: str, meal_type: str = "lunch"):
        self.parent = parent
        self.user_id = user_id
        self.meal_type = meal_type
        self.selected_foods = []
        
        # 创建对话框
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(f"记录{self._get_meal_name(meal_type)}")
        self.dialog.geometry("600x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self._create_widgets()
    
    def _get_meal_name(self, meal_type: str) -> str:
        """获取餐次中文名称"""
        meal_names = {
            "breakfast": "早餐",
            "lunch": "午餐", 
            "dinner": "晚餐"
        }
        return meal_names.get(meal_type, "餐食")
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ctk.CTkLabel(
            main_frame, 
            text=f"🍽️ 记录{self._get_meal_name(self.meal_type)}", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10)
        
        # 食物选择区域
        self._create_food_selection(main_frame)
        
        # 已选食物列表
        self._create_selected_foods(main_frame)
        
        # 满意度评分
        self._create_satisfaction_rating(main_frame)
        
        # 备注
        self._create_notes_section(main_frame)
        
        # 按钮区域
        self._create_buttons(main_frame)
    
    def _create_food_selection(self, parent):
        """创建食物选择区域"""
        # 食物选择框架
        food_frame = ctk.CTkFrame(parent)
        food_frame.pack(fill="x", padx=10, pady=10)
        
        # 标题
        food_title = ctk.CTkLabel(
            food_frame, 
            text="选择食物", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        food_title.pack(pady=10)
        
        # 食物搜索
        search_frame = ctk.CTkFrame(food_frame)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        search_label = ctk.CTkLabel(search_frame, text="搜索食物:")
        search_label.pack(anchor="w", padx=5, pady=2)
        
        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, placeholder_text="输入食物名称搜索...")
        self.search_entry.pack(fill="x", padx=5, pady=2)
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)
        
        # 搜索结果
        self.search_results_frame = ctk.CTkFrame(food_frame)
        self.search_results_frame.pack(fill="x", padx=10, pady=5)
        
        self.search_results_label = ctk.CTkLabel(self.search_results_frame, text="搜索结果:")
        self.search_results_label.pack(anchor="w", padx=5, pady=2)
        
        self.search_results_menu = ctk.CTkOptionMenu(
            self.search_results_frame,
            values=[],
            command=self._on_search_result_selected
        )
        self.search_results_menu.pack(fill="x", padx=5, pady=2)
        
        # 分隔线
        separator = ctk.CTkFrame(food_frame, height=2)
        separator.pack(fill="x", padx=10, pady=5)
        
        # 分类选择
        category_frame = ctk.CTkFrame(food_frame)
        category_frame.pack(fill="x", padx=10, pady=5)
        
        category_label = ctk.CTkLabel(category_frame, text="食物分类:")
        category_label.pack(side="left", padx=5)
        
        self.category_var = tk.StringVar(value="主食")
        self.category_menu = ctk.CTkOptionMenu(
            category_frame,
            variable=self.category_var,
            values=get_food_categories(),
            command=self._on_category_changed
        )
        self.category_menu.pack(side="left", padx=5)
        
        # 食物选择
        food_select_frame = ctk.CTkFrame(food_frame)
        food_select_frame.pack(fill="x", padx=10, pady=5)
        
        food_label = ctk.CTkLabel(food_select_frame, text="选择食物:")
        food_label.pack(anchor="w", padx=5, pady=2)
        
        self.food_var = tk.StringVar()
        self.food_menu = ctk.CTkOptionMenu(
            food_select_frame,
            variable=self.food_var,
            values=[]
        )
        self.food_menu.pack(fill="x", padx=5, pady=2)
        
        # 分量选择
        portion_frame = ctk.CTkFrame(food_frame)
        portion_frame.pack(fill="x", padx=10, pady=5)
        
        portion_label = ctk.CTkLabel(portion_frame, text="分量:")
        portion_label.pack(anchor="w", padx=5, pady=2)
        
        self.portion_var = tk.StringVar(value="适量")
        self.portion_menu = ctk.CTkOptionMenu(
            portion_frame,
            variable=self.portion_var,
            values=["适量"]
        )
        self.portion_menu.pack(fill="x", padx=5, pady=2)
        
        # 添加按钮
        add_button = ctk.CTkButton(
            food_frame,
            text="添加到餐食",
            command=self._add_food,
            width=150
        )
        add_button.pack(pady=10)
        
        # AI分析按钮
        ai_analyze_button = ctk.CTkButton(
            food_frame,
            text="AI分析食物",
            command=self._analyze_food_with_ai,
            width=150,
            fg_color="green"
        )
        ai_analyze_button.pack(pady=5)
        
        # 初始化食物列表
        self._on_category_changed("主食")
    
    def _create_selected_foods(self, parent):
        """创建已选食物列表"""
        # 已选食物框架
        selected_frame = ctk.CTkFrame(parent)
        selected_frame.pack(fill="x", padx=10, pady=10)
        
        # 标题
        selected_title = ctk.CTkLabel(
            selected_frame, 
            text="已选食物", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        selected_title.pack(pady=10)
        
        # 食物列表
        self.foods_listbox = tk.Listbox(selected_frame, height=6)
        self.foods_listbox.pack(fill="x", padx=10, pady=5)
        
        # 删除按钮
        delete_button = ctk.CTkButton(
            selected_frame,
            text="删除选中",
            command=self._remove_food,
            width=150
        )
        delete_button.pack(pady=5)
    
    def _create_satisfaction_rating(self, parent):
        """创建满意度评分"""
        # 满意度框架
        satisfaction_frame = ctk.CTkFrame(parent)
        satisfaction_frame.pack(fill="x", padx=10, pady=10)
        
        # 标题
        satisfaction_title = ctk.CTkLabel(
            satisfaction_frame, 
            text="满意度评分", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        satisfaction_title.pack(pady=10)
        
        # 评分滑块
        self.satisfaction_var = tk.IntVar(value=3)
        satisfaction_slider = ctk.CTkSlider(
            satisfaction_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            variable=self.satisfaction_var
        )
        satisfaction_slider.pack(fill="x", padx=20, pady=10)
        
        # 评分标签
        self.satisfaction_label = ctk.CTkLabel(
            satisfaction_frame, 
            text="3分 - 一般", 
            font=ctk.CTkFont(size=14)
        )
        self.satisfaction_label.pack(pady=5)
        
        # 绑定滑块事件
        satisfaction_slider.configure(command=self._on_satisfaction_changed)
    
    def _create_notes_section(self, parent):
        """创建备注区域"""
        # 备注框架
        notes_frame = ctk.CTkFrame(parent)
        notes_frame.pack(fill="x", padx=10, pady=10)
        
        # 标题
        notes_title = ctk.CTkLabel(
            notes_frame, 
            text="备注 (可选)", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        notes_title.pack(pady=10)
        
        # 备注输入
        self.notes_text = ctk.CTkTextbox(notes_frame, height=60)
        self.notes_text.pack(fill="x", padx=10, pady=5)
        self.notes_text.insert("1.0", "可以记录一些感受或特殊说明...")
    
    def _create_buttons(self, parent):
        """创建按钮区域"""
        # 按钮框架
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", padx=10, pady=20)
        
        # 保存按钮
        save_button = ctk.CTkButton(
            button_frame,
            text="保存餐食记录",
            command=self._save_meal,
            width=150,
            height=40
        )
        save_button.pack(side="left", padx=20, pady=10)
        
        # 取消按钮
        cancel_button = ctk.CTkButton(
            button_frame,
            text="取消",
            command=self._cancel,
            width=150,
            height=40
        )
        cancel_button.pack(side="right", padx=20, pady=10)
    
    def _on_search_changed(self, event=None):
        """搜索输入改变事件"""
        query = self.search_var.get().strip()
        if not query:
            self.search_results_menu.configure(values=[])
            return
        
        try:
            from smart_food.smart_database import search_foods
            results = search_foods(query)
            if results:
                food_names = [result["name"] for result in results]
                self.search_results_menu.configure(values=food_names)
                self.search_results_label.configure(text=f"搜索结果 ({len(food_names)}个):")
            else:
                self.search_results_menu.configure(values=[])
                self.search_results_label.configure(text="未找到匹配的食物")
        except Exception as e:
            self.search_results_menu.configure(values=[])
            self.search_results_label.configure(text="搜索失败")
    
    def _on_search_result_selected(self, food_name):
        """搜索结果选择事件"""
        self.food_var.set(food_name)
        self._on_food_changed(food_name)
        
        # 自动选择对应的分类
        try:
            from smart_food.smart_database import get_food_categories, get_foods_by_category
            categories = get_food_categories()
            for category in categories:
                foods_in_category = get_foods_by_category(category)
                if food_name in foods_in_category:
                    self.category_var.set(category)
                    self._on_category_changed(category)
                    break
        except Exception:
            pass
    
    def _analyze_food_with_ai(self):
        """使用AI分析食物"""
        food_name = self.food_var.get()
        portion = self.portion_var.get()
        
        if not food_name:
            messagebox.showwarning("警告", "请选择食物")
            return
        
        try:
            from smart_food.smart_database import analyze_food_with_ai
            
            # 显示分析进度
            self._show_ai_analysis_dialog(food_name, portion)
            
        except Exception as e:
            messagebox.showerror("错误", f"AI分析失败: {str(e)}")
    
    def _show_ai_analysis_dialog(self, food_name: str, portion: str):
        """显示AI分析对话框"""
        # 创建分析对话框
        analysis_dialog = ctk.CTkToplevel(self.dialog)
        analysis_dialog.title(f"AI分析 - {food_name}")
        analysis_dialog.geometry("500x600")
        analysis_dialog.transient(self.dialog)
        analysis_dialog.grab_set()
        
        # 居中显示
        analysis_dialog.geometry("+%d+%d" % (self.dialog.winfo_rootx() + 50, self.dialog.winfo_rooty() + 50))
        
        # 创建滚动框架
        scroll_frame = ctk.CTkScrollableFrame(analysis_dialog)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ctk.CTkLabel(
            scroll_frame, 
            text=f"🤖 AI分析: {food_name}", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=10)
        
        # 分析进度
        progress_label = ctk.CTkLabel(scroll_frame, text="正在分析中...")
        progress_label.pack(pady=10)
        
        # 分析结果区域
        result_text = ctk.CTkTextbox(scroll_frame, height=400, width=450)
        result_text.pack(fill="both", expand=True, pady=10)
        
        # 关闭按钮
        close_button = ctk.CTkButton(
            scroll_frame,
            text="关闭",
            command=analysis_dialog.destroy,
            width=100
        )
        close_button.pack(pady=10)
        
        # 在后台线程中执行AI分析
        import threading
        
        def analyze_thread():
            try:
                from smart_food.smart_database import analyze_food_with_ai
                
                # 执行AI分析
                result = analyze_food_with_ai(food_name, portion)
                
                # 更新UI
                analysis_dialog.after(0, lambda: self._update_ai_analysis_result(
                    analysis_dialog, result_text, progress_label, result
                ))
                
            except Exception as e:
                analysis_dialog.after(0, lambda: self._update_ai_analysis_error(
                    analysis_dialog, result_text, progress_label, str(e)
                ))
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def _update_ai_analysis_result(self, dialog, result_text, progress_label, result):
        """更新AI分析结果"""
        progress_label.configure(text="分析完成")
        
        if result.get('success'):
            content = f"""
🍎 食物分析结果: {result.get('reasoning', 'AI分析')}

📊 营养成分:
- 热量: {result.get('calories', 0)} 卡路里
- 蛋白质: {result.get('protein', 0):.1f} 克
- 碳水化合物: {result.get('carbs', 0):.1f} 克
- 脂肪: {result.get('fat', 0):.1f} 克
- 纤维: {result.get('fiber', 0):.1f} 克

🏷️ 分类: {result.get('category', '其他')}

💡 健康建议:
"""
            for tip in result.get('health_tips', []):
                content += f"• {tip}\n"
            
            content += "\n👨‍🍳 制作建议:\n"
            for suggestion in result.get('cooking_suggestions', []):
                content += f"• {suggestion}\n"
            
            content += f"\n🎯 置信度: {result.get('confidence', 0.5):.1%}"
        else:
            content = "AI分析失败，请稍后重试。"
        
        result_text.delete("1.0", "end")
        result_text.insert("1.0", content)
    
    def _update_ai_analysis_error(self, dialog, result_text, progress_label, error_msg):
        """更新AI分析错误"""
        progress_label.configure(text="分析失败")
        result_text.delete("1.0", "end")
        result_text.insert("1.0", f"AI分析失败: {error_msg}")
    
    def _on_category_changed(self, category):
        """分类改变事件"""
        foods = get_foods_by_category(category)
        self.food_menu.configure(values=foods)
        if foods:
            self.food_var.set(foods[0])
            self._on_food_changed(foods[0])
    
    def _on_food_changed(self, food_name):
        """食物改变事件"""
        portions = get_portion_options(food_name)
        self.portion_menu.configure(values=portions)
        if portions:
            self.portion_var.set(portions[0])
    
    def _add_food(self):
        """添加食物"""
        food_name = self.food_var.get()
        portion = self.portion_var.get()
        
        if not food_name:
            messagebox.showwarning("警告", "请选择食物")
            return
        
        # 估算热量
        calories = estimate_calories(food_name, portion)
        
        # 添加到列表
        food_item = {
            "name": food_name,
            "portion": portion,
            "calories": calories
        }
        
        self.selected_foods.append(food_item)
        self._update_foods_list()
    
    def _update_foods_list(self):
        """更新食物列表显示"""
        self.foods_listbox.delete(0, tk.END)
        
        total_calories = 0
        for i, food_item in enumerate(self.selected_foods):
            display_text = f"{food_item['name']} - {food_item['portion']} ({food_item['calories']}卡)"
            self.foods_listbox.insert(tk.END, display_text)
            total_calories += food_item['calories']
        
        # 显示总热量
        if self.selected_foods:
            total_text = f"总热量: {total_calories}卡路里"
            self.foods_listbox.insert(tk.END, "")
            self.foods_listbox.insert(tk.END, total_text)
    
    def _remove_food(self):
        """删除选中的食物"""
        selection = self.foods_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的食物")
            return
        
        index = selection[0]
        if index < len(self.selected_foods):
            self.selected_foods.pop(index)
            self._update_foods_list()
    
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
        self.satisfaction_label.configure(text=score_texts.get(score, "3分 - 一般"))
    
    def _save_meal(self):
        """保存餐食记录"""
        if not self.selected_foods:
            messagebox.showwarning("警告", "请至少添加一种食物")
            return
        
        try:
            # 构建餐食数据
            meal_data = {
                "meal_type": self.meal_type,
                "foods": self.selected_foods,
                "satisfaction_score": self.satisfaction_var.get(),
                "notes": self.notes_text.get("1.0", "end-1c").strip()
            }
            
            # 智能记录餐食
            if record_meal_smart(self.user_id, meal_data):
                messagebox.showinfo("成功", "餐食记录保存成功！")
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "餐食记录保存失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def _cancel(self):
        """取消记录"""
        self.dialog.destroy()


# 便捷函数
def show_smart_meal_record_dialog(parent, user_id: str, meal_type: str = "lunch"):
    """显示智能餐食记录对话框"""
    dialog = SmartMealRecordDialog(parent, user_id, meal_type)
    parent.wait_window(dialog.dialog)


if __name__ == "__main__":
    # 测试智能餐食记录对话框
    root = tk.Tk()
    root.title("测试智能餐食记录")
    
    def test_dialog():
        show_smart_meal_record_dialog(root, "test_user", "lunch")
    
    test_button = tk.Button(root, text="测试餐食记录", command=test_dialog)
    test_button.pack(pady=20)
    
    root.mainloop()
