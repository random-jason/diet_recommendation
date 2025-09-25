"""
推荐引擎模块 - 基于基座架构
结合机器学习和AI分析的混合推荐系统
"""

from typing import Dict, List, Optional, Any, Tuple
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta
from core.base import BaseModule, ModuleType, UserData, AnalysisResult, BaseConfig
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class RecommendationEngine(BaseModule):
    """推荐引擎模块"""
    
    def __init__(self, config: BaseConfig):
        super().__init__(config, ModuleType.RECOMMENDATION)
        self.model_path = Path(config.model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # 推荐模型组件
        self.tfidf_vectorizer = None
        self.user_clustering_model = None
        self.food_similarity_matrix = None
        self.user_preference_model = None
        
        # 食物数据库
        self.food_database = self._load_food_database()
        
        # 餐食搭配模板
        self.meal_templates = self._load_meal_templates()
        
        # 推荐配置
        self.max_recommendations = config.max_recommendations
        self.min_training_samples = config.min_training_samples
        self.model_update_threshold = config.model_update_threshold
    
    def initialize(self) -> bool:
        """初始化推荐引擎"""
        try:
            self.logger.info("推荐引擎初始化中...")
            
            # 加载或训练模型
            self._load_or_train_models()
            
            self.is_initialized = True
            self.logger.info("推荐引擎初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"推荐引擎初始化失败: {e}")
            return False
    
    def process(self, input_data: Any, user_data: UserData) -> AnalysisResult:
        """处理推荐请求"""
        try:
            recommendation_type = input_data.get('type', 'meal_recommendation')
            
            if recommendation_type == 'meal_recommendation':
                result = self._generate_meal_recommendations(input_data, user_data)
            elif recommendation_type == 'food_similarity':
                result = self._find_similar_foods(input_data, user_data)
            elif recommendation_type == 'preference_update':
                result = self._update_user_preferences(input_data, user_data)
            elif recommendation_type == 'model_retrain':
                result = self._retrain_models(input_data, user_data)
            else:
                result = self._create_error_result("未知的推荐类型")
            
            return AnalysisResult(
                module_type=self.module_type,
                user_id=user_data.user_id,
                input_data=input_data,
                result=result,
                confidence=result.get('confidence', 0.5)
            )
        except Exception as e:
            self.logger.error(f"处理推荐请求失败: {e}")
            return self._create_error_result(str(e))
    
    def _generate_meal_recommendations(self, input_data: Dict, user_data: UserData) -> Dict[str, Any]:
        """生成餐食推荐"""
        meal_type = input_data.get('meal_type', 'lunch')
        preferences = input_data.get('preferences', {})
        context = input_data.get('context', {})
        
        try:
            # 生成完整餐食搭配推荐
            meal_combinations = self._generate_meal_combinations(user_data, meal_type, preferences, context)
            
            return {
                'success': True,
                'recommendations': meal_combinations,
                'reasoning': self._generate_meal_reasoning(meal_combinations, user_data, meal_type),
                'confidence': self._calculate_recommendation_confidence(user_data),
                'metadata': {
                    'meal_type': meal_type,
                    'combination_count': len(meal_combinations)
                }
            }
            
        except Exception as e:
            self.logger.error(f"生成餐食推荐失败: {e}")
            return self._create_error_result(f"推荐生成失败: {str(e)}")
    
    def _generate_meal_combinations(self, user_data: UserData, meal_type: str, 
                                 preferences: Dict, context: Dict) -> List[Dict[str, Any]]:
        """生成基于用户数据的动态餐食搭配组合"""
        combinations = []
        
        try:
            # 1. 基于用户历史数据生成搭配
            historical_combinations = self._generate_historical_combinations(user_data, meal_type)
            combinations.extend(historical_combinations)
            
            # 2. 基于用户偏好生成个性化搭配
            personalized_combinations = self._generate_personalized_combinations(user_data, meal_type, preferences)
            combinations.extend(personalized_combinations)
            
            # 3. 基于相似用户生成搭配
            similar_user_combinations = self._generate_similar_user_combinations(user_data, meal_type)
            combinations.extend(similar_user_combinations)
            
            # 4. 如果没有足够数据，使用模板生成
            if len(combinations) < 3:
                template_combinations = self._generate_template_combinations(user_data, meal_type)
                combinations.extend(template_combinations)
            
            # 5. 去重和排序
            combinations = self._deduplicate_and_rank_combinations(combinations, user_data)
            
            # 6. 确保至少有一些推荐
            if not combinations:
                combinations = self._generate_fallback_combinations(meal_type)
            
            return combinations[:5]  # 返回前5个最佳搭配
            
        except Exception as e:
            self.logger.error(f"生成餐食搭配失败: {e}")
            # 返回基础推荐
            return self._generate_fallback_combinations(meal_type)

    def _generate_historical_combinations(self, user_data: UserData, meal_type: str) -> List[Dict[str, Any]]:
        """基于用户历史数据生成搭配"""
        combinations = []
        
        # 获取该餐次的所有历史记录
        meal_records = [meal for meal in user_data.meals if meal.get('meal_type') == meal_type]
        
        if not meal_records:
            return combinations
        
        # 分析高频搭配
        food_combinations = {}
        for meal in meal_records:
            foods = meal.get('foods', [])
            if len(foods) >= 2 and meal.get('satisfaction_score', 0) >= 4:
                # 生成2-3食物组合
                for i in range(len(foods)):
                    for j in range(i+1, min(i+3, len(foods))):
                        combo = tuple(sorted(foods[i:j+1]))
                        food_combinations[combo] = food_combinations.get(combo, 0) + 1
        
        # 选择出现频率最高的搭配
        sorted_combinations = sorted(food_combinations.items(), key=lambda x: x[1], reverse=True)
        
        for combo, count in sorted_combinations[:2]:  # 取前2个高频搭配
            if count >= 2:  # 至少出现2次
                combination = {
                    "name": f"历史搭配{len(combinations)+1}",
                    "description": f"基于您{meal_type}的历史偏好",
                    "foods": [],
                    "total_calories": 0,
                    "nutrition_score": 0,
                    "personalization_score": 1.0,
                    "categories": ["历史数据"],
                    "source": "historical"
                }
                
                for food_name in combo:
                    food_info = self._get_food_info(food_name)
                    if food_info:
                        combination["foods"].append(food_info)
                        combination["total_calories"] += food_info.get("calories", 0)
                
                if len(combination["foods"]) >= 2:
                    combination["nutrition_score"] = self._calculate_nutrition_score(combination["foods"])
                    combinations.append(combination)
        
        return combinations

    def _generate_personalized_combinations(self, user_data: UserData, meal_type: str, preferences: Dict) -> List[Dict[str, Any]]:
        """基于用户偏好生成个性化搭配"""
        combinations = []
        
        # 获取用户喜爱的食物
        favorite_foods = self._get_user_favorite_foods(user_data, meal_type)
        
        if len(favorite_foods) >= 2:
            combination = {
                "name": "个性化搭配",
                "description": f"基于您的{meal_type}偏好定制",
                "foods": [],
                "total_calories": 0,
                "nutrition_score": 0,
                "personalization_score": 0.9,
                "categories": ["个性化"],
                "source": "personalized"
            }
            
            # 选择2-4种用户喜爱的食物
            selected_foods = favorite_foods[:min(4, len(favorite_foods))]
            for food in selected_foods:
                food_info = self._get_food_info(food)
                if food_info:
                    combination["foods"].append(food_info)
                    combination["total_calories"] += food_info.get("calories", 0)
            
            if len(combination["foods"]) >= 2:
                combination["nutrition_score"] = self._calculate_nutrition_score(combination["foods"])
                combinations.append(combination)
        
        return combinations

    def _generate_similar_user_combinations(self, user_data: UserData, meal_type: str) -> List[Dict[str, Any]]:
        """基于相似用户生成搭配"""
        return []  # 暂时返回空列表

    def _generate_template_combinations(self, user_data: UserData, meal_type: str) -> List[Dict[str, Any]]:
        """基于模板生成搭配（当历史数据不足时）"""
        combinations = []
        
        templates = self.meal_templates.get(meal_type, [])
        
        for template in templates[:2]:  # 只使用前2个模板
            combination = {
                "name": template["name"],
                "description": f"营养均衡的{meal_type}搭配",
                "foods": [],
                "total_calories": 0,
                "nutrition_score": 0,
                "personalization_score": 0.3,
                "categories": template["categories"],
                "source": "template"
            }
            
            # 为每个类别选择常见食物
            for category in template["categories"]:
                food = self._select_common_food_for_category(category, meal_type)
                if food:
                    combination["foods"].append(food)
                    combination["total_calories"] += food.get("calories", 0)
            
            if len(combination["foods"]) >= 2:
                combination["nutrition_score"] = self._calculate_nutrition_score(combination["foods"])
                combinations.append(combination)
        
        return combinations

    def _select_common_food_for_category(self, category: str, meal_type: str) -> Dict[str, Any]:
        """为特定类别选择常见食物"""
        common_foods = {
            "主食": ["米饭", "面条", "面包", "粥"],
            "蛋白质": ["鸡蛋", "鸡肉", "牛肉", "豆腐"],
            "蔬菜": ["青菜", "白菜", "西红柿"],
            "饮品": ["牛奶", "酸奶", "汤"],
            "水果": ["苹果", "香蕉"],
            "坚果": ["坚果"],
            "小食": ["饼干"]
        }
        
        foods = common_foods.get(category, [])
        if foods:
            # 根据餐次选择合适的主食
            if category == "主食" and meal_type == "breakfast":
                food_name = "面包" if "面包" in foods else foods[0]
            elif category == "主食" and meal_type == "lunch":
                food_name = "米饭" if "米饭" in foods else foods[0]
            elif category == "主食" and meal_type == "dinner":
                food_name = "粥" if "粥" in foods else foods[0]
            else:
                food_name = foods[0]
            
            return self._get_food_info(food_name)
        
        return None

    def _deduplicate_and_rank_combinations(self, combinations: List[Dict], user_data: UserData) -> List[Dict]:
        """去重和排序搭配组合"""
        # 去重：基于食物组合去重
        unique_combinations = []
        seen_combinations = set()
        
        for combo in combinations:
            food_names = tuple(sorted([f["name"] for f in combo["foods"]]))
            if food_names not in seen_combinations:
                seen_combinations.add(food_names)
                unique_combinations.append(combo)
        
        # 排序：综合得分
        def score_combination(combo):
            personal_score = combo.get("personalization_score", 0) * 0.4
            nutrition_score = combo.get("nutrition_score", 0) * 0.3
            satisfaction_score = sum(f.get("satisfaction_score", 4) for f in combo["foods"]) / len(combo["foods"]) * 0.3
            return personal_score + nutrition_score + satisfaction_score
        
        return sorted(unique_combinations, key=score_combination, reverse=True)

    def _generate_meal_reasoning(self, combinations: List[Dict], user_data: UserData, meal_type: str) -> str:
        """生成动态餐食推荐理由"""
        if not combinations:
            return "暂无推荐"
        
        top_combination = combinations[0]
        foods = top_combination["foods"]
        
        reasoning_parts = []
        
        # 基于数据来源生成理由
        source = top_combination.get("source", "unknown")
        if source == "historical":
            reasoning_parts.append("基于您的历史用餐偏好")
        elif source == "personalized":
            reasoning_parts.append("基于您的个人喜好")
        elif source == "template":
            reasoning_parts.append("营养均衡搭配")
        
        # 满意度理由
        avg_satisfaction = sum(f.get("satisfaction_score", 4) for f in foods) / len(foods)
        if avg_satisfaction > 4.0:
            reasoning_parts.append(f"历史满意度: {avg_satisfaction:.1f}分")
        
        # 食物搭配理由
        food_names = [f["name"] for f in foods]
        reasoning_parts.append(f"推荐搭配: {', '.join(food_names)}")
        
        return "，".join(reasoning_parts) if reasoning_parts else "营养搭配推荐"

    def _get_user_favorite_foods(self, user_data: UserData, meal_type: str) -> List[str]:
        """获取用户喜爱的食物"""
        favorite_foods = []
        
        # 从历史餐食记录中提取
        for meal in user_data.meals:
            if meal.get('meal_type') == meal_type and meal.get('satisfaction_score', 0) >= 4:
                favorite_foods.extend(meal.get('foods', []))
        
        # 统计频率
        food_counts = {}
        for food in favorite_foods:
            food_counts[food] = food_counts.get(food, 0) + 1
        
        # 按频率排序
        sorted_foods = sorted(food_counts.items(), key=lambda x: x[1], reverse=True)
        return [food for food, count in sorted_foods[:10]]

    def _get_food_info(self, food_name: str) -> Dict[str, Any]:
        """获取食物信息"""
        # 从食物数据库获取信息
        food_info = self.food_database.get(food_name, {})
        return {
            "name": food_name,
            "calories": food_info.get("calories", 100),
            "category": food_info.get("category", "其他"),
            "nutrition": food_info.get("nutrition", {}),
            "satisfaction_score": food_info.get("avg_satisfaction", 4.0)
        }

    def _calculate_nutrition_score(self, foods: List[Dict]) -> float:
        """计算营养得分"""
        if not foods:
            return 0.0
        
        # 简单的营养评分逻辑
        score = 0.0
        categories = set()
        
        for food in foods:
            category = food.get("category", "其他")
            categories.add(category)
            score += food.get("satisfaction_score", 4.0)
        
        # 多样性加分
        diversity_bonus = min(len(categories) * 0.1, 0.3)
        
        return (score / len(foods)) + diversity_bonus

    def _generate_fallback_combinations(self, meal_type: str) -> List[Dict[str, Any]]:
        """生成备选推荐（当其他方法都失败时）"""
        combinations = []
        
        # 基础推荐搭配
        fallback_combinations = {
            "breakfast": [
                {"name": "营养早餐", "foods": ["面包", "鸡蛋", "牛奶"]},
                {"name": "健康早餐", "foods": ["燕麦粥", "香蕉", "酸奶"]}
            ],
            "lunch": [
                {"name": "均衡午餐", "foods": ["米饭", "鸡肉", "青菜"]},
                {"name": "轻食午餐", "foods": ["面条", "牛肉", "西红柿"]}
            ],
            "dinner": [
                {"name": "清淡晚餐", "foods": ["粥", "豆腐", "白菜"]},
                {"name": "温馨晚餐", "foods": ["饺子", "汤"]}
            ],
            "snack": [
                {"name": "健康小食", "foods": ["苹果", "坚果"]},
                {"name": "休闲小食", "foods": ["酸奶", "饼干"]}
            ]
        }
        
        templates = fallback_combinations.get(meal_type, [])
        
        for template in templates:
            combination = {
                "name": template["name"],
                "description": f"营养均衡的{meal_type}搭配",
                "foods": [],
                "total_calories": 0,
                "nutrition_score": 4.0,
                "personalization_score": 0.2,
                "categories": ["基础推荐"],
                "source": "fallback"
            }
            
            for food_name in template["foods"]:
                food_info = self._get_food_info(food_name)
                if food_info:
                    combination["foods"].append(food_info)
                    combination["total_calories"] += food_info.get("calories", 0)
            
            if len(combination["foods"]) >= 2:
                combinations.append(combination)
        
        return combinations

    def _get_historical_recommendations(self, user_data: UserData, meal_type: str) -> List[Dict[str, Any]]:
        """基于历史数据的推荐"""
        recommendations = []
        
        # 分析用户历史餐食
        historical_meals = [meal for meal in user_data.meals if meal.get('meal_type') == meal_type]
        
        if not historical_meals:
            return recommendations
        
        # 统计用户喜欢的食物
        food_scores = {}
        for meal in historical_meals:
            satisfaction = meal.get('satisfaction_score', 3)  # 默认3分
            for food in meal.get('foods', []):
                if food not in food_scores:
                    food_scores[food] = []
                food_scores[food].append(satisfaction)
        
        # 计算平均满意度
        for food, scores in food_scores.items():
            avg_score = np.mean(scores)
            if avg_score >= 3:  # 只推荐满意度>=3的食物
                recommendations.append({
                    'food': food,
                    'score': avg_score,
                    'type': 'historical',
                    'reason': f'历史满意度: {avg_score:.1f}分'
                })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)
    
    def _get_similar_user_recommendations(self, user_data: UserData, meal_type: str) -> List[Dict[str, Any]]:
        """基于相似用户的推荐"""
        recommendations = []
        
        if not self.user_clustering_model:
            return recommendations
        
        try:
            # 获取用户特征向量
            user_features = self._extract_user_features(user_data)
            
            # 找到相似用户
            similar_users = self._find_similar_users(user_features)
            
            # 基于相似用户的偏好推荐
            for similar_user_id in similar_users:
                similar_user_data = self._get_user_data_by_id(similar_user_id)
                if similar_user_data:
                    user_recommendations = self._get_historical_recommendations(similar_user_data, meal_type)
                    for rec in user_recommendations:
                        rec['type'] = 'similar_user'
                        rec['reason'] = f'相似用户推荐'
                        recommendations.append(rec)
            
        except Exception as e:
            self.logger.error(f"相似用户推荐失败: {e}")
        
        return recommendations
    
    def _get_content_based_recommendations(self, user_data: UserData, meal_type: str) -> List[Dict[str, Any]]:
        """基于内容相似性的推荐"""
        recommendations = []
        
        if not self.food_similarity_matrix:
            return recommendations
        
        try:
            # 获取用户喜欢的食物
            liked_foods = []
            for meal in user_data.meals:
                if meal.get('satisfaction_score', 0) >= 4:  # 满意度>=4的食物
                    liked_foods.extend(meal.get('foods', []))
            
            if not liked_foods:
                return recommendations
            
            # 基于食物相似性推荐
            for liked_food in liked_foods:
                if liked_food in self.food_similarity_matrix:
                    similar_foods = self.food_similarity_matrix[liked_food]
                    for food, similarity in similar_foods.items():
                        if food not in liked_foods:  # 避免重复推荐
                            recommendations.append({
                                'food': food,
                                'score': similarity,
                                'type': 'content_based',
                                'reason': f'与{liked_food}相似'
                            })
            
        except Exception as e:
            self.logger.error(f"内容推荐失败: {e}")
        
        return recommendations
    
    def _get_physiological_recommendations(self, user_data: UserData, context: Dict) -> List[Dict[str, Any]]:
        """基于生理状态的推荐"""
        recommendations = []
        
        # 获取生理状态信息
        physiological_state = context.get('physiological_state', {})
        needs = physiological_state.get('needs', [])
        
        if not needs:
            return recommendations
        
        # 根据营养需求推荐食物
        nutrition_food_mapping = {
            '铁质': ['菠菜', '瘦肉', '红枣', '黑芝麻', '猪肝'],
            '蛋白质': ['鸡蛋', '豆腐', '鱼肉', '鸡肉', '牛奶'],
            '维生素C': ['橙子', '柠檬', '西红柿', '西兰花', '草莓'],
            '叶酸': ['绿叶蔬菜', '豆类', '坚果', '菠菜', '芦笋'],
            '维生素B': ['全谷物', '瘦肉', '蛋类', '香蕉', '土豆'],
            '锌': ['牡蛎', '瘦肉', '坚果', '豆类', '南瓜子'],
            '维生素E': ['坚果', '植物油', '鳄梨', '葵花籽', '杏仁'],
            '镁': ['坚果', '绿叶蔬菜', '全谷物', '黑巧克力', '香蕉'],
            '维生素B6': ['香蕉', '土豆', '鸡肉', '三文鱼', '鹰嘴豆'],
            '钙质': ['牛奶', '豆腐', '绿叶蔬菜', '奶酪', '酸奶']
        }
        
        for need in needs:
            foods = nutrition_food_mapping.get(need, [])
            for food in foods:
                recommendations.append({
                    'food': food,
                    'score': 0.8,  # 生理需求推荐分数较高
                    'type': 'physiological',
                    'reason': f'补充{need}'
                })
        
        return recommendations
    
    def _fuse_recommendations(self, recommendation_lists: List[List[Dict]], user_data: UserData) -> List[Dict[str, Any]]:
        """融合多种推荐结果"""
        food_scores = {}
        
        # 权重配置
        weights = {
            'historical': 0.4,
            'similar_user': 0.2,
            'content_based': 0.2,
            'physiological': 0.2
        }
        
        for rec_list in recommendation_lists:
            for rec in rec_list:
                food = rec['food']
                score = rec['score']
                rec_type = rec['type']
                
                if food not in food_scores:
                    food_scores[food] = {
                        'total_score': 0,
                        'count': 0,
                        'reasons': [],
                        'types': []
                    }
                
                weight = weights.get(rec_type, 0.1)
                food_scores[food]['total_score'] += score * weight
                food_scores[food]['count'] += 1
                food_scores[food]['reasons'].append(rec['reason'])
                food_scores[food]['types'].append(rec_type)
        
        # 转换为推荐列表
        recommendations = []
        for food, data in food_scores.items():
            recommendations.append({
                'food': food,
                'score': data['total_score'],
                'count': data['count'],
                'reasons': data['reasons'],
                'types': data['types']
            })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)
    
    def _filter_and_rank_recommendations(self, recommendations: List[Dict], 
                                       user_data: UserData, preferences: Dict) -> List[Dict[str, Any]]:
        """过滤和排序推荐"""
        filtered = []
        
        # 获取用户不喜欢的食物
        dislikes = user_data.profile.get('dislikes', [])
        allergies = user_data.profile.get('allergies', [])
        
        for rec in recommendations:
            food = rec['food']
            
            # 过滤不喜欢的食物
            if any(dislike in food for dislike in dislikes):
                continue
            
            # 过滤过敏食物
            if any(allergy in food for allergy in allergies):
                continue
            
            # 应用用户偏好
            if preferences:
                if 'taste' in preferences:
                    taste = preferences['taste']
                    if taste == 'sweet' and not self._is_sweet_food(food):
                        rec['score'] *= 0.8
                    elif taste == 'spicy' and not self._is_spicy_food(food):
                        rec['score'] *= 0.8
            
            filtered.append(rec)
        
        return sorted(filtered, key=lambda x: x['score'], reverse=True)
    
    def _generate_recommendation_reasoning(self, recommendations: List[Dict], user_data: UserData) -> str:
        """生成推荐理由"""
        if not recommendations:
            return "暂无推荐"
        
        top_rec = recommendations[0]
        reasons = top_rec.get('reasons', [])
        
        if reasons:
            return f"推荐{top_rec['food']}，理由：{'; '.join(reasons[:2])}"
        else:
            return f"推荐{top_rec['food']}，基于您的个人偏好"
    
    def _calculate_recommendation_confidence(self, user_data: UserData) -> float:
        """计算推荐置信度"""
        meal_count = len(user_data.meals)
        feedback_count = len(user_data.feedback)
        
        # 基于数据量计算置信度
        if meal_count >= 15 and feedback_count >= 5:
            return 0.9
        elif meal_count >= 10 and feedback_count >= 3:
            return 0.7
        elif meal_count >= 5:
            return 0.5
        else:
            return 0.3
    
    def _extract_user_features(self, user_data: UserData) -> np.ndarray:
        """提取用户特征向量"""
        features = []
        
        # 基础特征
        profile = user_data.profile
        features.extend([
            profile.get('age', 25),
            profile.get('height', 165),
            profile.get('weight', 60),
            len(profile.get('allergies', [])),
            len(profile.get('dislikes', []))
        ])
        
        # 口味偏好特征
        taste_prefs = profile.get('taste_preferences', {})
        features.extend([
            taste_prefs.get('sweet', 3),
            taste_prefs.get('salty', 3),
            taste_prefs.get('spicy', 3),
            taste_prefs.get('sour', 3),
            taste_prefs.get('bitter', 3),
            taste_prefs.get('umami', 3)
        ])
        
        # 餐食特征
        features.extend([
            len(user_data.meals),
            np.mean([meal.get('satisfaction_score', 3) for meal in user_data.meals]) if user_data.meals else 3,
            len(user_data.feedback)
        ])
        
        return np.array(features)
    
    def _find_similar_users(self, user_features: np.ndarray) -> List[str]:
        """找到相似用户"""
        # 这里简化实现，实际应该基于用户聚类模型
        return []
    
    def _get_user_data_by_id(self, user_id: str) -> Optional[UserData]:
        """根据ID获取用户数据"""
        # 这里需要从数据管理器获取，简化实现
        return None
    
    def _is_sweet_food(self, food: str) -> bool:
        """判断是否为甜食"""
        sweet_keywords = ['甜', '糖', '蜂蜜', '果', '蛋糕', '巧克力', '冰淇淋']
        return any(keyword in food for keyword in sweet_keywords)
    
    def _is_spicy_food(self, food: str) -> bool:
        """判断是否为辣食"""
        spicy_keywords = ['辣', '椒', '麻', '辛', '咖喱', '辣椒']
        return any(keyword in food for keyword in spicy_keywords)
    
    def _load_meal_templates(self) -> Dict[str, List[Dict]]:
        """加载基础餐食搭配模板（作为备选方案）"""
        return {
            "breakfast": [
                {"name": "经典早餐", "categories": ["主食", "蛋白质", "饮品"]},
                {"name": "健康早餐", "categories": ["谷物", "水果", "蛋白质"]},
                {"name": "中式早餐", "categories": ["主食", "蛋白质", "蔬菜"]}
            ],
            "lunch": [
                {"name": "均衡午餐", "categories": ["主食", "蛋白质", "蔬菜"]},
                {"name": "轻食午餐", "categories": ["主食", "蛋白质", "蔬菜"]},
                {"name": "丰盛午餐", "categories": ["主食", "蛋白质", "蔬菜", "汤品"]}
            ],
            "dinner": [
                {"name": "清淡晚餐", "categories": ["主食", "蛋白质", "蔬菜"]},
                {"name": "温馨晚餐", "categories": ["主食", "蛋白质", "蔬菜"]}
            ],
            "snack": [
                {"name": "健康小食", "categories": ["水果", "坚果"]},
                {"name": "休闲小食", "categories": ["饮品", "小食"]}
            ]
        }

    def _load_food_database(self) -> Dict[str, Dict]:
        """加载食物数据库"""
        return {
            '米饭': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3, 'category': '主食'},
            '面条': {'calories': 131, 'protein': 5, 'carbs': 25, 'fat': 1.1, 'category': '主食'},
            '鸡蛋': {'calories': 155, 'protein': 13, 'carbs': 1.1, 'fat': 11, 'category': '蛋白质'},
            '鸡肉': {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6, 'category': '蛋白质'},
            '鱼肉': {'calories': 206, 'protein': 22, 'carbs': 0, 'fat': 12, 'category': '蛋白质'},
            '豆腐': {'calories': 76, 'protein': 8, 'carbs': 2, 'fat': 4.8, 'category': '蛋白质'},
            '菠菜': {'calories': 23, 'protein': 2.9, 'carbs': 3.6, 'fat': 0.4, 'category': '蔬菜'},
            '西兰花': {'calories': 34, 'protein': 2.8, 'carbs': 7, 'fat': 0.4, 'category': '蔬菜'},
            '苹果': {'calories': 52, 'protein': 0.3, 'carbs': 14, 'fat': 0.2, 'category': '水果'},
            '香蕉': {'calories': 89, 'protein': 1.1, 'carbs': 23, 'fat': 0.3, 'category': '水果'},
            '牛奶': {'calories': 42, 'protein': 3.4, 'carbs': 5, 'fat': 1, 'category': '乳制品'},
            '燕麦': {'calories': 389, 'protein': 17, 'carbs': 66, 'fat': 7, 'category': '主食'}
        }
    
    def _load_or_train_models(self):
        """加载或训练模型"""
        try:
            # 尝试加载现有模型
            tfidf_path = self.model_path / 'tfidf_vectorizer.pkl'
            if tfidf_path.exists():
                self.tfidf_vectorizer = joblib.load(tfidf_path)
                self.logger.info("TF-IDF向量化器加载成功")
            
            # 构建食物相似性矩阵
            self._build_food_similarity_matrix()
            
        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
            # 如果加载失败，使用默认配置
            self._initialize_default_models()
    
    def _build_food_similarity_matrix(self):
        """构建食物相似性矩阵"""
        try:
            if not self.tfidf_vectorizer:
                self._initialize_default_models()
            
            # 获取所有食物名称
            food_names = list(self.food_database.keys())
            
            # 使用TF-IDF计算相似性
            food_features = self.tfidf_vectorizer.transform(food_names)
            similarity_matrix = cosine_similarity(food_features)
            
            # 构建相似性字典
            self.food_similarity_matrix = {}
            for i, food1 in enumerate(food_names):
                similarities = {}
                for j, food2 in enumerate(food_names):
                    if i != j:
                        similarities[food2] = similarity_matrix[i][j]
                
                # 按相似性排序
                sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
                self.food_similarity_matrix[food1] = dict(sorted_similarities[:5])  # 只保留前5个相似食物
            
            self.logger.info("食物相似性矩阵构建完成")
            
        except Exception as e:
            self.logger.error(f"构建食物相似性矩阵失败: {e}")
            self.food_similarity_matrix = {}
    
    def _initialize_default_models(self):
        """初始化默认模型"""
        try:
            # 初始化TF-IDF向量化器
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=None,  # 中文不需要英文停用词
                ngram_range=(1, 2)
            )
            
            # 使用食物名称训练
            food_names = list(self.food_database.keys())
            self.tfidf_vectorizer.fit(food_names)
            
            # 保存模型
            tfidf_path = self.model_path / 'tfidf_vectorizer.pkl'
            joblib.dump(self.tfidf_vectorizer, tfidf_path)
            
            self.logger.info("默认模型初始化完成")
            
        except Exception as e:
            self.logger.error(f"默认模型初始化失败: {e}")
    
    def _find_similar_foods(self, input_data: Dict, user_data: UserData) -> Dict[str, Any]:
        """查找相似食物"""
        target_food = input_data.get('food', '')
        
        if not target_food or not self.food_similarity_matrix:
            return self._create_error_result("无法找到相似食物")
        
        similar_foods = self.food_similarity_matrix.get(target_food, {})
        
        return {
            'success': True,
            'target_food': target_food,
            'similar_foods': list(similar_foods.items()),
            'confidence': 0.8
        }
    
    def _update_user_preferences(self, input_data: Dict, user_data: UserData) -> Dict[str, Any]:
        """更新用户偏好"""
        feedback_data = input_data.get('feedback', {})
        
        # 更新用户偏好模型
        # 这里可以实现更复杂的偏好学习算法
        
        return {
            'success': True,
            'message': '用户偏好更新成功',
            'confidence': 0.7
        }
    
    def _retrain_models(self, input_data: Dict, user_data: UserData) -> Dict[str, Any]:
        """重新训练模型"""
        try:
            # 检查是否有足够的数据进行重训练
            total_samples = len(user_data.meals) + len(user_data.feedback)
            
            if total_samples < self.model_update_threshold:
                return {
                    'success': False,
                    'message': f'数据不足，需要至少{self.model_update_threshold}个样本',
                    'current_samples': total_samples
                }
            
            # 重新训练模型
            self._load_or_train_models()
            
            return {
                'success': True,
                'message': '模型重训练完成',
                'confidence': 0.9
            }
            
        except Exception as e:
            return self._create_error_result(f"模型重训练失败: {str(e)}")
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """创建错误结果"""
        return {
            'success': False,
            'error': error_message,
            'message': f'推荐失败: {error_message}',
            'confidence': 0.0
        }
    
    def cleanup(self) -> bool:
        """清理资源"""
        try:
            self.logger.info("推荐引擎清理完成")
            return True
        except Exception as e:
            self.logger.error(f"推荐引擎清理失败: {e}")
            return False


