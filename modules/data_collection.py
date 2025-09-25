"""
数据采集模块 - 基于基座架构
负责收集用户数据、问卷和餐食记录
"""

from typing import Dict, List, Optional, Any
import json
from datetime import datetime, date
from core.base import BaseModule, ModuleType, UserData, AnalysisResult, BaseConfig


class DataCollectionModule(BaseModule):
    """数据采集模块"""
    
    def __init__(self, config: BaseConfig):
        super().__init__(config, ModuleType.DATA_COLLECTION)
        self.questionnaire_templates = self._load_questionnaire_templates()
    
    def initialize(self) -> bool:
        """初始化模块"""
        try:
            self.logger.info("数据采集模块初始化中...")
            self.is_initialized = True
            self.logger.info("数据采集模块初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"数据采集模块初始化失败: {e}")
            return False
    
    def process(self, input_data: Any, user_data: UserData) -> AnalysisResult:
        """处理数据采集请求"""
        try:
            request_type = input_data.get('type', 'unknown')
            
            if request_type == 'questionnaire':
                result = self._process_questionnaire(input_data, user_data)
            elif request_type == 'meal_record':
                result = self._process_meal_record(input_data, user_data)
            elif request_type == 'feedback':
                result = self._process_feedback(input_data, user_data)
            else:
                result = self._create_error_result("未知的请求类型")
            
            return AnalysisResult(
                module_type=self.module_type,
                user_id=user_data.user_id,
                input_data=input_data,
                result=result,
                confidence=0.9 if result.get('success', False) else 0.1
            )
        except Exception as e:
            self.logger.error(f"处理数据采集请求失败: {e}")
            return self._create_error_result(str(e))
    
    def _process_questionnaire(self, input_data: Dict, user_data: UserData) -> Dict[str, Any]:
        """处理问卷数据"""
        questionnaire_type = input_data.get('questionnaire_type', 'basic')
        answers = input_data.get('answers', {})
        
        # 根据问卷类型处理答案
        if questionnaire_type == 'basic':
            processed_data = self._process_basic_questionnaire(answers)
        elif questionnaire_type == 'taste':
            processed_data = self._process_taste_questionnaire(answers)
        elif questionnaire_type == 'physiological':
            processed_data = self._process_physiological_questionnaire(answers)
        else:
            processed_data = answers
        
        # 更新用户数据
        user_data.profile.update(processed_data)
        user_data.updated_at = datetime.now().isoformat()
        
        return {
            'success': True,
            'processed_data': processed_data,
            'message': f'{questionnaire_type}问卷处理完成'
        }
    
    def _process_meal_record(self, input_data: Dict, user_data: UserData) -> Dict[str, Any]:
        """处理餐食记录"""
        meal_data = {
            'date': input_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'meal_type': input_data.get('meal_type', 'unknown'),
            'foods': input_data.get('foods', []),
            'quantities': input_data.get('quantities', []),
            'calories': input_data.get('calories'),
            'satisfaction_score': input_data.get('satisfaction_score'),
            'notes': input_data.get('notes', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        # 添加到用户餐食记录
        user_data.meals.append(meal_data)
        user_data.updated_at = datetime.now().isoformat()
        
        return {
            'success': True,
            'meal_data': meal_data,
            'message': '餐食记录保存成功'
        }
    
    def _process_feedback(self, input_data: Dict, user_data: UserData) -> Dict[str, Any]:
        """处理用户反馈"""
        feedback_data = {
            'date': input_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'recommended_foods': input_data.get('recommended_foods', []),
            'user_choice': input_data.get('user_choice', ''),
            'feedback_type': input_data.get('feedback_type', 'unknown'),
            'satisfaction_score': input_data.get('satisfaction_score'),
            'notes': input_data.get('notes', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        # 添加到用户反馈记录
        user_data.feedback.append(feedback_data)
        user_data.updated_at = datetime.now().isoformat()
        
        return {
            'success': True,
            'feedback_data': feedback_data,
            'message': '反馈记录保存成功'
        }
    
    def _process_basic_questionnaire(self, answers: Dict) -> Dict[str, Any]:
        """处理基础信息问卷"""
        return {
            'name': answers.get('name', ''),
            'age': int(answers.get('age', 0)),
            'gender': answers.get('gender', ''),
            'height': float(answers.get('height', 0)),
            'weight': float(answers.get('weight', 0)),
            'activity_level': answers.get('activity_level', ''),
            'health_goals': answers.get('health_goals', [])
        }
    
    def _process_taste_questionnaire(self, answers: Dict) -> Dict[str, Any]:
        """处理口味偏好问卷"""
        return {
            'taste_preferences': {
                'sweet': int(answers.get('sweet', 3)),
                'salty': int(answers.get('salty', 3)),
                'spicy': int(answers.get('spicy', 3)),
                'sour': int(answers.get('sour', 3)),
                'bitter': int(answers.get('bitter', 3)),
                'umami': int(answers.get('umami', 3))
            },
            'dietary_preferences': answers.get('dietary_preferences', []),
            'allergies': answers.get('allergies', []),
            'dislikes': answers.get('dislikes', [])
        }
    
    def _process_physiological_questionnaire(self, answers: Dict) -> Dict[str, Any]:
        """处理生理信息问卷"""
        return {
            'is_female': answers.get('gender') == '女',
            'menstrual_cycle_length': int(answers.get('menstrual_cycle_length', 28)),
            'last_period_date': answers.get('last_period_date', ''),
            'ovulation_symptoms': answers.get('ovulation_symptoms', []),
            'zodiac_sign': answers.get('zodiac_sign', ''),
            'personality_traits': answers.get('personality_traits', [])
        }
    
    def _load_questionnaire_templates(self) -> Dict[str, Dict]:
        """加载问卷模板"""
        return {
            'basic': {
                'title': '基本信息问卷',
                'questions': {
                    'name': {'question': '您的姓名', 'type': 'text'},
                    'age': {'question': '您的年龄', 'type': 'number', 'min': 1, 'max': 120},
                    'gender': {'question': '性别', 'type': 'select', 'options': ['男', '女']},
                    'height': {'question': '身高 (cm)', 'type': 'number', 'min': 100, 'max': 250},
                    'weight': {'question': '体重 (kg)', 'type': 'number', 'min': 30, 'max': 200},
                    'activity_level': {
                        'question': '日常活动水平',
                        'type': 'select',
                        'options': ['久坐', '轻度活动', '中度活动', '高度活动', '极高活动']
                    },
                    'health_goals': {
                        'question': '健康目标 (可多选)',
                        'type': 'checkbox',
                        'options': ['减肥', '增肌', '维持体重', '提高免疫力', '改善消化']
                    }
                }
            },
            'taste': {
                'title': '口味偏好问卷',
                'questions': {
                    'sweet': {'question': '甜味偏好 (1-5分)', 'type': 'scale', 'min': 1, 'max': 5},
                    'salty': {'question': '咸味偏好 (1-5分)', 'type': 'scale', 'min': 1, 'max': 5},
                    'spicy': {'question': '辣味偏好 (1-5分)', 'type': 'scale', 'min': 1, 'max': 5},
                    'sour': {'question': '酸味偏好 (1-5分)', 'type': 'scale', 'min': 1, 'max': 5},
                    'bitter': {'question': '苦味偏好 (1-5分)', 'type': 'scale', 'min': 1, 'max': 5},
                    'umami': {'question': '鲜味偏好 (1-5分)', 'type': 'scale', 'min': 1, 'max': 5},
                    'dietary_preferences': {
                        'question': '饮食限制 (可多选)',
                        'type': 'checkbox',
                        'options': ['素食', '纯素食', '无麸质', '无乳制品', '无坚果', '低钠', '低碳水', '无糖']
                    },
                    'allergies': {
                        'question': '过敏食物 (可多选)',
                        'type': 'checkbox',
                        'options': ['花生', '坚果', '海鲜', '鸡蛋', '牛奶', '大豆', '小麦', '无过敏']
                    },
                    'dislikes': {
                        'question': '不喜欢的食物类型',
                        'type': 'checkbox',
                        'options': ['内脏', '海鲜', '蘑菇', '香菜', '洋葱', '大蒜', '辛辣食物', '甜食']
                    }
                }
            },
            'physiological': {
                'title': '生理信息问卷',
                'questions': {
                    'menstrual_cycle_length': {
                        'question': '月经周期长度 (天)',
                        'type': 'number',
                        'min': 20,
                        'max': 40,
                        'optional': True
                    },
                    'last_period_date': {
                        'question': '上次月经日期',
                        'type': 'date',
                        'optional': True
                    },
                    'ovulation_symptoms': {
                        'question': '排卵期症状 (可多选)',
                        'type': 'checkbox',
                        'options': ['乳房胀痛', '情绪波动', '食欲变化', '疲劳', '无特殊症状'],
                        'optional': True
                    },
                    'zodiac_sign': {
                        'question': '星座',
                        'type': 'select',
                        'options': ['白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座',
                                  '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座'],
                        'optional': True
                    },
                    'personality_traits': {
                        'question': '性格特征 (可多选)',
                        'type': 'checkbox',
                        'options': ['外向', '内向', '理性', '感性', '冒险', '保守', '创新', '传统'],
                        'optional': True
                    }
                }
            }
        }
    
    def get_questionnaire_template(self, questionnaire_type: str) -> Optional[Dict]:
        """获取问卷模板"""
        return self.questionnaire_templates.get(questionnaire_type)
    
    def get_all_questionnaire_types(self) -> List[str]:
        """获取所有问卷类型"""
        return list(self.questionnaire_templates.keys())
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """创建错误结果"""
        return {
            'success': False,
            'error': error_message,
            'message': f'数据采集失败: {error_message}'
        }
    
    def cleanup(self) -> bool:
        """清理资源"""
        try:
            self.logger.info("数据采集模块清理完成")
            return True
        except Exception as e:
            self.logger.error(f"数据采集模块清理失败: {e}")
            return False


# 便捷函数
def collect_questionnaire_data(user_id: str, questionnaire_type: str, answers: Dict) -> bool:
    """收集问卷数据"""
    from core.base import get_app_core
    
    app = get_app_core()
    input_data = {
        'type': 'questionnaire',
        'questionnaire_type': questionnaire_type,
        'answers': answers
    }
    
    result = app.process_user_request(ModuleType.DATA_COLLECTION, input_data, user_id)
    return result and result.result.get('success', False)


def record_meal(user_id: str, meal_data: Dict) -> bool:
    """记录餐食"""
    from core.base import get_app_core
    
    app = get_app_core()
    input_data = {
        'type': 'meal_record',
        **meal_data
    }
    
    result = app.process_user_request(ModuleType.DATA_COLLECTION, input_data, user_id)
    return result and result.result.get('success', False)


def record_feedback(user_id: str, feedback_data: Dict) -> bool:
    """记录反馈"""
    from core.base import get_app_core
    
    app = get_app_core()
    input_data = {
        'type': 'feedback',
        **feedback_data
    }
    
    result = app.process_user_request(ModuleType.DATA_COLLECTION, input_data, user_id)
    return result and result.result.get('success', False)


if __name__ == "__main__":
    # 测试数据采集模块
    from core.base import BaseConfig, initialize_app, cleanup_app
    
    print("测试数据采集模块...")
    
    # 初始化应用
    config = BaseConfig()
    if initialize_app(config):
        print("✅ 应用初始化成功")
        
        # 测试问卷数据收集
        test_user_id = "test_user_001"
        questionnaire_answers = {
            'name': '小美',
            'age': 25,
            'gender': '女',
            'height': 165,
            'weight': 55,
            'activity_level': '中度活动',
            'health_goals': ['维持体重', '提高免疫力']
        }
        
        if collect_questionnaire_data(test_user_id, 'basic', questionnaire_answers):
            print("✅ 基础问卷数据收集成功")
        
        # 测试餐食记录
        meal_data = {
            'date': '2024-01-15',
            'meal_type': 'breakfast',
            'foods': ['燕麦粥', '香蕉', '牛奶'],
            'quantities': ['1碗', '1根', '200ml'],
            'calories': 350.0,
            'satisfaction_score': 4,
            'notes': '很满意，营养均衡'
        }
        
        if record_meal(test_user_id, meal_data):
            print("✅ 餐食记录成功")
        
        # 清理应用
        cleanup_app()
        print("✅ 应用清理完成")
    else:
        print("❌ 应用初始化失败")
    
    print("数据采集模块测试完成！")
