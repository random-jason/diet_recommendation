"""
主应用入口 - 个性化饮食推荐助手
基于基座架构的完整应用
"""

import sys
import os
from pathlib import Path
from typing import Optional
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.base import BaseConfig, AppCore, ModuleManager, ModuleType, initialize_app, cleanup_app
from modules.data_collection import DataCollectionModule
from modules.ai_analysis import AIAnalysisModule
from modules.recommendation_engine import RecommendationEngine
from modules.ocr_calorie_recognition import OCRCalorieRecognitionModule
from gui.main_window import MainWindow
import tkinter as tk
from tkinter import messagebox

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class DietRecommendationApp:
    """饮食推荐应用主类"""
    
    def __init__(self):
        self.config = self._load_config()
        self.app_core: Optional[AppCore] = None
        self.main_window: Optional[MainWindow] = None
        self.is_running = False
    
    def _load_config(self) -> BaseConfig:
        """加载配置"""
        config = BaseConfig()
        
        # 从环境变量加载API密钥
        config.qwen_api_key = os.getenv('QWEN_API_KEY')
        
        # 从.env文件加载配置
        env_file = Path('.env')
        if env_file.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv()
                config.qwen_api_key = os.getenv('QWEN_API_KEY')
            except Exception:
                # 如果.env文件有编码问题，跳过加载
                pass
        
        return config
    
    def initialize(self) -> bool:
        """初始化应用"""
        try:
            logger.info("正在初始化饮食推荐应用...")
            
            # 创建必要的目录
            self._create_directories()
            
            # 初始化应用核心
            if not initialize_app(self.config):
                logger.error("应用核心初始化失败")
                return False
            
            self.app_core = AppCore(self.config)
            
            # 注册所有模块
            if not self._register_modules():
                logger.error("模块注册失败")
                return False
            
            # 启动应用核心
            if not self.app_core.start():
                logger.error("应用核心启动失败")
                return False
            
            self.is_running = True
            logger.info("饮食推荐应用初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"应用初始化失败: {e}")
            return False
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            'data',
            'data/users',
            'data/training',
            'models',
            'logs',
            'gui'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _register_modules(self) -> bool:
        """注册所有模块"""
        try:
            module_manager = ModuleManager(self.config)
            
            # 注册数据采集模块
            data_collection_module = DataCollectionModule(self.config)
            if not module_manager.register_module(data_collection_module):
                logger.error("数据采集模块注册失败")
                return False
            
            # 注册AI分析模块
            ai_analysis_module = AIAnalysisModule(self.config)
            if not module_manager.register_module(ai_analysis_module):
                logger.error("AI分析模块注册失败")
                return False
            
            # 注册推荐引擎模块
            recommendation_module = RecommendationEngine(self.config)
            if not module_manager.register_module(recommendation_module):
                logger.error("推荐引擎模块注册失败")
                return False
            
            # 注册OCR热量识别模块
            ocr_module = OCRCalorieRecognitionModule(self.config)
            if not module_manager.register_module(ocr_module):
                logger.error("OCR热量识别模块注册失败")
                return False
            
            # 初始化模块管理器
            if not module_manager.initialize_all():
                logger.error("模块管理器初始化失败")
                return False
            
            # 将模块管理器设置到应用核心
            self.app_core.module_manager = module_manager
            logger.info("所有模块注册成功")
            return True
            
        except Exception as e:
            logger.error(f"模块注册失败: {e}")
            return False
    
    def run_gui(self):
        """运行GUI界面"""
        try:
            logger.info("启动移动端GUI界面...")
            
            # 使用移动端界面，传递应用核心
            from gui.mobile_main_window import MobileMainWindow
            self.main_window = MobileMainWindow(self.app_core)
            
            # 启动GUI主循环
            self.main_window.run()
            
        except Exception as e:
            logger.error(f"GUI启动失败: {e}")
            messagebox.showerror("错误", f"GUI启动失败: {str(e)}")
    
    def _on_closing(self):
        """窗口关闭事件处理"""
        try:
            if messagebox.askokcancel("退出", "确定要退出应用吗？"):
                self.shutdown()
        except Exception as e:
            logger.error(f"关闭应用失败: {e}")
            sys.exit(1)
    
    def shutdown(self):
        """关闭应用"""
        try:
            logger.info("正在关闭应用...")
            
            # 关闭GUI
            if self.main_window:
                self.main_window.destroy()
            
            # 关闭应用核心
            if self.app_core:
                self.app_core.stop()
            
            # 清理资源
            cleanup_app()
            
            self.is_running = False
            logger.info("应用关闭完成")
            
        except Exception as e:
            logger.error(f"应用关闭失败: {e}")
        finally:
            sys.exit(0)
    
    def get_app_status(self) -> dict:
        """获取应用状态"""
        if not self.app_core:
            return {"status": "not_initialized"}
        
        module_status = self.app_core.module_manager.get_module_status()
        
        return {
            "status": "running" if self.is_running else "stopped",
            "modules": module_status,
            "config": {
                "app_name": self.config.app_name,
                "version": self.config.version,
                "debug": self.config.debug
            }
        }


def main():
    """主函数"""
    try:
        # 创建应用实例
        app = DietRecommendationApp()
        
        # 初始化应用
        if not app.initialize():
            logger.error("应用初始化失败，退出")
            sys.exit(1)
        
        # 运行GUI
        app.run_gui()
        
    except KeyboardInterrupt:
        logger.info("用户中断，正在退出...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"应用运行失败: {e}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
