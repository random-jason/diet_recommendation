"""
千问大模型集成模块
支持千问API的智能分析功能
"""

import requests
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """大模型配置"""
    provider: str
    api_key: str
    base_url: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2000


class QwenLLMClient:
    """千问大模型客户端"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        })
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Optional[Dict]:
        """聊天完成"""
        try:
            # 构建请求数据
            data = {
                'model': self.config.model,
                'messages': messages,
                'temperature': kwargs.get('temperature', self.config.temperature),
                'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
                'stream': False
            }
            
            # 发送请求
            response = self.session.post(
                f"{self.config.base_url}/chat/completions",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"千问API请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"千问API调用失败: {e}")
            return None
    
    def analyze_user_intent(self, user_input: str, user_context: Dict) -> Dict[str, Any]:
        """分析用户意图"""
        system_prompt = """
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

请以JSON格式返回分析结果，包含以下字段：
- user_intent: 用户真实意图
- emotional_state: 情绪状态
- nutritional_needs: 营养需求列表
- recommended_foods: 推荐食物列表
- reasoning: 推荐理由
- confidence: 置信度(0-1)
"""
        
        user_prompt = f"""
请分析以下用户输入的真实需求和意图：

用户输入: "{user_input}"

用户背景信息:
- 姓名: {user_context.get('name', '未知')}
- 年龄: {user_context.get('age', '未知')}
- 性别: {user_context.get('gender', '未知')}
- 身高体重: {user_context.get('height', '未知')}cm, {user_context.get('weight', '未知')}kg
- 活动水平: {user_context.get('activity_level', '未知')}

口味偏好: {json.dumps(user_context.get('taste_preferences', {}), ensure_ascii=False, indent=2)}

饮食限制:
- 过敏: {', '.join(user_context.get('allergies', []))}
- 不喜欢: {', '.join(user_context.get('dislikes', []))}
- 饮食偏好: {', '.join(user_context.get('dietary_preferences', []))}

最近3天饮食记录: {self._format_meal_history(user_context.get('recent_meals', []))}

用户反馈历史: {self._format_feedback_history(user_context.get('feedback_history', []))}

当前情况:
- 日期: {datetime.now().strftime('%Y-%m-%d')}
- 生理状态: {json.dumps(user_context.get('physiological_state', {}), ensure_ascii=False)}

请从以下维度分析用户需求:

1. **真实意图分析**: 用户真正想要什么？是饿了、馋了、还是需要特定营养？

2. **情绪状态**: 用户当前的情绪如何？压力大、开心、疲惫、焦虑等？

3. **生理需求**: 基于用户的身体状况、生理周期等，需要什么营养？

4. **口味偏好**: 基于历史数据和当前状态，推测用户可能的口味偏好

5. **饮食限制**: 考虑过敏、不喜欢、饮食偏好等限制

6. **推荐食物**: 基于以上分析，推荐3-5种合适的食物

7. **推荐理由**: 解释为什么推荐这些食物

8. **置信度**: 对分析的信心程度 (0-1)

请以JSON格式返回分析结果。
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.chat_completion(messages, temperature=0.3)
        
        if response and 'choices' in response:
            content = response['choices'][0]['message']['content']
            return self._parse_analysis_result(content)
        else:
            return self._get_fallback_analysis(user_input, user_context)
    
    def analyze_nutrition(self, meal_data: Dict, user_context: Dict) -> Dict[str, Any]:
        """分析营养状况"""
        system_prompt = """
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

请以JSON格式返回分析结果，包含以下字段：
- nutrition_balance: 营养均衡性评估
- calorie_assessment: 热量评估
- missing_nutrients: 缺少的营养素列表
- improvements: 改进建议列表
- recommendations: 个性化建议列表
- confidence: 置信度(0-1)
"""
        
        user_prompt = f"""
请分析以下餐食的营养状况：

餐食信息:
- 食物: {', '.join(meal_data.get('foods', []))}
- 分量: {', '.join(meal_data.get('quantities', []))}
- 热量: {meal_data.get('calories', '未知')}卡路里

用户信息:
- 年龄: {user_context.get('age', '未知')}
- 性别: {user_context.get('gender', '未知')}
- 身高体重: {user_context.get('height', '未知')}cm, {user_context.get('weight', '未知')}kg
- 活动水平: {user_context.get('activity_level', '未知')}
- 健康目标: {', '.join(user_context.get('health_goals', []))}

请分析：
1. 营养均衡性
2. 热量是否合适
3. 缺少的营养素
4. 建议改进的地方
5. 个性化建议

请以JSON格式返回分析结果。
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.chat_completion(messages, temperature=0.2)
        
        if response and 'choices' in response:
            content = response['choices'][0]['message']['content']
            return self._parse_nutrition_analysis(content)
        else:
            return self._get_fallback_nutrition_analysis(meal_data, user_context)
    
    def analyze_physiological_state(self, profile: Dict, cycle_info: Dict) -> Dict[str, Any]:
        """分析生理状态"""
        system_prompt = """
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

