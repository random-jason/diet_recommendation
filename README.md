# 🍽️ 个性化饮食推荐APP

一个基于机器学习和OCR技术的智能饮食推荐系统，具有现代化的移动端界面和强大的AI分析能力。

## ✨ 最新特性

### 📷 OCR热量识别
- **多引擎OCR支持**：Tesseract、PaddleOCR、EasyOCR
- **智能图片识别**：自动识别食物名称和热量信息
- **多级验证机制**：OCR结果 + 数据库匹配 + 用户确认
- **学习优化系统**：从用户修正中持续学习改进
- **一键记录**：拍照即可完成餐食记录

### 🎨 现代化界面设计
- **圆角设计系统**：统一的圆角主题，减少方形元素
- **多色主题支持**：主色、次色、强调色等多种配色
- **移动端适配**：专为手机屏幕优化的界面布局
- **卡片式设计**：清晰的信息层次和视觉反馈
- **响应式交互**：悬停效果和状态变化

## 🎯 核心功能

### 1. 智能数据采集
- **OCR图片识别**：📷 拍照识别食物热量信息
- **5天三餐数据记录**：详细记录早中晚三餐的饮食内容
- **用户偏好问卷**：口味偏好、饮食习惯、过敏信息等
- **生理周期跟踪**：针对女性的生理期、排卵期等特殊时期
- **个性化因素**：星座、性格特征等参考因素

### 2. 机器学习推荐引擎
- **个人饮食模型训练**：基于用户历史数据训练个性化模型
- **持续学习机制**：根据用户反馈不断优化推荐
- **偏好矫正**：用户不喜欢或已食用食物的反馈学习
- **多因素融合**：结合生理周期、星座等多维度因素

### 3. AI大模型分析
- **千问大模型集成**：智能营养分析和建议生成
- **热量分析**：每日饮食热量计算和评估
- **营养建议**：基于大模型的智能营养建议
- **个性化指导**：结合用户特征的定制化建议

### 4. 现代化应用界面
- **移动端设计**：模拟小程序/安卓App的界面体验
- **圆角美化**：统一的圆角设计语言
- **多色主题**：丰富的颜色搭配和视觉层次
- **实时推荐**：动态推荐系统
- **数据可视化**：饮食趋势、营养分析图表

## 🏗️ 技术架构

### 核心基座
- **统一基座架构**：模块化设计，支持功能扩展
- **SQLite数据库**：轻量级本地数据存储
- **事件总线系统**：模块间通信和事件处理
- **数据管理器**：统一的数据访问接口

### OCR识别技术
- **Tesseract OCR**：开源OCR引擎，支持中英文
- **PaddleOCR**：百度开源OCR，中文识别优秀
- **EasyOCR**：简单易用的多语言OCR库
- **OpenCV**：图像预处理和增强
- **PIL/Pillow**：图像处理和格式转换

### 机器学习
- **scikit-learn**：推荐算法实现
- **pandas/numpy**：数据处理和分析
- **joblib**：模型序列化和加载
- **TF-IDF向量化**：文本特征提取

### AI大模型集成
- **千问大模型**：阿里云通义千问API
- **智能分析**：用户意图分析和营养建议
- **个性化推理**：基于用户特征的智能推荐

### 现代化界面
- **CustomTkinter**：现代化Python GUI框架
- **移动端设计**：375x812像素，模拟手机界面
- **圆角美化系统**：统一的视觉设计语言
- **多色主题**：丰富的颜色配置系统

## 📁 项目结构

```
diet_recommendation_app/
├── core/                    # 核心基座架构
│   ├── base.py             # 基础类和配置
│   └── base_engine.py      # 基础引擎抽象类
├── modules/                # 功能模块
│   ├── data_collection.py  # 数据采集模块
│   ├── ai_analysis.py      # AI分析模块
│   ├── recommendation_engine.py # 推荐引擎模块
│   └── ocr_calorie_recognition.py # OCR热量识别模块
├── gui/                    # 现代化界面
│   ├── mobile_main_window.py # 移动端主界面
│   ├── ocr_calorie_gui.py  # OCR识别界面
│   ├── styles.py           # 样式配置系统
│   └── main_window.py      # 桌面端界面
├── llm_integration/        # 大模型集成
│   └── qwen_client.py      # 千问大模型客户端
├── smart_food/             # 智能食物数据库
│   └── smart_database.py   # 食物数据库管理
├── data/                   # 数据存储
│   ├── users/              # 用户数据
│   ├── training/           # 训练数据
│   └── app.db              # SQLite数据库
├── models/                 # 机器学习模型
├── logs/                   # 日志文件
├── main.py                 # 应用入口
├── requirements.txt        # 依赖包列表
├── OCR_USAGE_GUIDE.md      # OCR使用指南
├── UI_BEAUTIFICATION_SUMMARY.md # 界面美化总结
└── README.md               # 项目说明文档
```

## 🚀 快速开始

### 1. 环境要求
- Python 3.8+
- Windows/macOS/Linux

### 2. 安装依赖
```bash
# 克隆项目
git clone <repository-url>
cd diet_recommendation_app

# 安装基础依赖
pip install -r requirements.txt

# 安装OCR依赖（可选）
pip install pytesseract opencv-python paddleocr easyocr
```

### 3. OCR引擎配置（可选）