# 便捷函数
def generate_meal_recommendations(user_id: str, meal_type: str, preferences: Dict = None, context: Dict = None) -> Optional[Dict]:
    """生成餐食推荐"""
    from core.base import get_app_core
    
    if preferences is None:
        preferences = {}
    if context is None:
        context = {}
    
    app = get_app_core()
    input_data = {
        'type': 'meal_recommendation',
        'meal_type': meal_type,
        'preferences': preferences,
        'context': context
    }
    
    result = app.process_user_request(ModuleType.RECOMMENDATION, input_data, user_id)
    return result.result if result else None


def find_similar_foods(user_id: str, food: str) -> Optional[Dict]:
    """查找相似食物"""
    from core.base import get_app_core
    
    app = get_app_core()
    input_data = {
        'type': 'food_similarity',
        'food': food
    }
    
    result = app.process_user_request(ModuleType.RECOMMENDATION, input_data, user_id)
    return result.result if result else None


def update_user_preferences(user_id: str, feedback: Dict) -> Optional[Dict]:
    """更新用户偏好"""
    from core.base import get_app_core
    
    app = get_app_core()
    input_data = {
        'type': 'preference_update',
        'feedback': feedback
    }
    
    result = app.process_user_request(ModuleType.RECOMMENDATION, input_data, user_id)
    return result.result if result else None