请以JSON格式返回分析结果，包含以下字段：
- physiological_state: 生理状态描述
- nutritional_needs: 营养需求列表
- foods_to_avoid: 需要避免的食物列表
- emotional_changes: 情绪变化描述
- appetite_changes: 食欲变化描述
- recommendations: 个性化建议列表
- confidence: 置信度(0-1)
"""
        
        user_prompt = f"""
作为专业的女性健康专家，请分析以下用户的生理状态和营养需求：

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
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.chat_completion(messages, temperature=0.2)
        
        if response and 'choices' in response:
            content = response['choices'][0]['message']['content']
            return self._parse_physiological_analysis(content, cycle_info)
        else:
            return self._get_fallback_physiological_analysis(cycle_info)
    
    def generate_meal_suggestion(self, meal_type: str, preferences: Dict, user_context: Dict) -> Dict[str, Any]:
        """生成餐食建议"""
        system_prompt = """
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

请以JSON格式返回建议，包含以下字段：
- recommended_foods: 推荐食物列表
- reasoning: 推荐理由
- nutrition_tips: 营养搭配建议列表
- cooking_suggestions: 制作建议列表
- confidence: 置信度(0-1)
"""
        
        user_prompt = f"""
请为以下用户推荐{meal_type}：

用户信息:
- 姓名: {user_context.get('name', '未知')}
- 年龄: {user_context.get('age', '未知')}
- 性别: {user_context.get('gender', '未知')}
- 身高体重: {user_context.get('height', '未知')}cm, {user_context.get('weight', '未知')}kg

口味偏好: {json.dumps(user_context.get('taste_preferences', {}), ensure_ascii=False)}
饮食限制: 过敏({', '.join(user_context.get('allergies', []))}), 不喜欢({', '.join(user_context.get('dislikes', []))})
健康目标: {', '.join(user_context.get('health_goals', []))}

特殊偏好: {json.dumps(preferences, ensure_ascii=False)}

请推荐：
1. 3-5种适合的食物
2. 推荐理由
3. 营养搭配建议
4. 制作建议

请以JSON格式返回建议。
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.chat_completion(messages, temperature=0.4)
        
        if response and 'choices' in response:
            content = response['choices'][0]['message']['content']
            return self._parse_meal_suggestion(content)
        else:
            return self._get_fallback_meal_suggestion(meal_type, user_context)
    
    def _format_meal_history(self, meals: List[Dict]) -> str:
        """格式化餐食历史"""
        if not meals:
            return "暂无饮食记录"
        
        formatted = []
        for meal in meals:
            foods = ', '.join(meal.get('foods', []))
            satisfaction = meal.get('satisfaction_score', '未知')
            formatted.append(f"- {meal.get('date', '')} {meal.get('meal_type', '')}: {foods} (满意度: {satisfaction})")
        
        return '\n'.join(formatted)
    
    def _format_feedback_history(self, feedbacks: List[Dict]) -> str:
        """格式化反馈历史"""
        if not feedbacks:
            return "暂无反馈记录"
        
        formatted = []
        for feedback in feedbacks:
            recommended = ', '.join(feedback.get('recommended_foods', []))
            choice = feedback.get('user_choice', '未知')
            feedback_type = feedback.get('feedback_type', '未知')
            formatted.append(f"- 推荐: {recommended} | 选择: {choice} | 反馈: {feedback_type}")
        
        return '\n'.join(formatted)
    
    def _parse_analysis_result(self, analysis_text: str) -> Dict[str, Any]:
        """解析分析结果"""
        try:
            # 尝试提取JSON部分
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
            logger.error(f"解析分析结果失败: {e}")
        
        return self._get_fallback_analysis("", {})
    
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
            logger.error(f"解析营养分析结果失败: {e}")
        
        return self._get_fallback_nutrition_analysis({}, {})
    
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
            logger.error(f"解析生理分析结果失败: {e}")
        
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
            logger.error(f"解析餐食建议结果失败: {e}")
        
        return self._get_fallback_meal_suggestion("lunch", {})
    
    def _get_fallback_analysis(self, user_input: str, user_context: Dict) -> Dict[str, Any]:
        """获取备用分析结果"""
        return {
            'success': True,
            'user_intent': '需要饮食建议',
            'emotional_state': '正常',
            'nutritional_needs': ['均衡营养'],
            'recommended_foods': ['米饭', '蔬菜', '蛋白质'],
            'reasoning': '基于基础营养需求',
            'confidence': 0.3
        }
    
    def _get_fallback_nutrition_analysis(self, meal_data: Dict, user_context: Dict) -> Dict[str, Any]:
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
    
    def _get_fallback_meal_suggestion(self, meal_type: str, user_context: Dict) -> Dict[str, Any]:
        """获取备用餐食建议结果"""
        return {
            'success': True,
            'recommended_foods': ['米饭', '蔬菜', '蛋白质'],
            'reasoning': '营养均衡的基础搭配',
            'nutrition_tips': ['注意营养搭配'],
            'cooking_suggestions': ['简单烹饪'],
            'confidence': 0.3
        }


# 千问配置 - 从环境变量获取
def get_qwen_config() -> LLMConfig:
    """获取千问配置"""
    api_key = os.getenv('QWEN_API_KEY', '')
    base_url = os.getenv('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    model = os.getenv('QWEN_MODEL', 'qwen-plus-latest')
    
    return LLMConfig(
        provider="qwen",
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0.7,
        max_tokens=2000
    )


# 全局千问客户端实例
qwen_client: Optional[QwenLLMClient] = None


def get_qwen_client() -> QwenLLMClient:
    """获取千问客户端实例"""
    global qwen_client
    if qwen_client is None:
        config = get_qwen_config()
        qwen_client = QwenLLMClient(config)
    return qwen_client


# 便捷函数
def analyze_user_intent_with_qwen(user_input: str, user_context: Dict) -> Dict[str, Any]:
    """使用千问分析用户意图"""
    client = get_qwen_client()
    return client.analyze_user_intent(user_input, user_context)


def analyze_nutrition_with_qwen(meal_data: Dict, user_context: Dict) -> Dict[str, Any]:
    """使用千问分析营养状况"""
    client = get_qwen_client()
    return client.analyze_nutrition(meal_data, user_context)


def analyze_physiological_state_with_qwen(profile: Dict, cycle_info: Dict) -> Dict[str, Any]:
    """使用千问分析生理状态"""
    client = get_qwen_client()
    return client.analyze_physiological_state(profile, cycle_info)


def generate_meal_suggestion_with_qwen(meal_type: str, preferences: Dict, user_context: Dict) -> Dict[str, Any]:
    """使用千问生成餐食建议"""
    client = get_qwen_client()
    return client.generate_meal_suggestion(meal_type, preferences, user_context)


if __name__ == "__main__":
    # 测试千问大模型集成
    print("测试千问大模型集成...")
    
    # 测试用户意图分析
    user_input = "我今天有点累，想吃点甜的，但是又怕胖"
    user_context = {
        'name': '小美',
        'age': 25,
        'gender': '女',
        'height': 165,
        'weight': 55,
        'taste_preferences': {'sweet': 4, 'salty': 3, 'spicy': 2},
        'allergies': ['花生'],
        'dislikes': ['内脏'],
        'recent_meals': [],
        'feedback_history': []
    }
    
    result = analyze_user_intent_with_qwen(user_input, user_context)
    print(f"用户意图分析结果: {result}")
    
    print("千问大模型集成测试完成！")
