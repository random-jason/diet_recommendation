"""
核心基座架构 - Diet Recommendation App
统一的基座设计，支持所有功能模块的扩展
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
import json
import sqlite3
import logging
from datetime import datetime, date
from pathlib import Path
import asyncio
from enum import Enum
import threading
from queue import Queue
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # 如果没有.env文件或加载失败，使用默认配置
    pass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModuleType(Enum):
    """模块类型枚举"""
    DATA_COLLECTION = "data_collection"
    USER_ANALYSIS = "user_analysis"
    RECOMMENDATION = "recommendation"
    GUI_INTERFACE = "gui_interface"
    NOTIFICATION = "notification"


@dataclass
class BaseConfig:
    """基础配置类"""
    app_name: str = "个性化饮食推荐助手"
    version: str = "1.0.0"
    debug: bool = True
    database_path: str = "data/app.db"
    model_path: str = "models/"
    log_level: str = "INFO"
    
    # API配置
    qwen_api_key: Optional[str] = None
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-plus-latest"
    
    # 用户配置
    max_recommendations: int = 5
    min_training_samples: int = 10
    model_update_threshold: int = 50


@dataclass
class UserData:
    """统一用户数据结构"""
    user_id: str
    profile: Dict[str, Any] = field(default_factory=dict)
    meals: List[Dict[str, Any]] = field(default_factory=list)
    feedback: List[Dict[str, Any]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AnalysisResult:
    """统一分析结果结构"""
    module_type: ModuleType
    user_id: str
    input_data: Any
    result: Dict[str, Any]
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseModule(ABC):
    """基础模块抽象类"""
    
    def __init__(self, config: BaseConfig, module_type: ModuleType):
        self.config = config
        self.module_type = module_type
        self.is_initialized = False
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化模块"""
        pass
    
    @abstractmethod
    def process(self, input_data: Any, user_data: UserData) -> AnalysisResult:
        """处理数据"""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """清理资源"""
        pass
    
    def is_ready(self) -> bool:
        """检查模块是否就绪"""
        return self.is_initialized


