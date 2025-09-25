"""
核心基座架构 - 个性化饮食推荐系统
提供统一的基础设施和接口，所有功能模块都基于此基座构建
"""

import json
import sqlite3
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, date
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """用户画像 - 统一数据结构"""
    user_id: str
    name: str
    age: int
    gender: str
    height: float
    weight: float
    activity_level: str
    
    # 偏好和限制
    taste_preferences: Dict[str, int] = None
    dietary_preferences: List[str] = None
    allergies: List[str] = None
    dislikes: List[str] = None
    
    # 生理信息
    is_female: bool = False
    menstrual_cycle_length: Optional[int] = None
    last_period_date: Optional[str] = None
    
    # 个性化因素
    zodiac_sign: Optional[str] = None
    personality_traits: List[str] = None
    health_goals: List[str] = None
    
    def __post_init__(self):
        if self.taste_preferences is None:
            self.taste_preferences = {}
        if self.dietary_preferences is None:
            self.dietary_preferences = []
        if self.allergies is None:
            self.allergies = []
        if self.dislikes is None:
            self.dislikes = []
        if self.personality_traits is None:
            self.personality_traits = []
        if self.health_goals is None:
            self.health_goals = []


@dataclass
class MealRecord:
    """餐食记录 - 统一数据结构"""
    user_id: str
    date: str
    meal_type: str  # breakfast, lunch, dinner
    foods: List[str]
    quantities: List[str]
    calories: Optional[float] = None
    satisfaction_score: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class RecommendationResult:
    """推荐结果 - 统一数据结构"""
    user_id: str
    date: str
    meal_type: str
    recommended_foods: List[str]
    reasoning: str
    confidence_score: float
    special_considerations: List[str] = None
    
    def __post_init__(self):
        if self.special_considerations is None:
            self.special_considerations = []


class BaseEngine(ABC):
    """基础引擎抽象类 - 所有功能模块的基座"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化引擎"""
        pass
    
    @abstractmethod
    async def process(self, data: Any) -> Any:
        """处理数据"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> bool:
        """清理资源"""
        pass
    
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置"""
        return self.config.get(key, default)


