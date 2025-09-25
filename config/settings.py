"""
统一配置管理 - 所有接口、配置、SQL入口的集中管理
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

# 尝试加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # 如果没有.env文件或加载失败，使用默认配置
    pass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """数据库配置"""
    # 数据库路径
    database_path: str = "data/app.db"
    database_url: str = "sqlite:///./data/app.db"
    
    # 数据库连接参数
    connection_timeout: int = 30
    check_same_thread: bool = False
    
    # 表配置
    enable_foreign_keys: bool = True
    enable_wal_mode: bool = True


@dataclass
class APIConfig:
    """API接口配置"""
    # 千问大模型配置
    qwen_api_key: Optional[str] = None
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-plus-latest"
    qwen_temperature: float = 0.7
    qwen_max_tokens: int = 2000
    
    # OpenAI配置（备用）
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    
    # Anthropic配置（备用）
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # API超时配置
    api_timeout: int = 30
    api_retry_count: int = 3


@dataclass
class AppConfig:
    """应用配置"""
    # 应用基本信息
    app_name: str = "个性化饮食推荐助手"
    version: str = "1.0.0"
    debug: bool = True
    
    # 路径配置
    model_path: str = "models/"
    log_path: str = "logs/"
    data_path: str = "data/"
    user_data_path: str = "data/users/"
    training_data_path: str = "data/training/"
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "logs/app.log"


@dataclass
class MLConfig:
    """机器学习配置"""
    # 推荐系统配置
    max_recommendations: int = 5
    min_training_samples: int = 10
    model_update_threshold: int = 50
    
    # 模型配置
    model_save_format: str = "joblib"
    enable_model_caching: bool = True
    model_cache_size: int = 100
    
    # 特征工程配置
    tfidf_max_features: int = 1000
    tfidf_ngram_range: tuple = (1, 2)
    similarity_threshold: float = 0.7


@dataclass
class OCRConfig:
    """OCR识别配置"""
    # OCR引擎配置
    enable_tesseract: bool = True
    enable_paddleocr: bool = True
    enable_easyocr: bool = True
    
    # 识别参数
    min_confidence: float = 0.6
    max_processing_time: float = 30.0
    
    # 图片处理配置
    image_max_size: tuple = (1920, 1080)
    image_quality: int = 95
    enable_image_preprocessing: bool = True


@dataclass
class UIConfig:
    """界面配置"""
    # 移动端界面配置
    mobile_width: int = 375
    mobile_height: int = 812
    
    # 主题配置
    theme_mode: str = "light"  # light, dark, system
    color_theme: str = "blue"
    
    # 圆角配置
    corner_radius_small: int = 8
    corner_radius_medium: int = 12
    corner_radius_large: int = 15
    corner_radius_xlarge: int = 20
    corner_radius_xxlarge: int = 25


class UnifiedConfig:
    """统一配置管理类"""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.api = APIConfig()
        self.app = AppConfig()
        self.ml = MLConfig()
        self.ocr = OCRConfig()
        self.ui = UIConfig()
        
        # 从环境变量加载配置
        self._load_from_env()
        
        # 创建必要目录
        self._create_directories()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        # 数据库配置
        if os.getenv('DATABASE_PATH'):
            self.database.database_path = os.getenv('DATABASE_PATH')
        
        # API配置 - 使用统一API密钥管理
        from config.api_keys import get_api_key_manager
        api_manager = get_api_key_manager()
        
        self.api.qwen_api_key = api_manager.get_qwen_key()
        self.api.qwen_base_url = os.getenv('QWEN_BASE_URL', self.api.qwen_base_url)
        self.api.qwen_model = os.getenv('QWEN_MODEL', self.api.qwen_model)
        
        self.api.openai_api_key = api_manager.get_openai_key()
        self.api.anthropic_api_key = api_manager.get_anthropic_key()
        
        # 应用配置
        if os.getenv('DEBUG'):
            self.app.debug = os.getenv('DEBUG').lower() == 'true'
        
        if os.getenv('LOG_LEVEL'):
            self.app.log_level = os.getenv('LOG_LEVEL')
        
        # ML配置
        if os.getenv('MAX_RECOMMENDATIONS'):
            self.ml.max_recommendations = int(os.getenv('MAX_RECOMMENDATIONS'))
        
        if os.getenv('MIN_TRAINING_SAMPLES'):
            self.ml.min_training_samples = int(os.getenv('MIN_TRAINING_SAMPLES'))
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            self.app.data_path,
            self.app.user_data_path,
            self.app.training_data_path,
            self.app.model_path,
            self.app.log_path,
            Path(self.database.database_path).parent
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get_database_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        try:
            conn = sqlite3.connect(
                self.database.database_path,
                timeout=self.database.connection_timeout,
                check_same_thread=self.database.check_same_thread
            )
            
            # 启用外键约束
            if self.database.enable_foreign_keys:
                conn.execute("PRAGMA foreign_keys = ON")
            
            # 启用WAL模式
            if self.database.enable_wal_mode:
                conn.execute("PRAGMA journal_mode = WAL")
            
            return conn
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def get_api_config(self, provider: str = "qwen") -> Dict[str, Any]:
        """获取API配置"""
        if provider == "qwen":
            return {
                "api_key": self.api.qwen_api_key,
                "base_url": self.api.qwen_base_url,
                "model": self.api.qwen_model,
                "temperature": self.api.qwen_temperature,
                "max_tokens": self.api.qwen_max_tokens,
                "timeout": self.api.api_timeout,
                "retry_count": self.api.api_retry_count
            }
        elif provider == "openai":
            return {
                "api_key": self.api.openai_api_key,
                "model": self.api.openai_model,
                "timeout": self.api.api_timeout,
                "retry_count": self.api.api_retry_count
            }
        elif provider == "anthropic":
            return {
                "api_key": self.api.anthropic_api_key,
                "model": self.api.anthropic_model,
                "timeout": self.api.api_timeout,
                "retry_count": self.api.api_retry_count
            }
        else:
            raise ValueError(f"不支持的API提供商: {provider}")
    
    def is_api_available(self, provider: str = "qwen") -> bool:
        """检查API是否可用"""
        if provider == "qwen":
            return self.api.qwen_api_key is not None
        elif provider == "openai":
            return self.api.openai_api_key is not None
        elif provider == "anthropic":
            return self.api.anthropic_api_key is not None
        else:
            return False
    
    def get_ocr_config(self) -> Dict[str, Any]:
        """获取OCR配置"""
        return {
            "enable_tesseract": self.ocr.enable_tesseract,
            "enable_paddleocr": self.ocr.enable_paddleocr,
            "enable_easyocr": self.ocr.enable_easyocr,
            "min_confidence": self.ocr.min_confidence,
            "max_processing_time": self.ocr.max_processing_time,
            "image_max_size": self.ocr.image_max_size,
            "image_quality": self.ocr.image_quality,
            "enable_preprocessing": self.ocr.enable_image_preprocessing
        }
    
    def get_ui_config(self) -> Dict[str, Any]:
        """获取界面配置"""
        return {
            "mobile_width": self.ui.mobile_width,
            "mobile_height": self.ui.mobile_height,
            "theme_mode": self.ui.theme_mode,
            "color_theme": self.ui.color_theme,
            "corner_radius": {
                "small": self.ui.corner_radius_small,
                "medium": self.ui.corner_radius_medium,
                "large": self.ui.corner_radius_large,
                "xlarge": self.ui.corner_radius_xlarge,
                "xxlarge": self.ui.corner_radius_xxlarge
            }
        }
    
    def validate_config(self) -> bool:
        """验证配置有效性"""
        try:
            # 检查数据库路径
            db_path = Path(self.database.database_path)
            if not db_path.parent.exists():
                db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 检查API配置
            if not self.is_api_available("qwen"):
                logger.warning("千问API密钥未配置，部分功能可能不可用")
            
            # 检查目录权限
            for directory in [self.app.data_path, self.app.model_path, self.app.log_path]:
                if not Path(directory).exists():
                    Path(directory).mkdir(parents=True, exist_ok=True)
            
            logger.info("配置验证通过")
            return True
            
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            return False
    
    def save_config_to_file(self, file_path: str = "config/app_config.json"):
        """保存配置到文件"""
        import json
        
        config_dict = {
            "database": self.database.__dict__,
            "api": self.api.__dict__,
            "app": self.app.__dict__,
            "ml": self.ml.__dict__,
            "ocr": self.ocr.__dict__,
            "ui": self.ui.__dict__
        }
        
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"配置已保存到: {file_path}")
    
    def load_config_from_file(self, file_path: str = "config/app_config.json"):
        """从文件加载配置"""
        import json
        
        if not Path(file_path).exists():
            logger.warning(f"配置文件不存在: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # 更新配置
            if "database" in config_dict:
                for key, value in config_dict["database"].items():
                    if hasattr(self.database, key):
                        setattr(self.database, key, value)
            
            if "api" in config_dict:
                for key, value in config_dict["api"].items():
                    if hasattr(self.api, key):
                        setattr(self.api, key, value)
            
            # 其他配置类似处理...
            
            logger.info(f"配置已从文件加载: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return False


# 全局配置实例
_config_instance: Optional[UnifiedConfig] = None


def get_config() -> UnifiedConfig:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = UnifiedConfig()
        _config_instance.validate_config()
    return _config_instance


def reload_config():
    """重新加载配置"""
    global _config_instance
    _config_instance = None
    return get_config()


# 便捷函数
def get_database_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    return get_config().get_database_connection()


def get_api_config(provider: str = "qwen") -> Dict[str, Any]:
    """获取API配置"""
    return get_config().get_api_config(provider)


def is_api_available(provider: str = "qwen") -> bool:
    """检查API是否可用"""
    return get_config().is_api_available(provider)


if __name__ == "__main__":
    # 测试配置系统
    print("=== 统一配置管理测试 ===")
    
    config = get_config()
    
    print(f"✅ 应用名称: {config.app.app_name}")
    print(f"✅ 数据库路径: {config.database.database_path}")
    print(f"✅ 千问API可用: {config.is_api_available('qwen')}")
    print(f"✅ OpenAI API可用: {config.is_api_available('openai')}")
    
    # 测试数据库连接
    try:
        conn = config.get_database_connection()
        print("✅ 数据库连接成功")
        conn.close()
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
    
    # 保存配置
    config.save_config_to_file()
    
    print("✅ 配置系统测试完成")