def retrain_recommendation_model(user_id: str) -> Optional[Dict]:
    """重新训练推荐模型"""
    from core.base import get_app_core
    
    app = get_app_core()
    input_data = {
        'type': 'model_retrain'
    }
    
    result = app.process_user_request(ModuleType.RECOMMENDATION, input_data, user_id)
    return result.result if result else None


if __name__ == "__main__":
    # 测试推荐引擎
    from core.base import BaseConfig, initialize_app, cleanup_app
    
    print("测试推荐引擎...")
    
    # 初始化应用
    config = BaseConfig()
    if initialize_app(config):
        print("✅ 应用初始化成功")
        
        # 测试餐食推荐
        test_user_id = "test_user_001"
        
        result = generate_meal_recommendations(test_user_id, "lunch", {"taste": "sweet"})
        if result and result.get('success'):
            recommendations = result.get('recommendations', [])
            print(f"✅ 餐食推荐成功，推荐了{len(recommendations)}种食物")
            for rec in recommendations[:3]:
                print(f"  - {rec['food']}: {rec.get('score', 0):.2f}")
        
        # 测试相似食物查找
        result = find_similar_foods(test_user_id, "米饭")
        if result and result.get('success'):
            similar_foods = result.get('similar_foods', [])
            print(f"✅ 相似食物查找成功，找到{len(similar_foods)}种相似食物")
        
        # 清理应用
        cleanup_app()
        print("✅ 应用清理完成")
    else:
        print("❌ 应用初始化失败")
