# API密钥配置指南

## 📋 概述

本项目已将所有API密钥统一管理到 `config/api_keys.py` 文件中，提供更安全、更便捷的密钥管理方式。

## 🔧 配置步骤

### 1. 创建环境变量文件

在项目根目录创建 `.env` 文件：

```bash
# 复制模板文件
cp .env.template .env
```

### 2. 配置API密钥

编辑 `.env` 文件，填入您的API密钥：

```env
# 千问大模型API密钥 (必需)
QWEN_API_KEY=sk-your-actual-qwen-api-key-here

# OpenAI API密钥 (可选)
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Anthropic API密钥 (可选)
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-api-key-here
```

### 3. 验证配置

运行以下命令验证API密钥配置：

```bash
python -c "from config.api_keys import get_api_status_report; print(get_api_status_report())"
```

## 🏗️ 架构说明

### 统一API密钥管理

- **文件位置**: `config/api_keys.py`
- **管理类**: `APIKeyManager`
- **全局实例**: 通过 `get_api_key_manager()` 获取

### 支持的API提供商

| 提供商 | 环境变量 | 必需性 | 用途 |
|--------|----------|--------|------|
| 千问 | `QWEN_API_KEY` | ✅ 必需 | 主要AI分析服务 |
| OpenAI | `OPENAI_API_KEY` | ⚪ 可选 | 备用AI服务 |
| Anthropic | `ANTHROPIC_API_KEY` | ⚪ 可选 | 备用AI服务 |
| Google | `GOOGLE_API_KEY` | ⚪ 可选 | 扩展服务 |
| 百度 | `BAIDU_API_KEY` | ⚪ 可选 | 扩展服务 |
| 腾讯 | `TENCENT_API_KEY` | ⚪ 可选 | 扩展服务 |

## 🔒 安全特性

### 1. 密钥验证
- 自动验证API密钥格式
- 检查密钥是否为空或无效
- 提供详细的验证报告

### 2. 环境隔离
- 所有密钥存储在环境变量中
- `.env` 文件被 `.gitignore` 忽略
- 不会意外提交到版本控制

### 3. 运行时管理
- 支持运行时动态设置密钥
- 提供密钥状态监控
- 支持多提供商切换

## 📚 使用方法

### 基本用法

```python
from config.api_keys import get_qwen_key, get_openai_key

# 获取千问API密钥
qwen_key = get_qwen_key()
if qwen_key:
    print("千问API密钥已配置")
else:
    print("千问API密钥未配置")

# 获取OpenAI API密钥
openai_key = get_openai_key()
```

### 高级用法

```python
from config.api_keys import get_api_key_manager

# 获取管理器实例
manager = get_api_key_manager()

# 检查提供商可用性
if manager.is_available('qwen'):
    print("千问服务可用")

# 获取所有可用提供商
available = manager.get_available_providers()
print(f"可用提供商: {available}")

# 获取状态报告
status = manager.get_status_report()
print(f"配置状态: {status}")
```

### 动态设置密钥

```python
from config.api_keys import get_api_key_manager

manager = get_api_key_manager()

# 运行时设置API密钥
manager.set_key('qwen', 'sk-your-new-api-key')
```

## 🛠️ 开发工具

### 创建环境变量模板

```python
from config.api_keys import create_env_template

# 创建 .env 文件模板
create_env_template()
```

### 获取配置建议

```python
from config.api_keys import get_api_status_report

status = get_api_status_report()
for recommendation in status['recommendations']:
    print(f"💡 {recommendation}")
```

## 🔍 故障排除

### 常见问题

1. **API密钥未配置**
   ```
   ValueError: 千问API密钥未配置，请在.env文件中设置QWEN_API_KEY
   ```
   **解决方案**: 检查 `.env` 文件是否存在且包含正确的API密钥

2. **密钥格式错误**
   ```
   ⚠️ 千问API密钥格式可能不正确
   ```
   **解决方案**: 确保API密钥以 `sk-` 开头（千问）或 `sk-ant-` 开头（Anthropic）

3. **环境变量未加载**
   ```
   ⚠️ 千问API密钥未配置
   ```
   **解决方案**: 确保 `.env` 文件在项目根目录，且格式正确

### 调试命令

```bash
# 检查环境变量
python -c "import os; print('QWEN_API_KEY:', os.getenv('QWEN_API_KEY', 'Not set'))"

# 测试API密钥管理
python config/api_keys.py

# 验证配置
python -c "from config.api_keys import get_api_status_report; import json; print(json.dumps(get_api_status_report(), indent=2, ensure_ascii=False))"
```

## 📈 最佳实践

1. **密钥安全**
   - 永远不要将API密钥硬编码在代码中
   - 使用环境变量或配置文件
   - 定期轮换API密钥

2. **错误处理**
   - 始终检查API密钥是否可用
   - 提供友好的错误提示
   - 实现降级策略

3. **配置管理**
   - 使用统一的配置管理
   - 提供配置验证
   - 支持多环境配置

## 🔄 迁移指南

如果您之前在其他文件中硬编码了API密钥，请按以下步骤迁移：

1. **移除硬编码密钥**
   ```python
   # 旧方式 ❌
   api_key = "sk-hardcoded-key"
   
   # 新方式 ✅
   from config.api_keys import get_qwen_key
   api_key = get_qwen_key()
   ```

2. **更新导入语句**
   ```python
   # 添加统一导入
   from config.api_keys import get_qwen_key, get_openai_key, get_anthropic_key
   ```

3. **添加错误处理**
   ```python
   api_key = get_qwen_key()
   if not api_key:
       raise ValueError("千问API密钥未配置")
   ```

## 📞 支持

如果您在配置API密钥时遇到问题，请：

1. 检查本指南的故障排除部分
2. 运行调试命令验证配置
3. 查看项目日志获取详细错误信息
4. 提交Issue描述具体问题

---

**注意**: 请妥善保管您的API密钥，不要分享给他人或提交到公开仓库。
