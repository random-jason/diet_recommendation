"""
启动脚本 - 个性化饮食推荐助手
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        ('customtkinter', 'customtkinter'),
        ('openai', 'openai'),
        ('anthropic', 'anthropic'),
        ('sklearn', 'scikit-learn'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('dotenv', 'python-dotenv')
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_config():
    """检查配置文件"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  配置文件 .env 不存在")
        print("正在创建示例配置文件...")
        
        env_content = """# 个性化饮食推荐助手配置文件

# 数据库配置
DATABASE_URL=sqlite:///./data/app.db

# 大模型API配置 (可选，不配置将使用备用方案)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# 模型配置
MODEL_SAVE_PATH=./models/
TRAINING_DATA_PATH=./data/training/
USER_DATA_PATH=./data/users/

# 推荐系统配置
RECOMMENDATION_TOP_K=5
MIN_TRAINING_SAMPLES=10
MODEL_RETRAIN_THRESHOLD=50

# 用户画像配置
ENABLE_PHYSIOLOGICAL_TRACKING=true
ENABLE_ASTROLOGY_FACTORS=true
ENABLE_TASTE_PREFERENCES=true

# GUI配置
APP_TITLE=个性化饮食推荐助手
WINDOW_SIZE=1200x800
THEME=dark

# 开发配置
DEBUG=true
LOG_LEVEL=INFO
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ 示例配置文件已创建: .env")
        print("💡 提示: 如需使用大模型功能，请在 .env 文件中配置API密钥")
    else:
        print("✅ 配置文件存在")
    
    return True

def create_directories():
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
    
    print("✅ 目录结构创建完成")

def main():
    """主函数"""
    print("🍎 个性化饮食推荐助手 - 启动检查")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 检查配置
    if not check_config():
        return False
    
    # 创建目录
    create_directories()
    
    print("\n🚀 启动应用...")
    print("=" * 50)
    
    try:
        # 导入并运行主应用
        from main import main as run_app
        run_app()
    except KeyboardInterrupt:
        print("\n👋 用户中断，应用退出")
    except Exception as e:
        print(f"\n❌ 应用启动失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