class DataManager:
    """数据管理基座"""
    
    def __init__(self, config: BaseConfig):
        self.config = config
        self.db_path = Path(config.database_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 分析结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                module_type TEXT,
                input_data TEXT,
                result TEXT,
                confidence REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 系统配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_user_data(self, user_data: UserData) -> bool:
        """保存用户数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (user_data.user_id, json.dumps(user_data.__dict__)))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"保存用户数据失败: {e}")
            return False
    
    def get_user_data(self, user_id: str) -> Optional[UserData]:
        """获取用户数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取用户基本信息
            cursor.execute('SELECT data FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return None
            
            # 解析用户基本信息
            data_dict = json.loads(result[0])
            
            # 获取餐食记录
            cursor.execute('''
                SELECT date, meal_type, foods, quantities, calories, satisfaction_score, food_items
                FROM meal_records 
                WHERE user_id = ? 
                ORDER BY date DESC
            ''', (user_id,))
            
            meal_rows = cursor.fetchall()
            meals = []
            for row in meal_rows:
                meal = {
                    'date': row[0],
                    'meal_type': row[1],
                    'foods': json.loads(row[2]) if row[2] else [],
                    'quantities': json.loads(row[3]) if row[3] else [],
                    'calories': row[4],
                    'satisfaction_score': row[5],
                    'food_items': json.loads(row[6]) if row[6] else []
                }
                meals.append(meal)
            
            # 获取反馈记录
            cursor.execute('''
                SELECT date, recommended_foods, user_choice, feedback_type
                FROM feedback_records 
                WHERE user_id = ? 
                ORDER BY date DESC
            ''', (user_id,))
            
            feedback_rows = cursor.fetchall()
            feedback = []
            for row in feedback_rows:
                fb = {
                    'date': row[0],
                    'recommended_foods': json.loads(row[1]) if row[1] else [],
                    'user_choice': row[2],
                    'feedback_type': row[3]
                }
                feedback.append(fb)
            
            # 获取问卷数据
            cursor.execute('''
                SELECT questionnaire_type, answers
                FROM questionnaire_records 
                WHERE user_id = ?
            ''', (user_id,))
            
            questionnaire_rows = cursor.fetchall()
            preferences = {}
            for row in questionnaire_rows:
                preferences[row[0]] = json.loads(row[1]) if row[1] else {}
            
            conn.close()
            
            # 构建完整的用户数据
            user_data = UserData(
                user_id=data_dict['user_id'],
                profile=data_dict.get('profile', {}),
                meals=meals,
                feedback=feedback,
                preferences=preferences,
                created_at=data_dict.get('created_at', ''),
                updated_at=data_dict.get('updated_at', '')
            )
            
            return user_data
            
        except Exception as e:
            logger.error(f"获取用户数据失败: {e}")
            return None
    
    def save_analysis_result(self, result: AnalysisResult) -> bool:
        """保存分析结果"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analysis_results 
                (user_id, module_type, input_data, result, confidence, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                result.user_id,
                result.module_type.value,
                json.dumps(result.input_data),
                json.dumps(result.result),
                result.confidence,
                json.dumps(result.metadata)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"保存分析结果失败: {e}")
            return False
    
    def get_analysis_history(self, user_id: str, module_type: Optional[ModuleType] = None, 
                           limit: int = 10) -> List[AnalysisResult]:
        """获取分析历史"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if module_type:
                cursor.execute('''
                    SELECT module_type, input_data, result, confidence, timestamp, metadata
                    FROM analysis_results 
                    WHERE user_id = ? AND module_type = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_id, module_type.value, limit))
            else:
                cursor.execute('''
                    SELECT module_type, input_data, result, confidence, timestamp, metadata
                    FROM analysis_results 
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            analysis_results = []
            for row in results:
                result = AnalysisResult(
                    module_type=ModuleType(row[0]),
                    user_id=user_id,
                    input_data=json.loads(row[1]),
                    result=json.loads(row[2]),
                    confidence=row[3],
                    timestamp=row[4],
                    metadata=json.loads(row[5])
                )
                analysis_results.append(result)
            
            return analysis_results
        except Exception as e:
            logger.error(f"获取分析历史失败: {e}")
            return []


class EventBus:
    """事件总线基座"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_queue = Queue()
        self.is_running = False
        self.worker_thread = None
    
    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """取消订阅"""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
    
    def publish(self, event_type: str, data: Any):
        """发布事件"""
        self.event_queue.put((event_type, data))
    
    def start(self):
        """启动事件总线"""
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._process_events)
        self.worker_thread.start()
    
    def stop(self):
        """停止事件总线"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join()
    
    def _process_events(self):
        """处理事件"""
        while self.is_running:
            try:
                event_type, data = self.event_queue.get(timeout=1)
                
                if event_type in self.subscribers:
                    for callback in self.subscribers[event_type]:
                        try:
                            callback(data)
                        except Exception as e:
                            logger.error(f"事件处理失败: {e}")
                
                self.event_queue.task_done()
            except:
                continue


class ModuleManager:
    """模块管理器基座"""
    
    def __init__(self, config: BaseConfig):
        self.config = config
        self.modules: Dict[ModuleType, BaseModule] = {}
        self.data_manager = DataManager(config)
        self.event_bus = EventBus()
        self.is_initialized = False
    
    def register_module(self, module: BaseModule) -> bool:
        """注册模块"""
        try:
            # 检查模块是否已经注册
            if module.module_type in self.modules:
                logger.warning(f"模块 {module.module_type.value} 已经注册，跳过重复注册")
                return True
            
            if module.initialize():
                self.modules[module.module_type] = module
                logger.info(f"模块 {module.module_type.value} 注册成功")
                return True
            else:
                logger.error(f"模块 {module.module_type.value} 初始化失败")
                return False
        except Exception as e:
            logger.error(f"注册模块失败: {e}")
            return False
    
    def process_request(self, module_type: ModuleType, input_data: Any, 
                       user_id: str) -> Optional[AnalysisResult]:
        """处理请求"""
        if module_type not in self.modules:
            logger.error(f"模块 {module_type.value} 未注册")
            return None
        
        module = self.modules[module_type]
        if not module.is_ready():
            logger.error(f"模块 {module_type.value} 未就绪")
            return None
        
        # 获取用户数据
        user_data = self.data_manager.get_user_data(user_id)
        if not user_data:
            logger.error(f"用户 {user_id} 数据不存在")
            return None
        
        try:
            # 处理请求
            result = module.process(input_data, user_data)
            
            # 保存结果
            self.data_manager.save_analysis_result(result)
            
            # 发布事件
            self.event_bus.publish(f"{module_type.value}_completed", result)
            
            return result
        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return None
    
    def get_module_status(self) -> Dict[str, bool]:
        """获取模块状态"""
        return {module_type.value: module.is_ready() 
                for module_type, module in self.modules.items()}
    
    def initialize_all(self) -> bool:
        """初始化所有模块"""
        try:
            self.event_bus.start()
            self.is_initialized = True
            logger.info("模块管理器初始化完成")
            return True
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            return False
    
    def cleanup_all(self) -> bool:
        """清理所有模块"""
        try:
            self.event_bus.stop()
            
            for module in self.modules.values():
                module.cleanup()
            
            self.is_initialized = False
            logger.info("模块管理器清理完成")
            return True
        except Exception as e:
            logger.error(f"清理失败: {e}")
            return False


class AppCore:
    """应用核心基座"""
    
    def __init__(self, config: BaseConfig):
        self.config = config
        self.module_manager = ModuleManager(config)
        self.data_manager = DataManager(config)
        self.is_running = False
    
    def start(self) -> bool:
        """启动应用"""
        try:
            if self.module_manager.initialize_all():
                self.is_running = True
                logger.info("应用启动成功")
                return True
            else:
                logger.error("应用启动失败")
                return False
        except Exception as e:
            logger.error(f"启动应用失败: {e}")
            return False
    
    def stop(self) -> bool:
        """停止应用"""
        try:
            if self.module_manager.cleanup_all():
                self.is_running = False
                logger.info("应用停止成功")
                return True
            else:
                logger.error("应用停止失败")
                return False
        except Exception as e:
            logger.error(f"停止应用失败: {e}")
            return False
    
    def create_user(self, user_id: str, initial_data: Dict[str, Any]) -> bool:
        """创建用户"""
        user_data = UserData(
            user_id=user_id,
            profile=initial_data.get('profile', {}),
            preferences=initial_data.get('preferences', {})
        )
        return self.module_manager.data_manager.save_user_data(user_data)
    
    def process_user_request(self, module_type: ModuleType, input_data: Any, 
                           user_id: str) -> Optional[AnalysisResult]:
        """处理用户请求"""
        return self.module_manager.process_request(module_type, input_data, user_id)
    
    def get_user_data(self, user_id: str) -> Optional[UserData]:
        """获取用户数据"""
        return self.module_manager.data_manager.get_user_data(user_id)
    
    def get_analysis_history(self, user_id: str, module_type: Optional[ModuleType] = None) -> List[AnalysisResult]:
        """获取分析历史"""
        return self.module_manager.data_manager.get_analysis_history(user_id, module_type)


# 全局应用实例
app_core: Optional[AppCore] = None


def get_app_core() -> AppCore:
    """获取应用核心实例"""
    global app_core
    if app_core is None:
        config = BaseConfig()
        app_core = AppCore(config)
    return app_core


def initialize_app(config: Optional[BaseConfig] = None) -> bool:
    """初始化应用"""
    global app_core
    if config is None:
        config = BaseConfig()
    
    app_core = AppCore(config)
    return app_core.start()


def cleanup_app() -> bool:
    """清理应用"""
    global app_core
    if app_core:
        return app_core.stop()
    return True


if __name__ == "__main__":
    # 测试基座架构
    print("测试核心基座架构...")
    
    # 初始化应用
    if initialize_app():
        print("✅ 应用初始化成功")
        
        # 创建测试用户
        test_user_id = "test_user_001"
        initial_data = {
            "profile": {
                "name": "测试用户",
                "age": 25,
                "gender": "女"
            },
            "preferences": {
                "taste": "sweet",
                "diet": "balanced"
            }
        }
        
        app = get_app_core()
        if app.create_user(test_user_id, initial_data):
            print("✅ 用户创建成功")
            
            # 获取用户数据
            user_data = app.get_user_data(test_user_id)
            if user_data:
                print(f"✅ 用户数据获取成功: {user_data.user_id}")
        
        # 清理应用
        cleanup_app()
        print("✅ 应用清理完成")
    else:
        print("❌ 应用初始化失败")
    
    print("基座架构测试完成！")