class DataManager(BaseEngine):
    """数据管理基座 - 统一的数据存储和访问接口"""
    
    def __init__(self, db_path: str = "data/app.db"):
        super().__init__()
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self) -> bool:
        """初始化数据库"""
        try:
            await self._create_tables()
            self._initialized = True
            self.logger.info("数据管理器初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"数据管理器初始化失败: {e}")
            return False
    
    async def _create_tables(self):
        """创建数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                profile_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 餐食记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                date TEXT,
                meal_type TEXT,
                foods TEXT,
                quantities TEXT,
                calories REAL,
                satisfaction_score INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 推荐记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                date TEXT,
                meal_type TEXT,
                recommended_foods TEXT,
                reasoning TEXT,
                confidence_score REAL,
                special_considerations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 用户反馈表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                date TEXT,
                recommendation_id INTEGER,
                user_choice TEXT,
                feedback_type TEXT,
                satisfaction_score INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (recommendation_id) REFERENCES recommendations (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def process(self, operation: str, data: Any) -> Any:
        """处理数据操作"""
        if not self._initialized:
            await self.initialize()
        
        operations = {
            'save_user': self._save_user_profile,
            'get_user': self._get_user_profile,
            'save_meal': self._save_meal_record,
            'get_meals': self._get_meal_records,
            'save_recommendation': self._save_recommendation,
            'get_recommendations': self._get_recommendations,
            'save_feedback': self._save_feedback,
            'get_feedback': self._get_feedback
        }
        
        if operation in operations:
            return await operations[operation](data)
        else:
            raise ValueError(f"不支持的操作: {operation}")
    
    async def _save_user_profile(self, profile: UserProfile) -> bool:
        """保存用户画像"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, profile_data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (profile.user_id, json.dumps(asdict(profile))))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"保存用户画像失败: {e}")
            return False
    
    async def _get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """获取用户画像"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT profile_data FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                profile_dict = json.loads(result[0])
                return UserProfile(**profile_dict)
            return None
        except Exception as e:
            self.logger.error(f"获取用户画像失败: {e}")
            return None
    
    async def _save_meal_record(self, meal: MealRecord) -> bool:
        """保存餐食记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO meals (user_id, date, meal_type, foods, quantities, 
                                 calories, satisfaction_score, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                meal.user_id, meal.date, meal.meal_type,
                json.dumps(meal.foods), json.dumps(meal.quantities),
                meal.calories, meal.satisfaction_score, meal.notes
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"保存餐食记录失败: {e}")
            return False
    
    async def _get_meal_records(self, params: Dict[str, Any]) -> List[MealRecord]:
        """获取餐食记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            user_id = params.get('user_id')
            days = params.get('days', 5)
            
            cursor.execute('''
                SELECT user_id, date, meal_type, foods, quantities, calories, 
                       satisfaction_score, notes
                FROM meals 
                WHERE user_id = ? 
                ORDER BY date DESC, meal_type
                LIMIT ?
            ''', (user_id, days * 3))
            
            results = cursor.fetchall()
            conn.close()
            
            meals = []
            for row in results:
                meal = MealRecord(
                    user_id=row[0],
                    date=row[1],
                    meal_type=row[2],
                    foods=json.loads(row[3]),
                    quantities=json.loads(row[4]),
                    calories=row[5],
                    satisfaction_score=row[6],
                    notes=row[7]
                )
                meals.append(meal)
            
            return meals
        except Exception as e:
            self.logger.error(f"获取餐食记录失败: {e}")
            return []
    
    async def _save_recommendation(self, recommendation: RecommendationResult) -> int:
        """保存推荐结果"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO recommendations (user_id, date, meal_type, recommended_foods,
                                           reasoning, confidence_score, special_considerations)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                recommendation.user_id, recommendation.date, recommendation.meal_type,
                json.dumps(recommendation.recommended_foods), recommendation.reasoning,
                recommendation.confidence_score, json.dumps(recommendation.special_considerations)
            ))
            
            recommendation_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return recommendation_id
        except Exception as e:
            self.logger.error(f"保存推荐结果失败: {e}")
            return -1
    
    async def _get_recommendations(self, params: Dict[str, Any]) -> List[RecommendationResult]:
        """获取推荐记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            user_id = params.get('user_id')
            days = params.get('days', 7)
            
            cursor.execute('''
                SELECT user_id, date, meal_type, recommended_foods, reasoning,
                       confidence_score, special_considerations
                FROM recommendations 
                WHERE user_id = ? 
                ORDER BY date DESC
                LIMIT ?
            ''', (user_id, days))
            
            results = cursor.fetchall()
            conn.close()
            
            recommendations = []
            for row in results:
                rec = RecommendationResult(
                    user_id=row[0],
                    date=row[1],
                    meal_type=row[2],
                    recommended_foods=json.loads(row[3]),
                    reasoning=row[4],
                    confidence_score=row[5],
                    special_considerations=json.loads(row[6]) if row[6] else []
                )
                recommendations.append(rec)
            
            return recommendations
        except Exception as e:
            self.logger.error(f"获取推荐记录失败: {e}")
            return []
    
    async def _save_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """保存用户反馈"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO feedback (user_id, date, recommendation_id, user_choice,
                                    feedback_type, satisfaction_score, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback_data['user_id'], feedback_data['date'], 
                feedback_data.get('recommendation_id'), feedback_data['user_choice'],
                feedback_data['feedback_type'], feedback_data.get('satisfaction_score'),
                feedback_data.get('notes')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"保存用户反馈失败: {e}")
            return False
    
    async def _get_feedback(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取用户反馈"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            user_id = params.get('user_id')
            days = params.get('days', 7)
            
            cursor.execute('''
                SELECT user_id, date, recommendation_id, user_choice, feedback_type,
                       satisfaction_score, notes
                FROM feedback 
                WHERE user_id = ? 
                ORDER BY date DESC
                LIMIT ?
            ''', (user_id, days))
            
            results = cursor.fetchall()
            conn.close()
            
            feedbacks = []
            for row in results:
                feedback = {
                    'user_id': row[0],
                    'date': row[1],
                    'recommendation_id': row[2],
                    'user_choice': row[3],
                    'feedback_type': row[4],
                    'satisfaction_score': row[5],
                    'notes': row[6]
                }
                feedbacks.append(feedback)
            
            return feedbacks
        except Exception as e:
            self.logger.error(f"获取用户反馈失败: {e}")
            return []
    
    async def cleanup(self) -> bool:
        """清理资源"""
        self._initialized = False
        return True


class AIAnalyzer(BaseEngine):
    """AI分析基座 - 统一的大模型分析接口"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.openai_client = None
        self.anthropic_client = None
    
    async def initialize(self) -> bool:
        """初始化AI客户端"""
        try:
            import openai
            import anthropic
            
            self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            
            self._initialized = True
            self.logger.info("AI分析器初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"AI分析器初始化失败: {e}")
            return False
    
    async def process(self, analysis_type: str, data: Any) -> Any:
        """处理AI分析请求"""
        if not self._initialized:
            await self.initialize()
        
        analysis_types = {
            'user_intent': self._analyze_user_intent,
            'physiological_state': self._analyze_physiological_state,
            'nutrition_analysis': self._analyze_nutrition,
            'recommendation_reasoning': self._generate_reasoning
        }
        
        if analysis_type in analysis_types:
            return await analysis_types[analysis_type](data)
        else:
            raise ValueError(f"不支持的分析类型: {analysis_type}")
    
    async def _analyze_user_intent(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户意图"""
        user_input = data.get('user_input', '')
        context = data.get('context', {})
        
        prompt = f"""
请分析用户的真实意图和需求：

用户输入: "{user_input}"
用户背景: {json.dumps(context, ensure_ascii=False)}

请分析：
1. 真实意图
2. 情绪状态
3. 营养需求
4. 推荐理由

返回JSON格式结果。
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是专业的营养师和心理分析师。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content
            return self._parse_json_result(result_text)
        except Exception as e:
            self.logger.error(f"用户意图分析失败: {e}")
            return {"intent": "需要饮食建议", "confidence": 0.3}
    
    async def _analyze_physiological_state(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析生理状态"""
        profile = data.get('profile', {})
        current_date = data.get('current_date', '')
        
        if not profile.get('is_female', False):
            return {"state": "normal", "needs": []}
        
        # 计算生理周期
        cycle_info = self._calculate_cycle_state(profile, current_date)
        
        prompt = f"""
作为女性健康专家，分析用户的生理状态：

用户信息: {json.dumps(profile, ensure_ascii=False)}
当前日期: {current_date}
生理周期: {json.dumps(cycle_info, ensure_ascii=False)}

请分析营养需求和饮食建议。
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是专业的女性健康专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=400
            )
            
            result_text = response.choices[0].message.content
            result = self._parse_json_result(result_text)
            result['cycle_info'] = cycle_info
            return result
        except Exception as e:
            self.logger.error(f"生理状态分析失败: {e}")
            return {"state": "normal", "needs": [], "cycle_info": cycle_info}
    
    async def _analyze_nutrition(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """营养分析"""
        foods = data.get('foods', [])
        quantities = data.get('quantities', [])
        
        prompt = f"""
请分析以下食物的营养成分：

食物: {', '.join(foods)}
数量: {', '.join(quantities)}

请分析：
1. 总热量
2. 主要营养素
3. 营养均衡性
4. 改进建议

返回JSON格式结果。
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是专业的营养师。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=400
            )
            
            result_text = response.choices[0].message.content
            return self._parse_json_result(result_text)
        except Exception as e:
            self.logger.error(f"营养分析失败: {e}")
            return {"calories": 0, "analysis": "分析失败"}
    
    async def _generate_reasoning(self, data: Dict[str, Any]) -> str:
        """生成推荐理由"""
        recommendations = data.get('recommendations', [])
        user_profile = data.get('user_profile', {})
        
        prompt = f"""
请为以下推荐生成个性化理由：

推荐食物: {', '.join(recommendations)}
用户画像: {json.dumps(user_profile, ensure_ascii=False)}

请生成简洁明了的推荐理由。
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是专业的营养师。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"生成推荐理由失败: {e}")
            return "基于您的个人偏好和营养需求推荐"
    
    def _calculate_cycle_state(self, profile: Dict[str, Any], current_date: str) -> Dict[str, Any]:
        """计算生理周期状态"""
        try:
            last_period = datetime.strptime(profile.get('last_period_date', ''), '%Y-%m-%d')
            current = datetime.strptime(current_date, '%Y-%m-%d')
            cycle_length = profile.get('menstrual_cycle_length', 28)
            
            days_since_period = (current - last_period).days
            days_to_next_period = cycle_length - (days_since_period % cycle_length)
            
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
                "is_ovulation": phase == "排卵期"
            }
        except Exception:
            return {
                "phase": "未知",
                "days_since_period": 0,
                "days_to_next_period": 0,
                "is_ovulation": False
            }
    
    def _parse_json_result(self, text: str) -> Dict[str, Any]:
        """解析JSON结果"""
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"解析JSON结果失败: {e}")
        
        return {}
    
    async def cleanup(self) -> bool:
        """清理资源"""
        self._initialized = False
        return True


class RecommendationEngine(BaseEngine):
    """推荐引擎基座 - 统一的推荐算法接口"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.data_manager = None
        self.ai_analyzer = None
        self.food_database = {}
    
    async def initialize(self) -> bool:
        """初始化推荐引擎"""
        try:
            # 初始化依赖组件
            self.data_manager = DataManager()
            await self.data_manager.initialize()
            
            self.ai_analyzer = AIAnalyzer()
            await self.ai_analyzer.initialize()
            
            # 加载食物数据库
            await self._load_food_database()
            
            self._initialized = True
            self.logger.info("推荐引擎初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"推荐引擎初始化失败: {e}")
            return False
    
    async def process(self, request_type: str, data: Any) -> Any:
        """处理推荐请求"""
        if not self._initialized:
            await self.initialize()
        
        request_types = {
            'generate_recommendation': self._generate_recommendation,
            'update_model': self._update_model,
            'get_food_info': self._get_food_info
        }
        
        if request_type in request_types:
            return await request_types[request_type](data)
        else:
            raise ValueError(f"不支持的请求类型: {request_type}")
    
    async def _generate_recommendation(self, data: Dict[str, Any]) -> RecommendationResult:
        """生成推荐"""
        user_id = data.get('user_id')
        user_input = data.get('user_input', '')
        current_date = data.get('current_date', datetime.now().strftime('%Y-%m-%d'))
        meal_type = data.get('meal_type', 'lunch')
        
        # 获取用户数据
        user_profile = await self.data_manager.process('get_user', user_id)
        meal_history = await self.data_manager.process('get_meals', {'user_id': user_id, 'days': 5})
        
        if not user_profile:
            raise ValueError(f"用户 {user_id} 不存在")
        
        # AI分析用户意图
        intent_analysis = await self.ai_analyzer.process('user_intent', {
            'user_input': user_input,
            'context': asdict(user_profile)
        })
        
        # AI分析生理状态
        physiological_analysis = await self.ai_analyzer.process('physiological_state', {
            'profile': asdict(user_profile),
            'current_date': current_date
        })
        
        # 生成推荐食物
        recommended_foods = await self._select_foods(
            user_profile, intent_analysis, physiological_analysis
        )
        
        # 生成推荐理由
        reasoning = await self.ai_analyzer.process('recommendation_reasoning', {
            'recommendations': recommended_foods,
            'user_profile': asdict(user_profile)
        })
        
        # 创建推荐结果
        recommendation = RecommendationResult(
            user_id=user_id,
            date=current_date,
            meal_type=meal_type,
            recommended_foods=recommended_foods,
            reasoning=reasoning,
            confidence_score=intent_analysis.get('confidence', 0.5),
            special_considerations=physiological_analysis.get('considerations', [])
        )
        
        # 保存推荐结果
        await self.data_manager.process('save_recommendation', recommendation)
        
        return recommendation
    
    async def _select_foods(self, user_profile: UserProfile, 
                          intent_analysis: Dict[str, Any],
                          physiological_analysis: Dict[str, Any]) -> List[str]:
        """选择推荐食物"""
        
        # 基础食物池
        base_foods = [
            "米饭", "面条", "馒头", "包子", "饺子",
            "鸡蛋", "豆腐", "鱼肉", "鸡肉", "瘦肉",
            "青菜", "西红柿", "胡萝卜", "土豆", "西兰花",
            "苹果", "香蕉", "橙子", "葡萄", "草莓",
            "牛奶", "酸奶", "豆浆", "坚果", "红枣"
        ]
        
        # 根据用户偏好过滤
        filtered_foods = []
        for food in base_foods:
            if not any(dislike in food for dislike in user_profile.dislikes):
                if not any(allergy in food for allergy in user_profile.allergies):
                    filtered_foods.append(food)
        
        # 根据生理需求调整
        physiological_needs = physiological_analysis.get('needs', [])
        priority_foods = []
        
        for need in physiological_needs:
            if need == "铁质":
                priority_foods.extend(["菠菜", "瘦肉", "红枣"])
            elif need == "蛋白质":
                priority_foods.extend(["鸡蛋", "豆腐", "鱼肉"])
            elif need == "维生素C":
                priority_foods.extend(["橙子", "柠檬", "西红柿"])
        
        # 合并推荐
        recommended = list(set(priority_foods + filtered_foods))[:5]
        
        return recommended
    
    async def _update_model(self, data: Dict[str, Any]) -> bool:
        """更新模型"""
        # 这里可以实现机器学习模型的更新逻辑
        user_id = data.get('user_id')
        feedback_data = await self.data_manager.process('get_feedback', {'user_id': user_id, 'days': 30})
        
        # 基于反馈数据更新推荐策略
        self.logger.info(f"更新用户 {user_id} 的推荐模型")
        return True
    
    async def _get_food_info(self, food_name: str) -> Dict[str, Any]:
        """获取食物信息"""
        return self.food_database.get(food_name, {})
    
    async def _load_food_database(self):
        """加载食物数据库"""
        # 这里可以从文件或API加载食物营养信息
        self.food_database = {
            "米饭": {"calories": 130, "protein": 2.7, "carbs": 28},
            "鸡蛋": {"calories": 155, "protein": 13, "fat": 11},
            "豆腐": {"calories": 76, "protein": 8, "carbs": 2},
            # 更多食物数据...
        }
    
    async def cleanup(self) -> bool:
        """清理资源"""
        if self.data_manager:
            await self.data_manager.cleanup()
        if self.ai_analyzer:
            await self.ai_analyzer.cleanup()
        self._initialized = False
        return True


if __name__ == "__main__":
    # 测试基座架构
    async def test_base_engine():
        print("测试基座架构...")
        
        # 测试数据管理器
        data_manager = DataManager()
        await data_manager.initialize()
        
        # 创建测试用户
        test_user = UserProfile(
            user_id="test_001",
            name="测试用户",
            age=25,
            gender="女",
            height=165.0,
            weight=55.0,
            activity_level="moderate",
            taste_preferences={"sweet": 4, "salty": 3},
            is_female=True,
            zodiac_sign="天秤座"
        )
        
        # 保存用户
        await data_manager.process('save_user', test_user)
        print("用户保存成功")
        
        # 获取用户
        retrieved_user = await data_manager.process('get_user', "test_001")
        if retrieved_user:
            print(f"获取用户: {retrieved_user.name}")
        
        # 测试推荐引擎
        rec_engine = RecommendationEngine()
        await rec_engine.initialize()
        
        # 生成推荐
        recommendation = await rec_engine.process('generate_recommendation', {
            'user_id': 'test_001',
            'user_input': '我今天想吃点清淡的',
            'meal_type': 'lunch'
        })
        
        print(f"推荐结果: {recommendation.recommended_foods}")
        print(f"推荐理由: {recommendation.reasoning}")
        
        # 清理资源
        await data_manager.cleanup()
        await rec_engine.cleanup()
        print("测试完成")
    
    # 运行测试
    asyncio.run(test_base_engine())
