"""
API密钥统一管理
所有API密钥的集中管理和配置
"""

import os
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

logger = logging.getLogger(__name__)


@dataclass
class APIKeys:
    """API密钥配置类"""
    
    # 千问大模型API密钥
    qwen_api_key: Optional[str] = None
    
    # OpenAI API密钥
    openai_api_key: Optional[str] = None
    
    # Anthropic API密钥
    anthropic_api_key: Optional[str] = None
    
    # 其他API密钥（可扩展）
    google_api_key: Optional[str] = None
    baidu_api_key: Optional[str] = None
    tencent_api_key: Optional[str] = None


class APIKeyManager:
    """API密钥管理器"""
    
    def __init__(self):
        self.keys = APIKeys()
        self._load_from_env()
        self._validate_keys()
    
    def _load_from_env(self):
        """从环境变量加载API密钥"""
        # 千问API密钥
        self.keys.qwen_api_key = os.getenv('QWEN_API_KEY')
        
        # OpenAI API密钥
        self.keys.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Anthropic API密钥
        self.keys.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # 其他API密钥
        self.keys.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.keys.baidu_api_key = os.getenv('BAIDU_API_KEY')
        self.keys.tencent_api_key = os.getenv('TENCENT_API_KEY')
        
        logger.info("API密钥已从环境变量加载")
    
    def _validate_keys(self):
        """验证API密钥格式"""
        validation_results = {}
        
        # 验证千问API密钥
        if self.keys.qwen_api_key:
            if self.keys.qwen_api_key.startswith('sk-'):
                validation_results['qwen'] = True
                logger.info("✅ 千问API密钥格式正确")
            else:
                validation_results['qwen'] = False
                logger.warning("⚠️ 千问API密钥格式可能不正确")
        else:
            validation_results['qwen'] = False
            logger.warning("⚠️ 千问API密钥未配置")
        
        # 验证OpenAI API密钥
        if self.keys.openai_api_key:
            if self.keys.openai_api_key.startswith('sk-'):
                validation_results['openai'] = True
                logger.info("✅ OpenAI API密钥格式正确")
            else:
                validation_results['openai'] = False
                logger.warning("⚠️ OpenAI API密钥格式可能不正确")
        else:
            validation_results['openai'] = False
            logger.warning("⚠️ OpenAI API密钥未配置")
        
        # 验证Anthropic API密钥
        if self.keys.anthropic_api_key:
            if self.keys.anthropic_api_key.startswith('sk-ant-'):
                validation_results['anthropic'] = True
                logger.info("✅ Anthropic API密钥格式正确")
            else:
                validation_results['anthropic'] = False
                logger.warning("⚠️ Anthropic API密钥格式可能不正确")
        else:
            validation_results['anthropic'] = False
            logger.warning("⚠️ Anthropic API密钥未配置")
        
        return validation_results
    
    def get_qwen_key(self) -> Optional[str]:
        """获取千问API密钥"""
        return self.keys.qwen_api_key
    
    def get_openai_key(self) -> Optional[str]:
        """获取OpenAI API密钥"""
        return self.keys.openai_api_key
    
    def get_anthropic_key(self) -> Optional[str]:
        """获取Anthropic API密钥"""
        return self.keys.anthropic_api_key
    
    def get_key(self, provider: str) -> Optional[str]:
        """根据提供商获取API密钥"""
        key_map = {
            'qwen': self.keys.qwen_api_key,
            'openai': self.keys.openai_api_key,
            'anthropic': self.keys.anthropic_api_key,
            'google': self.keys.google_api_key,
            'baidu': self.keys.baidu_api_key,
            'tencent': self.keys.tencent_api_key
        }
        return key_map.get(provider.lower())
    
    def is_available(self, provider: str) -> bool:
        """检查指定提供商的API密钥是否可用"""
        key = self.get_key(provider)
        return key is not None and len(key.strip()) > 0
    
    def get_available_providers(self) -> list:
        """获取所有可用的API提供商"""
        providers = ['qwen', 'openai', 'anthropic', 'google', 'baidu', 'tencent']
        available = []
        
        for provider in providers:
            if self.is_available(provider):
                available.append(provider)
        
        return available
    
    def get_all_keys(self) -> Dict[str, Optional[str]]:
        """获取所有API密钥（用于调试，不包含实际密钥值）"""
        return {
            'qwen': '***' if self.keys.qwen_api_key else None,
            'openai': '***' if self.keys.openai_api_key else None,
            'anthropic': '***' if self.keys.anthropic_api_key else None,
            'google': '***' if self.keys.google_api_key else None,
            'baidu': '***' if self.keys.baidu_api_key else None,
            'tencent': '***' if self.keys.tencent_api_key else None
        }
    
    def set_key(self, provider: str, api_key: str):
        """设置API密钥（运行时设置）"""
        provider = provider.lower()
        
        if provider == 'qwen':
            self.keys.qwen_api_key = api_key
        elif provider == 'openai':
            self.keys.openai_api_key = api_key
        elif provider == 'anthropic':
            self.keys.anthropic_api_key = api_key
        elif provider == 'google':
            self.keys.google_api_key = api_key
        elif provider == 'baidu':
            self.keys.baidu_api_key = api_key
        elif provider == 'tencent':
            self.keys.tencent_api_key = api_key
        else:
            raise ValueError(f"不支持的API提供商: {provider}")
        
        logger.info(f"API密钥已设置: {provider}")
    
    def create_env_file(self, file_path: str = ".env"):
        """创建.env文件模板"""
        env_content = """# API密钥配置文件
# 请将下面的your-api-key-here替换为实际的API密钥

# 千问大模型API密钥
QWEN_API_KEY=your-qwen-api-key-here

# OpenAI API密钥（可选）
OPENAI_API_KEY=your-openai-api-key-here

# Anthropic API密钥（可选）
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Google API密钥（可选）
GOOGLE_API_KEY=your-google-api-key-here

# 百度API密钥（可选）
BAIDU_API_KEY=your-baidu-api-key-here

# 腾讯API密钥（可选）
TENCENT_API_KEY=your-tencent-api-key-here

# 其他配置
DEBUG=true
LOG_LEVEL=INFO
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        logger.info(f"环境变量文件已创建: {file_path}")
    
    def get_status_report(self) -> Dict[str, Any]:
        """获取API密钥状态报告"""
        available_providers = self.get_available_providers()
        
        return {
            "total_providers": 6,
            "available_providers": len(available_providers),
            "available_list": available_providers,
            "unavailable_providers": [p for p in ['qwen', 'openai', 'anthropic', 'google', 'baidu', 'tencent'] 
                                     if p not in available_providers],
            "recommendations": self._get_recommendations()
        }
    
    def _get_recommendations(self) -> list:
        """获取配置建议"""
        recommendations = []
        
        if not self.is_available('qwen'):
            recommendations.append("建议配置千问API密钥以获得最佳的中文AI分析体验")
        
        if not self.is_available('openai'):
            recommendations.append("可选配置OpenAI API密钥作为备用AI服务")
        
        if not self.is_available('anthropic'):
            recommendations.append("可选配置Anthropic API密钥作为备用AI服务")
        
        return recommendations


# 全局API密钥管理器实例
_api_key_manager: Optional[APIKeyManager] = None


def get_api_key_manager() -> APIKeyManager:
    """获取全局API密钥管理器实例"""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager


# 便捷函数
def get_qwen_key() -> Optional[str]:
    """获取千问API密钥"""
    return get_api_key_manager().get_qwen_key()


def get_openai_key() -> Optional[str]:
    """获取OpenAI API密钥"""
    return get_api_key_manager().get_openai_key()


def get_anthropic_key() -> Optional[str]:
    """获取Anthropic API密钥"""
    return get_api_key_manager().get_anthropic_key()


def get_api_key(provider: str) -> Optional[str]:
    """根据提供商获取API密钥"""
    return get_api_key_manager().get_key(provider)


def is_api_available(provider: str) -> bool:
    """检查指定提供商的API是否可用"""
    return get_api_key_manager().is_available(provider)


def get_available_providers() -> list:
    """获取所有可用的API提供商"""
    return get_api_key_manager().get_available_providers()


def create_env_template(file_path: str = ".env"):
    """创建环境变量文件模板"""
    return get_api_key_manager().create_env_file(file_path)


def get_api_status_report() -> Dict[str, Any]:
    """获取API状态报告"""
    return get_api_key_manager().get_status_report()


if __name__ == "__main__":
    # 测试API密钥管理
    print("=== API密钥管理测试 ===")
    
    manager = get_api_key_manager()
    
    # 显示状态报告
    status = manager.get_status_report()
    print(f"✅ 总提供商数量: {status['total_providers']}")
    print(f"✅ 可用提供商数量: {status['available_providers']}")
    print(f"✅ 可用提供商: {status['available_list']}")
    print(f"✅ 不可用提供商: {status['unavailable_providers']}")
    
    # 显示建议
    if status['recommendations']:
        print("\n💡 配置建议:")
        for rec in status['recommendations']:
            print(f"   - {rec}")
    
    # 创建环境变量文件模板
    manager.create_env_file()
    
    print("\n✅ API密钥管理测试完成")
