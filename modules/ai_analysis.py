"""
AI分析模块 - 基于基座架构
集成大模型进行用户需求分析和营养建议
"""

from typing import Dict, List, Optional, Any
import json
import requests
from datetime import datetime, date
from core.base import BaseModule, ModuleType, UserData, AnalysisResult, BaseConfig
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # 如果没有.env文件或加载失败，使用默认配置
    pass

# 导入千问客户端
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from llm_integration.qwen_client import get_qwen_client, analyze_user_intent_with_qwen, analyze_nutrition_with_qwen


class AIAnalysisModule(BaseModule):
    """AI分析模块"""
    
    def __init__(self, config: BaseConfig):
        super().__init__(config, ModuleType.USER_ANALYSIS)
        self.qwen_client = None
        self.analysis_templates = self._load_analysis_templates()
    
    def initialize(self) -> bool:
        """初始化模块"""
        try:
            self.logger.info("AI分析模块初始化中...")
            
            # 初始化千问客户端
            self.qwen_client = get_qwen_client()
            self.logger.info("千问客户端初始化成功")
            
            self.is_initialized = True
            self.logger.info("AI分析模块初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"AI分析模块初始化失败: {e}")
            return False
    
    def process(self, input_data: Any, user_data: UserData) -> AnalysisResult:
        """处理AI分析请求"""
        try:
            analysis_type = input_data.get('type', 'user_intent')
            
            if analysis_type == 'user_intent':
                result = self._analyze_user_intent(input_data, user_data)
            elif analysis_type == 'nutrition_analysis':
                result = self._analyze_nutrition(input_data, user_data)
            elif analysis_type == 'calorie_estimation':
                result = self._estimate_calories(input_data, user_data)
            elif analysis_type == 'physiological_state':
                result = self._analyze_physiological_state(input_data, user_data)
            elif analysis_type == 'meal_suggestion':
                result = self._generate_meal_suggestion(input_data, user_data)
            else:
                result = self._create_error_result("未知的分析类型")
            
            return AnalysisResult(
                module_type=self.module_type,
                user_id=user_data.user_id,
                input_data=input_data,
                result=result,
                confidence=result.get('confidence', 0.5)
            )
        except Exception as e:
            self.logger.error(f"处理AI分析请求失败: {e}")
            return self._create_error_result(str(e))
    
    def _analyze_user_intent(self, input_data: Dict, user_data: UserData) -> Dict[str, Any]:
        """分析用户意图"""
        user_input = input_data.get('user_input', '')
        
        if not self.qwen_client:
            return self._get_fallback_intent_analysis(user_input, user_data)
        
        try:
            # 构建用户上下文
            user_context = {
                'name': user_data.profile.get('name', '未知'),
                'age': user_data.profile.get('age', '未知'),
                'gender': user_data.profile.get('gender', '未知'),
                'height': user_data.profile.get('height', '未知'),
                'weight': user_data.profile.get('weight', '未知'),
                'activity_level': user_data.profile.get('activity_level', '未知'),
                'taste_preferences': user_data.profile.get('taste_preferences', {}),
                'allergies': user_data.profile.get('allergies', []),
                'dislikes': user_data.profile.get('dislikes', []),
                'dietary_preferences': user_data.profile.get('dietary_preferences', []),
                'recent_meals': user_data.meals[-3:] if user_data.meals else [],
                'feedback_history': user_data.feedback[-5:] if user_data.feedback else []
            }
            
            # 使用千问分析用户意图
            result = analyze_user_intent_with_qwen(user_input, user_context)
            return result
            
        except Exception as e:
            self.logger.error(f"用户意图分析失败: {e}")
            return self._get_fallback_intent_analysis(user_input, user_data)
    
    def _analyze_nutrition(self, input_data: Dict, user_data: UserData) -> Dict[str, Any]:
        """分析营养状况"""
        meal_data = input_data.get('meal_data', {})
        
        if not self.qwen_client:
            return self._get_fallback_nutrition_analysis(meal_data, user_data)
        
        try:
            # 构建用户上下文
            user_context = {
                'age': user_data.profile.get('age', '未知'),
                'gender': user_data.profile.get('gender', '未知'),
                'height': user_data.profile.get('height', '未知'),
                'weight': user_data.profile.get('weight', '未知'),
                'activity_level': user_data.profile.get('activity_level', '未知'),
                'health_goals': user_data.profile.get('health_goals', [])
            }
            
            # 使用千问分析营养状况
            result = analyze_nutrition_with_qwen(meal_data, user_context)
            return result
            
        except Exception as e:
            self.logger.error(f"营养分析失败: {e}")
            return self._get_fallback_nutrition_analysis(meal_data, user_data)
    
    def _estimate_calories(self, input_data: Dict, user_data: UserData) -> Dict[str, Any]:
        """估算食物热量"""
        food_data = input_data.get('food_data', {})
        food_name = food_data.get('food_name', '')
        quantity = food_data.get('quantity', '')
        
        if not food_name or not quantity:
            return self._create_error_result("缺少食物名称或分量信息")
        
        try:
            # 基础热量数据库
            calorie_db = {
                "米饭": 130, "面条": 110, "包子": 200, "饺子": 250, "馒头": 220, "面包": 250,
                "鸡蛋": 150, "牛奶": 60, "豆浆": 30, "酸奶": 80, "苹果": 50, "香蕉": 90,
                "鸡肉": 165, "牛肉": 250, "猪肉": 300, "鱼肉": 120, "豆腐": 80, "青菜": 20,
                "西红柿": 20, "黄瓜": 15, "胡萝卜": 40, "土豆": 80, "红薯": 100, "玉米": 90
            }
            
            # 获取基础热量
            base_calories = calorie_db.get(food_name, 100)  # 默认100卡路里
            
            # 简单的分量解析
            quantity_lower = quantity.lower()
            if '碗' in quantity_lower:
                multiplier = 1.0
            elif 'g' in quantity_lower or '克' in quantity_lower:
                # 假设一碗米饭约200g
                multiplier = 0.5
            elif '个' in quantity_lower:
                multiplier = 1.0
            else:
                multiplier = 1.0
            
            # 计算总热量
            total_calories = base_calories * multiplier
            
            return {
                'success': True,
                'calories': total_calories,
                'food_name': food_name,
                'quantity': quantity,
                'base_calories': base_calories,
                'multiplier': multiplier,
                'confidence': 0.8
            }
            
        except Exception as e:
            self.logger.error(f"热量估算失败: {e}")
            return self._create_error_result(f"热量估算失败: {str(e)}")
    
    def _analyze_physiological_state(self, input_data: Dict, user_data: UserData) -> Dict[str, Any]:
        """分析生理状态"""
        current_date = input_data.get('current_date', datetime.now().strftime('%Y-%m-%d'))
        
        if not user_data.profile.get('is_female', False):
            return {
                'success': True,
                'physiological_state': 'normal',
                'needs': [],
                'recommendations': [],
                'confidence': 0.8
            }
        
        try:
            cycle_info = self._calculate_menstrual_cycle(user_data.profile, current_date)
            
            if not self.qwen_client:
                return self._get_fallback_physiological_analysis(cycle_info)
            
            prompt = self._build_physiological_analysis_prompt(user_data.profile, cycle_info)
            
            messages = [
                {"role": "system", "content": self._get_physiological_analysis_system_prompt()},
                {"role": "user", "content": prompt}
            ]
            
            response = self.qwen_client.chat_completion(messages, temperature=0.2, max_tokens=800)
            
            if response and 'choices' in response:
                analysis_text = response['choices'][0]['message']['content']
            else:
                return self._get_fallback_physiological_analysis(cycle_info)
            return self._parse_physiological_analysis(analysis_text, cycle_info)
            
        except Exception as e:
            self.logger.error(f"生理状态分析失败: {e}")
            return self._get_fallback_physiological_analysis({})
    
    def _generate_meal_suggestion(self, input_data: Dict, user_data: UserData) -> Dict[str, Any]:
        """生成餐食建议"""
        meal_type = input_data.get('meal_type', 'lunch')
        preferences = input_data.get('preferences', {})
        
        if not self.qwen_client:
            return self._get_fallback_meal_suggestion(meal_type, user_data)
        
        try:
            prompt = self._build_meal_suggestion_prompt(meal_type, preferences, user_data)
            
            messages = [
                {"role": "system", "content": self._get_meal_suggestion_system_prompt()},
                {"role": "user", "content": prompt}
            ]
            
            response = self.qwen_client.chat_completion(messages, temperature=0.4, max_tokens=1000)
            
            if response and 'choices' in response:
                suggestion_text = response['choices'][0]['message']['content']
            else:
                return self._get_fallback_meal_suggestion(meal_type, user_data)
            return self._parse_meal_suggestion(suggestion_text)
            
        except Exception as e:
            self.logger.error(f"餐食建议生成失败: {e}")
            return self._get_fallback_meal_suggestion(meal_type, user_data)
    
    def _build_intent_analysis_prompt(self, user_input: str, user_data: UserData) -> str:
        """构建意图分析提示词"""
        return f"""
请分析以下用户输入的真实意图和需求：

用户输入: "{user_input}"

用户背景:
- 姓名: {user_data.profile.get('name', '未知')}
- 年龄: {user_data.profile.get('age', '未知')}
- 性别: {user_data.profile.get('gender', '未知')}
- 身高体重: {user_data.profile.get('height', '未知')}cm, {user_data.profile.get('weight', '未知')}kg

口味偏好: {json.dumps(user_data.profile.get('taste_preferences', {}), ensure_ascii=False)}
饮食限制: {', '.join(user_data.profile.get('allergies', []) + user_data.profile.get('dislikes', []))}

最近饮食记录: {self._format_recent_meals(user_data.meals[-3:])}

请分析：
1. 用户的真实意图（饿了、馋了、需要特定营养等）
2. 情绪状态（压力、开心、疲惫等）
3. 营养需求
4. 推荐的食物类型
5. 推荐理由

请以JSON格式返回分析结果。
"""
    
    def _build_nutrition_analysis_prompt(self, meal_data: Dict, user_data: UserData) -> str:
        """构建营养分析提示词"""
        return f"""
请分析以下餐食的营养状况：

餐食信息:
- 食物: {', '.join(meal_data.get('foods', []))}
- 分量: {', '.join(meal_data.get('quantities', []))}
- 热量: {meal_data.get('calories', '未知')}卡路里

用户信息:
- 年龄: {user_data.profile.get('age', '未知')}
- 性别: {user_data.profile.get('gender', '未知')}
- 身高体重: {user_data.profile.get('height', '未知')}cm, {user_data.profile.get('weight', '未知')}kg
- 活动水平: {user_data.profile.get('activity_level', '未知')}
- 健康目标: {', '.join(user_data.profile.get('health_goals', []))}

请分析：
1. 营养均衡性
2. 热量是否合适
3. 缺少的营养素
4. 建议改进的地方
5. 个性化建议

请以JSON格式返回分析结果。
"""
    
    def _build_physiological_analysis_prompt(self, profile: Dict, cycle_info: Dict) -> str:
        """构建生理状态分析提示词"""
        return f"""
作为专业的女性健康专家，请分析以下用户的生理状态：

用户信息:
- 年龄: {profile.get('age', '未知')}
- 身高体重: {profile.get('height', '未知')}cm, {profile.get('weight', '未知')}kg
- 月经周期长度: {profile.get('menstrual_cycle_length', '未知')}天
- 上次月经: {profile.get('last_period_date', '未知')}

当前生理周期状态:
- 周期阶段: {cycle_info.get('phase', '未知')}
- 距离下次月经: {cycle_info.get('days_to_next_period', '未知')}天

请分析：
1. 当前生理状态对营养需求的影响
2. 建议补充的营养素
3. 需要避免的食物
4. 情绪和食欲的变化
5. 个性化建议

请以JSON格式返回分析结果。
"""
    
    def _build_meal_suggestion_prompt(self, meal_type: str, preferences: Dict, user_data: UserData) -> str:
        """构建餐食建议提示词"""
        return f"""
请为以下用户推荐{meal_type}：

用户信息:
- 姓名: {user_data.profile.get('name', '未知')}
- 年龄: {user_data.profile.get('age', '未知')}
- 性别: {user_data.profile.get('gender', '未知')}
- 身高体重: {user_data.profile.get('height', '未知')}cm, {user_data.profile.get('weight', '未知')}kg

口味偏好: {json.dumps(user_data.profile.get('taste_preferences', {}), ensure_ascii=False)}
饮食限制: 过敏({', '.join(user_data.profile.get('allergies', []))}), 不喜欢({', '.join(user_data.profile.get('dislikes', []))})
健康目标: {', '.join(user_data.profile.get('health_goals', []))}

特殊偏好: {json.dumps(preferences, ensure_ascii=False)}

请推荐：
1. 3-5种适合的食物
2. 推荐理由
3. 营养搭配建议
4. 制作建议

请以JSON格式返回建议。
"""
    
    def _get_intent_analysis_system_prompt(self) -> str:
        """获取意图分析系统提示词"""
        return """
你是一个专业的营养师和心理学专家，擅长分析用户的饮食需求和心理状态。

你的任务是：
1. 深度理解用户的真实需求，不仅仅是表面的话语
2. 考虑用户的生理状态、情绪状态、历史偏好等多维度因素
3. 提供个性化的饮食建议
4. 特别关注女性用户的生理周期对饮食需求的影响

分析时要：
- 透过现象看本质，理解用户的真实意图
- 综合考虑生理、心理、社会等多重因素
- 提供科学、实用、个性化的建议
- 保持专业性和同理心

返回格式必须是有效的JSON，包含所有必需字段。
"""
    
    def _get_nutrition_analysis_system_prompt(self) -> str:
        """获取营养分析系统提示词"""
        return """
你是一个专业的营养师，擅长分析餐食的营养价值和健康建议。

你的任务是：
1. 分析餐食的营养均衡性
2. 评估热量是否合适
3. 识别缺少的营养素
4. 提供改进建议
5. 考虑用户的个人情况

分析时要：
- 基于科学的营养学知识
- 考虑用户的年龄、性别、体重、活动水平等因素
- 提供具体可行的建议
- 保持客观和专业

返回格式必须是有效的JSON，包含所有必需字段。
"""
    
    def _get_physiological_analysis_system_prompt(self) -> str:
        """获取生理状态分析系统提示词"""
        return """
你是专业的女性健康专家，了解生理周期对营养需求的影响。

你的任务是：
1. 分析女性用户的生理周期状态
2. 评估当前阶段的营养需求
3. 提供针对性的饮食建议
4. 考虑情绪和食欲的变化
5. 提供个性化建议

分析时要：
- 基于科学的生理学知识
- 考虑个体差异
- 提供温和、实用的建议
- 保持专业和同理心

返回格式必须是有效的JSON，包含所有必需字段。
"""
    
    def _get_meal_suggestion_system_prompt(self) -> str:
        """获取餐食建议系统提示词"""
        return """
你是一个专业的营养师和厨师，擅长根据用户需求推荐合适的餐食。

你的任务是：
1. 根据用户的口味偏好推荐食物
2. 考虑饮食限制和过敏情况
3. 提供营养均衡的建议
4. 考虑用户的健康目标
5. 提供实用的制作建议

推荐时要：
- 基于营养学原理
- 考虑用户的个人喜好
- 提供多样化的选择
- 保持实用性和可操作性

返回格式必须是有效的JSON，包含所有必需字段。
"""
    
    def _calculate_menstrual_cycle(self, profile: Dict, current_date: str) -> Dict[str, Any]:
        """计算月经周期状态"""
        try:
            last_period = datetime.strptime(profile.get('last_period_date', ''), '%Y-%m-%d')
            current = datetime.strptime(current_date, '%Y-%m-%d')
            cycle_length = profile.get('menstrual_cycle_length', 28)
            
            days_since_period = (current - last_period).days
            days_to_next_period = cycle_length - (days_since_period % cycle_length)
            
            # 判断周期阶段
            if days_since_period % cycle_length < 5:
                phase = "月经期"
            elif days_since_period % cycle_length < 14:
                phase = "卵泡期"
            elif days_since_period % cycle_length < 18:
                phase = "排卵期"
            else:
                phase = "黄体期"
            
            return {
                "phase": phase,
                "days_since_period": days_since_period % cycle_length,
                "days_to_next_period": days_to_next_period,
                "is_ovulation": phase == "排卵期",
                "cycle_length": cycle_length
            }
        except Exception:
            return {
                "phase": "未知",
                "days_since_period": 0,
                "days_to_next_period": 0,
                "is_ovulation": False,
                "cycle_length": 28
            }
    
    def _format_recent_meals(self, meals: List[Dict]) -> str:
        """格式化最近餐食"""
        if not meals:
            return "暂无饮食记录"
        
        formatted = []
        for meal in meals:
            foods = ', '.join(meal.get('foods', []))
            satisfaction = meal.get('satisfaction_score', '未知')
            formatted.append(f"- {meal.get('date', '')} {meal.get('meal_type', '')}: {foods} (满意度: {satisfaction})")
        
        return '\n'.join(formatted)
    
    def _parse_intent_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """解析意图分析结果"""
        try:
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = analysis_text[start_idx:end_idx]
                result_dict = json.loads(json_str)
                
                return {
                    'success': True,
                    'user_intent': result_dict.get('user_intent', ''),
                    'emotional_state': result_dict.get('emotional_state', ''),
                    'nutritional_needs': result_dict.get('nutritional_needs', []),
                    'recommended_foods': result_dict.get('recommended_foods', []),
                    'reasoning': result_dict.get('reasoning', ''),
                    'confidence': result_dict.get('confidence', 0.5)
                }
        except Exception as e:
            self.logger.error(f"解析意图分析结果失败: {e}")
        
        return self._get_fallback_intent_analysis("", None)
    
    def _parse_nutrition_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """解析营养分析结果"""
        try:
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = analysis_text[start_idx:end_idx]
                result_dict = json.loads(json_str)
                
                return {
                    'success': True,
                    'nutrition_balance': result_dict.get('nutrition_balance', ''),
                    'calorie_assessment': result_dict.get('calorie_assessment', ''),
                    'missing_nutrients': result_dict.get('missing_nutrients', []),
                    'improvements': result_dict.get('improvements', []),
                    'recommendations': result_dict.get('recommendations', []),
                    'confidence': result_dict.get('confidence', 0.5)
                }
        except Exception as e:
            self.logger.error(f"解析营养分析结果失败: {e}")
        
        return self._get_fallback_nutrition_analysis({}, None)
    
    def _parse_physiological_analysis(self, analysis_text: str, cycle_info: Dict) -> Dict[str, Any]:
        """解析生理状态分析结果"""
        try:
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = analysis_text[start_idx:end_idx]
                result_dict = json.loads(json_str)
                
                return {
                    'success': True,
                    'physiological_state': result_dict.get('physiological_state', cycle_info.get('phase', '')),
                    'nutritional_needs': result_dict.get('nutritional_needs', []),
                    'foods_to_avoid': result_dict.get('foods_to_avoid', []),
                    'emotional_changes': result_dict.get('emotional_changes', ''),
                    'appetite_changes': result_dict.get('appetite_changes', ''),
                    'recommendations': result_dict.get('recommendations', []),
                    'cycle_info': cycle_info,
                    'confidence': result_dict.get('confidence', 0.5)
                }
        except Exception as e:
            self.logger.error(f"解析生理分析结果失败: {e}")
        
        return self._get_fallback_physiological_analysis(cycle_info)
    
    def _parse_meal_suggestion(self, suggestion_text: str) -> Dict[str, Any]:
        """解析餐食建议结果"""
        try:
            start_idx = suggestion_text.find('{')
            end_idx = suggestion_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = suggestion_text[start_idx:end_idx]
                result_dict = json.loads(json_str)
                
                return {
                    'success': True,
                    'recommended_foods': result_dict.get('recommended_foods', []),
                    'reasoning': result_dict.get('reasoning', ''),
                    'nutrition_tips': result_dict.get('nutrition_tips', []),
                    'cooking_suggestions': result_dict.get('cooking_suggestions', []),
                    'confidence': result_dict.get('confidence', 0.5)
                }
        except Exception as e:
            self.logger.error(f"解析餐食建议结果失败: {e}")
        
        return self._get_fallback_meal_suggestion("lunch", None)
    
    def _get_fallback_intent_analysis(self, user_input: str, user_data: UserData) -> Dict[str, Any]:
        """获取备用意图分析结果"""
        return {
            'success': True,
            'user_intent': '需要饮食建议',
            'emotional_state': '正常',
            'nutritional_needs': ['均衡营养'],
            'recommended_foods': ['米饭', '蔬菜', '蛋白质'],
            'reasoning': '基于基础营养需求',
            'confidence': 0.3
        }
    
    def _get_fallback_nutrition_analysis(self, meal_data: Dict, user_data: UserData) -> Dict[str, Any]:
        """获取备用营养分析结果"""
        return {
            'success': True,
            'nutrition_balance': '基本均衡',
            'calorie_assessment': '适中',
            'missing_nutrients': [],
            'improvements': ['增加蔬菜摄入'],
            'recommendations': ['保持均衡饮食'],
            'confidence': 0.3
        }
    
    def _get_fallback_physiological_analysis(self, cycle_info: Dict) -> Dict[str, Any]:
        """获取备用生理状态分析结果"""
        return {
            'success': True,
            'physiological_state': cycle_info.get('phase', '正常'),
            'nutritional_needs': ['均衡营养'],
            'foods_to_avoid': [],
            'emotional_changes': '正常',
            'appetite_changes': '正常',
            'recommendations': ['保持规律饮食'],
            'cycle_info': cycle_info,
            'confidence': 0.3
        }
    
    def _get_fallback_meal_suggestion(self, meal_type: str, user_data: UserData) -> Dict[str, Any]:
        """获取备用餐食建议结果"""
        return {
            'success': True,
            'recommended_foods': ['米饭', '蔬菜', '蛋白质'],
            'reasoning': '营养均衡的基础搭配',
            'nutrition_tips': ['注意营养搭配'],
            'cooking_suggestions': ['简单烹饪'],
            'confidence': 0.3
        }
    
    def _load_analysis_templates(self) -> Dict[str, Dict]:
        """加载分析模板"""
        return {
            'intent_analysis': {
                'description': '用户意图分析',
                'required_fields': ['user_input']
            },
            'nutrition_analysis': {
                'description': '营养状况分析',
                'required_fields': ['meal_data']
            },
            'physiological_state': {
                'description': '生理状态分析',
                'required_fields': ['current_date']
            },
            'meal_suggestion': {
                'description': '餐食建议生成',
                'required_fields': ['meal_type']
            }
        }
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """创建错误结果"""
        return {
            'success': False,
            'error': error_message,
            'message': f'AI分析失败: {error_message}',
            'confidence': 0.0
        }
    
    def cleanup(self) -> bool:
        """清理资源"""
        try:
            self.logger.info("AI分析模块清理完成")
            return True
        except Exception as e:
            self.logger.error(f"AI分析模块清理失败: {e}")
            return False


# 便捷函数
def analyze_user_intent(user_id: str, user_input: str) -> Optional[Dict]:
    """分析用户意图"""
    from core.base import get_app_core
    
    app = get_app_core()
    input_data = {
        'type': 'user_intent',
        'user_input': user_input
    }
    
    result = app.process_user_request(ModuleType.USER_ANALYSIS, input_data, user_id)
    return result.result if result else None


def analyze_nutrition(user_id: str, meal_data: Dict) -> Optional[Dict]:
    """分析营养状况"""
    from core.base import get_app_core
    
    app = get_app_core()
    input_data = {
        'type': 'nutrition_analysis',
        'meal_data': meal_data
    }
    
    result = app.process_user_request(ModuleType.USER_ANALYSIS, input_data, user_id)
    return result.result if result else None


def analyze_physiological_state(user_id: str, current_date: str = None) -> Optional[Dict]:
    """分析生理状态"""
    from core.base import get_app_core
    from datetime import datetime
    
    if current_date is None:
        current_date = datetime.now().strftime('%Y-%m-%d')
    
    app = get_app_core()
    input_data = {
        'type': 'physiological_state',
        'current_date': current_date
    }
    
    result = app.process_user_request(ModuleType.USER_ANALYSIS, input_data, user_id)
    return result.result if result else None


def generate_meal_suggestion(user_id: str, meal_type: str, preferences: Dict = None) -> Optional[Dict]:
    """生成餐食建议"""
    from core.base import get_app_core
    
    if preferences is None:
        preferences = {}
    
    app = get_app_core()
    input_data = {
        'type': 'meal_suggestion',
        'meal_type': meal_type,
        'preferences': preferences
    }
    
    result = app.process_user_request(ModuleType.USER_ANALYSIS, input_data, user_id)
    return result.result if result else None


if __name__ == "__main__":
    # 测试AI分析模块
    from core.base import BaseConfig, initialize_app, cleanup_app
    
    print("测试AI分析模块...")
    
    # 初始化应用
    config = BaseConfig()
    if initialize_app(config):
        print("✅ 应用初始化成功")
        
        # 测试用户意图分析
        test_user_id = "test_user_001"
        user_input = "我今天有点累，想吃点甜的，但是又怕胖"
        
        result = analyze_user_intent(test_user_id, user_input)
        if result:
            print(f"✅ 用户意图分析成功: {result.get('user_intent', '')}")
        
        # 测试营养分析
        meal_data = {
            'foods': ['燕麦粥', '香蕉', '牛奶'],
            'quantities': ['1碗', '1根', '200ml'],
            'calories': 350.0
        }
        
        result = analyze_nutrition(test_user_id, meal_data)
        if result:
            print(f"✅ 营养分析成功: {result.get('nutrition_balance', '')}")
        
        # 清理应用
        cleanup_app()
        print("✅ 应用清理完成")
    else:
        print("❌ 应用初始化失败")
    
    print("AI分析模块测试完成！")