#### Tesseract安装
- **Windows**: 下载 [Tesseract安装包](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

#### 其他OCR引擎
```bash
# PaddleOCR（推荐，中文识别效果好）
pip install paddleocr

# EasyOCR（简单易用）
pip install easyocr
```

### 4. 配置环境
```bash
# 创建环境配置文件
echo "QWEN_API_KEY=your_qwen_api_key_here" > .env
```

### 5. 运行应用
```bash
python main.py
```

### 6. 使用OCR功能
1. 打开应用，进入"记录"页面
2. 点击食物输入框右侧的"📷"按钮
3. 选择包含食物信息的图片
4. 点击"开始识别"进行OCR识别
5. 查看和编辑识别结果
6. 确认保存到餐食记录

## 🔄 工作流程

### 1. 智能数据采集（5天）
- **OCR图片识别**：📷 拍照识别食物热量信息
- **手动数据记录**：详细记录三餐饮食内容
- **用户偏好问卷**：口味偏好、饮食习惯、过敏信息
- **个性化画像**：生理周期、星座、性格特征

### 2. AI模型训练
- **个人推荐模型**：基于采集数据训练个性化模型
- **多因素融合**：结合生理期、星座等多维度因素
- **OCR学习优化**：从用户修正中持续改进识别准确性

### 3. 智能推荐与学习
- **个性化推荐**：第6天开始提供智能推荐
- **用户反馈收集**：喜欢/不喜欢/已食用反馈
- **持续模型优化**：基于反馈数据不断改进
- **OCR准确性提升**：学习用户修正习惯

### 4. AI智能分析
- **千问大模型分析**：每日营养状况智能分析
- **个性化健康建议**：基于用户特征的定制建议
- **营养趋势分析**：长期饮食模式分析

## 🎨 特色功能

### 📷 OCR智能识别
- **多引擎支持**：Tesseract、PaddleOCR、EasyOCR
- **智能验证**：OCR + 数据库 + 用户确认三级验证
- **学习优化**：从用户修正中持续改进
- **一键记录**：拍照即可完成餐食记录

### 🎨 现代化界面
- **移动端设计**：375x812像素，模拟手机界面
- **圆角美化**：统一的圆角设计语言
- **多色主题**：丰富的颜色搭配和视觉层次
- **响应式交互**：悬停效果和状态变化

### 🤖 AI智能分析
- **千问大模型**：阿里云通义千问API集成
- **智能推理**：用户意图分析和营养建议
- **个性化指导**：基于用户特征的定制建议

### 👩 女性专属优化
- **生理周期智能调整**：月经期、排卵期等特殊时期
- **营养需求分析**：不同生理阶段的营养需求
- **个性化建议**：结合生理周期的饮食建议

### ⭐ 个性化因素
- **星座参考**：个性化因素融合
- **性格特征**：基于性格的饮食偏好分析
- **持续学习**：避免随机推荐问题

## 📚 文档说明

- **[OCR使用指南](OCR_USAGE_GUIDE.md)**：详细的OCR功能使用说明
- **[界面美化总结](UI_BEAUTIFICATION_SUMMARY.md)**：界面设计和技术实现
- **[项目总结](PROJECT_SUMMARY.md)**：项目整体架构和功能说明

## 🧪 测试验证

### 功能测试
```bash
# 测试OCR系统
python test_ocr_system.py

# 测试界面美化
python test_ui_beautification.py

# 测试核心功能
python test_core.py
```

### 应用启动测试
```bash
# 启动应用
python main.py

# 检查日志
tail -f logs/app.log
```

## 🚀 技术亮点

### 1. 统一基座架构
- **模块化设计**：所有功能模块基于统一基座构建
- **事件驱动**：模块间通过事件总线通信
- **数据统一**：统一的数据管理和访问接口
- **扩展性强**：支持新功能模块的快速集成

### 2. OCR多引擎融合
- **多引擎并行**：同时使用多个OCR引擎提高准确性
- **智能合并**：基于置信度的结果合并策略
- **学习优化**：从用户修正中持续学习改进
- **数据库匹配**：结合食物数据库进行智能验证

### 3. 现代化界面设计
- **移动端优先**：专为手机屏幕优化的界面设计
- **圆角美化**：统一的圆角设计语言
- **多色主题**：丰富的颜色配置和视觉层次
- **响应式交互**：流畅的用户交互体验

### 4. AI智能分析
- **千问大模型**：集成阿里云通义千问API
- **智能推理**：基于用户数据的智能分析
- **个性化建议**：结合多维度因素的定制建议
- **持续学习**：从用户反馈中不断优化

## 📈 项目状态

- ✅ **核心功能**：数据采集、推荐引擎、AI分析
- ✅ **OCR识别**：多引擎支持、智能验证、学习优化
- ✅ **界面美化**：圆角设计、多色主题、移动端适配
- ✅ **文档完善**：使用指南、技术文档、测试脚本
- 🔄 **持续优化**：性能提升、功能扩展、用户体验改进

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

### 开发环境设置
```bash
# 克隆项目
git clone <repository-url>
cd diet_recommendation_app

# 安装开发依赖
pip install -r requirements.txt

# 运行测试
python test_ocr_system.py
python test_ui_beautification.py
```

### 代码规范
- 遵循PEP 8代码风格
- 添加适当的注释和文档字符串
- 编写单元测试
- 更新相关文档

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

感谢以下开源项目的支持：
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - 现代化Python GUI框架
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - 开源OCR引擎
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 百度开源OCR
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - 简单易用的OCR库
- [scikit-learn](https://scikit-learn.org/) - 机器学习库

---

**🍽️ 让AI为您的饮食健康保驾护航！**