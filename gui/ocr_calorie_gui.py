"""
OCR热量识别GUI界面
提供图片上传、OCR识别、结果验证和修正功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import threading
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime
from core.base import UserData, CalorieInfo, FoodRecognitionResult


class OCRCalorieGUI:
    """OCR热量识别GUI界面"""
    
    def __init__(self, parent_window, app_core):
        self.parent_window = parent_window
        self.app_core = app_core
        self.current_image_path = None
        self.current_recognition_result = None
        self.user_corrections = {}
        
        # 创建主框架
        self.main_frame = ttk.Frame(parent_window)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建界面
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        self.title_label = ttk.Label(
            self.main_frame, 
            text="📷 图片OCR热量识别", 
            font=("Arial", 18, "bold"),
            foreground="#2c3e50"
        )
        
        # 图片上传区域
        self.image_frame = ttk.LabelFrame(
            self.main_frame, 
            text="📸 图片上传", 
            padding=15,
            relief="solid",
            borderwidth=1
        )
        
        self.upload_button = ttk.Button(
            self.image_frame,
            text="📁 选择图片",
            command=self._select_image,
            style="Accent.TButton"
        )
        
        self.image_label = ttk.Label(
            self.image_frame,
            text="请选择包含食物信息的图片",
            background="#f8f9fa",
            relief="solid",
            borderwidth=1,
            width=50,
            height=15,
            anchor="center"
        )
        
        # 识别控制区域
        self.control_frame = ttk.LabelFrame(
            self.main_frame, 
            text="⚙️ 识别控制", 
            padding=15,
            relief="solid",
            borderwidth=1
        )
        
        self.recognize_button = ttk.Button(
            self.control_frame,
            text="🚀 开始识别",
            command=self._start_recognition,
            state=tk.DISABLED,
            style="Accent.TButton"
        )
        
        self.progress_bar = ttk.Progressbar(
            self.control_frame,
            mode='indeterminate',
            style="Accent.TProgressbar"
        )
        
        self.status_label = ttk.Label(
            self.control_frame,
            text="✅ 准备就绪",
            foreground="#27ae60"
        )
        
        # 识别结果区域
        self.result_frame = ttk.LabelFrame(self.main_frame, text="识别结果", padding=10)
        
        # 创建结果表格
        self.result_tree = ttk.Treeview(
            self.result_frame,
            columns=('food_name', 'calories', 'confidence', 'source'),
            show='headings',
            height=8
        )
        
        # 设置列标题
        self.result_tree.heading('food_name', text='食物名称')
        self.result_tree.heading('calories', text='热量(卡路里)')
        self.result_tree.heading('confidence', text='置信度')
        self.result_tree.heading('source', text='来源')
        
        # 设置列宽
        self.result_tree.column('food_name', width=150)
        self.result_tree.column('calories', width=100)
        self.result_tree.column('confidence', width=80)
        self.result_tree.column('source', width=100)
        
        # 结果操作按钮
        self.result_button_frame = ttk.Frame(self.result_frame)
        
        self.edit_button = ttk.Button(
            self.result_button_frame,
            text="编辑结果",
            command=self._edit_result,
            state=tk.DISABLED
        )
        
        self.confirm_button = ttk.Button(
            self.result_button_frame,
            text="确认结果",
            command=self._confirm_result,
            state=tk.DISABLED
        )
        
        self.clear_button = ttk.Button(
            self.result_button_frame,
            text="清空结果",
            command=self._clear_results
        )
        
        # 详细信息区域
        self.detail_frame = ttk.LabelFrame(self.main_frame, text="详细信息", padding=10)
        
        self.detail_text = scrolledtext.ScrolledText(
            self.detail_frame,
            height=8,
            width=60
        )
        
        # 建议区域
        self.suggestion_frame = ttk.LabelFrame(self.main_frame, text="建议", padding=10)
        
        self.suggestion_text = scrolledtext.ScrolledText(
            self.suggestion_frame,
            height=4,
            width=60,
            state=tk.DISABLED
        )
    
    def _setup_layout(self):
        """设置布局"""
        # 标题
        self.title_label.pack(pady=(0, 10))
        
        # 图片上传区域
        self.image_frame.pack(fill=tk.X, pady=(0, 10))
        self.upload_button.pack(side=tk.LEFT, padx=(0, 10))
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # 识别控制区域
        self.control_frame.pack(fill=tk.X, pady=(0, 10))
        self.recognize_button.pack(side=tk.LEFT, padx=(0, 10))
        self.progress_bar.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        self.status_label.pack(side=tk.LEFT)
        
        # 识别结果区域
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 结果表格
        result_scrollbar = ttk.Scrollbar(self.result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=result_scrollbar.set)
        
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 结果操作按钮
        self.result_button_frame.pack(fill=tk.X, pady=(10, 0))
        self.edit_button.pack(side=tk.LEFT, padx=(0, 10))
        self.confirm_button.pack(side=tk.LEFT, padx=(0, 10))
        self.clear_button.pack(side=tk.LEFT)
        
        # 详细信息和建议区域
        detail_suggestion_frame = ttk.Frame(self.main_frame)
        detail_suggestion_frame.pack(fill=tk.BOTH, expand=True)
        
        self.detail_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        
        self.suggestion_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self.suggestion_text.pack(fill=tk.BOTH, expand=True)
    
    def _bind_events(self):
        """绑定事件"""
        self.result_tree.bind('<<TreeviewSelect>>', self._on_result_select)
        self.result_tree.bind('<Double-1>', self._on_result_double_click)
    
    def _select_image(self):
        """选择图片文件"""
        file_types = [
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("PNG文件", "*.png"),
            ("所有文件", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="选择包含食物信息的图片",
            filetypes=file_types
        )
        
        if file_path:
            self.current_image_path = file_path
            self._display_image(file_path)
            self.recognize_button.config(state=tk.NORMAL)
            self.status_label.config(text=f"已选择图片: {Path(file_path).name}")
    
    def _display_image(self, image_path: str):
        """显示图片"""
        try:
            # 加载图片
            image = Image.open(image_path)
            
            # 调整图片大小以适应显示区域
            display_size = (400, 300)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # 转换为Tkinter可显示的格式
            photo = ImageTk.PhotoImage(image)
            
            # 更新标签
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # 保持引用
            
        except Exception as e:
            messagebox.showerror("错误", f"无法显示图片: {str(e)}")
            self.image_label.config(image="", text="图片显示失败")
    
    def _start_recognition(self):
        """开始OCR识别"""
        if not self.current_image_path:
            messagebox.showwarning("警告", "请先选择图片")
            return
        
        # 禁用按钮，显示进度条
        self.recognize_button.config(state=tk.DISABLED)
        self.progress_bar.start()
        self.status_label.config(text="正在识别...")
        
        # 在新线程中执行识别
        thread = threading.Thread(target=self._perform_recognition)
        thread.daemon = True
        thread.start()
    
    def _perform_recognition(self):
        """执行OCR识别"""
        try:
            # 准备请求数据
            request_data = {
                'type': 'recognize_image',
                'image_path': self.current_image_path
            }
            
            # 获取当前用户数据（这里需要根据实际情况调整）
            user_data = UserData(
                user_id="current_user",
                profile={},
                meals=[],
                feedback=[],
                preferences={}
            )
            
            # 调用OCR模块
            from modules.ocr_calorie_recognition import OCRCalorieRecognitionModule
            ocr_module = OCRCalorieRecognitionModule(self.app_core.config)
            
            if not ocr_module.initialize():
                raise Exception("OCR模块初始化失败")
            
            result = ocr_module.process(request_data, user_data)
            
            # 在主线程中更新UI
            self.parent_window.after(0, self._on_recognition_complete, result)
            
        except Exception as e:
            self.parent_window.after(0, self._on_recognition_error, str(e))
    
    def _on_recognition_complete(self, result):
        """识别完成回调"""
        try:
            # 停止进度条
            self.progress_bar.stop()
            self.recognize_button.config(state=tk.NORMAL)
            
            if result.result.get('success', False):
                self.current_recognition_result = result.result['result']
                self._display_recognition_results()
                self.status_label.config(text="识别完成")
            else:
                error_msg = result.result.get('error', '识别失败')
                messagebox.showerror("识别失败", error_msg)
                self.status_label.config(text="识别失败")
                
        except Exception as e:
            self._on_recognition_error(str(e))
    
    def _on_recognition_error(self, error_msg: str):
        """识别错误回调"""
        self.progress_bar.stop()
        self.recognize_button.config(state=tk.NORMAL)
        self.status_label.config(text="识别失败")
        messagebox.showerror("识别错误", f"OCR识别过程中出现错误: {error_msg}")
    
    def _display_recognition_results(self):
        """显示识别结果"""
        if not self.current_recognition_result:
            return
        
        try:
            # 清空现有结果
            self._clear_results()
            
            # 显示热量信息
            calorie_infos = self.current_recognition_result.calorie_infos
            
            for info in calorie_infos:
                self.result_tree.insert('', tk.END, values=(
                    info.food_name,
                    f"{info.calories:.1f}" if info.calories else "未知",
                    f"{info.confidence:.2f}",
                    info.source
                ))
            
            # 显示详细信息
            self._update_detail_text()
            
            # 显示建议
            self._update_suggestion_text()
            
            # 启用操作按钮
            self.edit_button.config(state=tk.NORMAL)
            self.confirm_button.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("错误", f"显示识别结果失败: {str(e)}")
    
    def _update_detail_text(self):
        """更新详细信息文本"""
        if not self.current_recognition_result:
            return
        
        try:
            detail_text = "=== OCR识别详细信息 ===\n\n"
            
            # OCR结果
            detail_text += "OCR识别结果:\n"
            for ocr_result in self.current_recognition_result.ocr_results:
                detail_text += f"- 方法: {ocr_result.method}\n"
                detail_text += f"  置信度: {ocr_result.confidence:.2f}\n"
                detail_text += f"  识别文本: {ocr_result.text[:100]}...\n\n"
            
            # 处理时间
            detail_text += f"处理时间: {self.current_recognition_result.processing_time:.2f}秒\n"
            detail_text += f"整体置信度: {self.current_recognition_result.overall_confidence:.2f}\n"
            
            # 热量信息
            detail_text += "\n=== 热量信息 ===\n"
            for info in self.current_recognition_result.calorie_infos:
                detail_text += f"食物: {info.food_name}\n"
                detail_text += f"热量: {info.calories} 卡路里\n"
                detail_text += f"置信度: {info.confidence:.2f}\n"
                detail_text += f"来源: {info.source}\n"
                detail_text += f"原始文本: {info.raw_text}\n\n"
            
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, detail_text)
            
        except Exception as e:
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, f"详细信息加载失败: {str(e)}")
    
    def _update_suggestion_text(self):
        """更新建议文本"""
        if not self.current_recognition_result:
            return
        
        try:
            suggestions = self.current_recognition_result.suggestions
            
            suggestion_text = "=== 建议 ===\n\n"
            for i, suggestion in enumerate(suggestions, 1):
                suggestion_text += f"{i}. {suggestion}\n"
            
            self.suggestion_text.config(state=tk.NORMAL)
            self.suggestion_text.delete(1.0, tk.END)
            self.suggestion_text.insert(1.0, suggestion_text)
            self.suggestion_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.suggestion_text.config(state=tk.NORMAL)
            self.suggestion_text.delete(1.0, tk.END)
            self.suggestion_text.insert(1.0, f"建议加载失败: {str(e)}")
            self.suggestion_text.config(state=tk.DISABLED)
    
    def _on_result_select(self, event):
        """结果选择事件"""
        selection = self.result_tree.selection()
        if selection:
            self.edit_button.config(state=tk.NORMAL)
            self.confirm_button.config(state=tk.NORMAL)
        else:
            self.edit_button.config(state=tk.DISABLED)
            self.confirm_button.config(state=tk.DISABLED)
    
    def _on_result_double_click(self, event):
        """结果双击事件"""
        self._edit_result()
    
    def _edit_result(self):
        """编辑识别结果"""
        selection = self.result_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的结果")
            return
        
        try:
            item = selection[0]
            values = self.result_tree.item(item, 'values')
            
            food_name = values[0]
            calories = values[1]
            
            # 创建编辑对话框
            self._create_edit_dialog(food_name, calories, item)
            
        except Exception as e:
            messagebox.showerror("错误", f"编辑结果失败: {str(e)}")
    
    def _create_edit_dialog(self, food_name: str, calories: str, item_id: str):
        """创建编辑对话框"""
        dialog = tk.Toplevel(self.parent_window)
        dialog.title("编辑识别结果")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # 居中显示
        dialog.transient(self.parent_window)
        dialog.grab_set()
        
        # 创建表单
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 食物名称
        ttk.Label(form_frame, text="食物名称:").pack(anchor=tk.W, pady=(0, 5))
        food_name_var = tk.StringVar(value=food_name)
        food_name_entry = ttk.Entry(form_frame, textvariable=food_name_var, width=40)
        food_name_entry.pack(fill=tk.X, pady=(0, 15))
        
        # 热量
        ttk.Label(form_frame, text="热量(卡路里):").pack(anchor=tk.W, pady=(0, 5))
        calories_var = tk.StringVar(value=calories)
        calories_entry = ttk.Entry(form_frame, textvariable=calories_var, width=40)
        calories_entry.pack(fill=tk.X, pady=(0, 15))
        
        # 置信度
        ttk.Label(form_frame, text="置信度:").pack(anchor=tk.W, pady=(0, 5))
        confidence_var = tk.StringVar(value="0.95")
        confidence_entry = ttk.Entry(form_frame, textvariable=confidence_var, width=40)
        confidence_entry.pack(fill=tk.X, pady=(0, 20))
        
        # 按钮
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X)
        
        def save_changes():
            try:
                new_food_name = food_name_var.get().strip()
                new_calories = calories_var.get().strip()
                new_confidence = float(confidence_var.get())
                
                if not new_food_name:
                    messagebox.showwarning("警告", "食物名称不能为空")
                    return
                
                if new_calories and new_calories != "未知":
                    try:
                        float(new_calories)
                    except ValueError:
                        messagebox.showwarning("警告", "热量必须是数字")
                        return
                
                # 更新表格
                self.result_tree.item(item_id, values=(
                    new_food_name,
                    new_calories,
                    f"{new_confidence:.2f}",
                    "user_corrected"
                ))
                
                # 保存用户修正
                self.user_corrections[new_food_name] = {
                    'calories': float(new_calories) if new_calories and new_calories != "未知" else None,
                    'confidence': new_confidence,
                    'timestamp': datetime.now().isoformat()
                }
                
                dialog.destroy()
                messagebox.showinfo("成功", "结果已更新")
                
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
        
        def cancel_changes():
            dialog.destroy()
        
        ttk.Button(button_frame, text="保存", command=save_changes).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=cancel_changes).pack(side=tk.LEFT)
    
    def _confirm_result(self):
        """确认识别结果"""
        if not self.current_recognition_result:
            messagebox.showwarning("警告", "没有可确认的结果")
            return
        
        try:
            # 获取所有结果
            results = []
            for item in self.result_tree.get_children():
                values = self.result_tree.item(item, 'values')
                results.append({
                    'food_name': values[0],
                    'calories': float(values[1]) if values[1] != "未知" else None,
                    'confidence': float(values[2]),
                    'source': values[3]
                })
            
            if not results:
                messagebox.showwarning("警告", "没有可确认的结果")
                return
            
            # 确认对话框
            confirm_msg = "确认以下识别结果:\n\n"
            for i, result in enumerate(results, 1):
                confirm_msg += f"{i}. {result['food_name']}: {result['calories']} 卡路里\n"
            
            confirm_msg += "\n是否确认这些结果？"
            
            if messagebox.askyesno("确认结果", confirm_msg):
                # 保存到餐食记录
                self._save_to_meal_record(results)
                messagebox.showinfo("成功", "结果已保存到餐食记录")
                
                # 清空结果
                self._clear_results()
        
        except Exception as e:
            messagebox.showerror("错误", f"确认结果失败: {str(e)}")
    
    def _save_to_meal_record(self, results: List[Dict[str, Any]]):
        """保存到餐食记录"""
        try:
            # 这里需要调用应用核心的餐食记录功能
            # 暂时保存到本地文件
            meal_record = {
                'timestamp': datetime.now().isoformat(),
                'source': 'ocr_recognition',
                'foods': results,
                'total_calories': sum(r['calories'] for r in results if r['calories'])
            }
            
            # 保存到文件
            record_file = Path("data/ocr_meal_records.json")
            record_file.parent.mkdir(parents=True, exist_ok=True)
            
            records = []
            if record_file.exists():
                with open(record_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            
            records.append(meal_record)
            
            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            self.logger.error(f"保存餐食记录失败: {e}")
            raise
    
    def _clear_results(self):
        """清空识别结果"""
        self.result_tree.delete(*self.result_tree.get_children())
        self.detail_text.delete(1.0, tk.END)
        
        self.suggestion_text.config(state=tk.NORMAL)
        self.suggestion_text.delete(1.0, tk.END)
        self.suggestion_text.config(state=tk.DISABLED)
        
        self.edit_button.config(state=tk.DISABLED)
        self.confirm_button.config(state=tk.DISABLED)
        
        self.current_recognition_result = None


if __name__ == "__main__":
    # 测试GUI
    root = tk.Tk()
    root.title("OCR热量识别测试")
    root.geometry("800x600")
    
    # 模拟应用核心
    class MockAppCore:
        def __init__(self):
            self.config = type('Config', (), {})()
    
    app_core = MockAppCore()
    
    # 创建GUI
    ocr_gui = OCRCalorieGUI(root, app_core)
    
    root.mainloop()
