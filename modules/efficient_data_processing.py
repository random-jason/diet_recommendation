"""
高效数据处理和训练模块
优化数据处理流程，提高训练效率
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class EfficientDataProcessor:
    """高效数据处理器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 数据缓存
        self.user_data_cache = {}
        self.meal_data_cache = {}
        self.feedback_data_cache = {}
        
        # 预计算数据
        self.food_frequency = {}
        self.user_preferences = {}
        self.nutrition_patterns = {}
        
        # 线程锁
        self.cache_lock = threading.Lock()
        
        # 加载预计算数据
        self._load_precomputed_data()
    
    def _load_precomputed_data(self):
        """加载预计算数据"""
        try:
            # 加载食物频率
            freq_file = self.data_dir / "food_frequency.pkl"
            if freq_file.exists():
                with open(freq_file, 'rb') as f:
                    self.food_frequency = pickle.load(f)
            
            # 加载用户偏好
            pref_file = self.data_dir / "user_preferences.pkl"
            if pref_file.exists():
                with open(pref_file, 'rb') as f:
                    self.user_preferences = pickle.load(f)
            
            # 加载营养模式
            pattern_file = self.data_dir / "nutrition_patterns.pkl"
            if pattern_file.exists():
                with open(pattern_file, 'rb') as f:
                    self.nutrition_patterns = pickle.load(f)
                    
        except Exception as e:
            logger.warning(f"加载预计算数据失败: {e}")
    
    def _save_precomputed_data(self):
        """保存预计算数据"""
        try:
            # 保存食物频率
            freq_file = self.data_dir / "food_frequency.pkl"
            with open(freq_file, 'wb') as f:
                pickle.dump(self.food_frequency, f)
            
            # 保存用户偏好
            pref_file = self.data_dir / "user_preferences.pkl"
            with open(pref_file, 'wb') as f:
                pickle.dump(self.user_preferences, f)
            
            # 保存营养模式
            pattern_file = self.data_dir / "nutrition_patterns.pkl"
            with open(pattern_file, 'wb') as f:
                pickle.dump(self.nutrition_patterns, f)
                
        except Exception as e:
            logger.error(f"保存预计算数据失败: {e}")
    
    def batch_process_user_data(self, user_ids: List[str]) -> Dict[str, Any]:
        """批量处理用户数据"""
        logger.info(f"开始批量处理 {len(user_ids)} 个用户的数据")
        
        results = {}
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=4) as executor:
            # 提交任务
            future_to_user = {
                executor.submit(self._process_single_user, user_id): user_id 
                for user_id in user_ids
            }
            
            # 收集结果
            for future in as_completed(future_to_user):
                user_id = future_to_user[future]
                try:
                    result = future.result()
                    results[user_id] = result
                except Exception as e:
                    logger.error(f"处理用户 {user_id} 数据失败: {e}")
                    results[user_id] = {'error': str(e)}
        
        # 更新预计算数据
        self._update_precomputed_data(results)
        
        logger.info(f"批量处理完成，成功处理 {len(results)} 个用户")
        return results
    
    def _process_single_user(self, user_id: str) -> Dict[str, Any]:
        """处理单个用户数据"""
        try:
            from core.base import AppCore
            
            app_core = AppCore()
            user_data = app_core.get_user_data(user_id)
            
            if not user_data:
                return {'error': '用户数据不存在'}
            
            # 处理餐食数据
            meal_analysis = self._analyze_meal_patterns(user_data.meals)
            
            # 处理反馈数据
            feedback_analysis = self._analyze_feedback_patterns(user_data.feedback)
            
            # 处理用户偏好
            preference_analysis = self._analyze_user_preferences(user_data)
            
            # 生成个性化建议
            recommendations = self._generate_personalized_recommendations(
                user_data, meal_analysis, feedback_analysis, preference_analysis
            )
            
            return {
                'user_id': user_id,
                'meal_analysis': meal_analysis,
                'feedback_analysis': feedback_analysis,
                'preference_analysis': preference_analysis,
                'recommendations': recommendations,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"处理用户 {user_id} 数据失败: {e}")
            return {'error': str(e)}
    
    def _analyze_meal_patterns(self, meals: List[Dict]) -> Dict[str, Any]:
        """分析餐食模式"""
        if not meals:
            return {'total_meals': 0, 'patterns': {}}
        
        # 统计食物频率
        food_counter = Counter()
        meal_type_counter = Counter()
        satisfaction_scores = []
        calorie_totals = []
        
        for meal in meals:
            # 统计食物
            for food in meal.get('foods', []):
                food_counter[food] += 1
            
            # 统计餐次
            meal_type_counter[meal.get('meal_type', 'unknown')] += 1
            
            # 收集满意度
            if 'satisfaction_score' in meal:
                satisfaction_scores.append(meal['satisfaction_score'])
            
            # 收集热量
            if 'calories' in meal and meal['calories']:
                calorie_totals.append(meal['calories'])
        
        # 计算统计信息
        avg_satisfaction = np.mean(satisfaction_scores) if satisfaction_scores else 0
        avg_calories = np.mean(calorie_totals) if calorie_totals else 0
        
        # 识别模式
        patterns = {
            'favorite_foods': [food for food, count in food_counter.most_common(5)],
            'meal_type_preference': dict(meal_type_counter.most_common()),
            'avg_satisfaction': round(avg_satisfaction, 2),
            'avg_calories': round(avg_calories, 2),
            'total_meals': len(meals),
            'food_diversity': len(food_counter)
        }
        
        return patterns
    
    def _analyze_feedback_patterns(self, feedbacks: List[Dict]) -> Dict[str, Any]:
        """分析反馈模式"""
        if not feedbacks:
            return {'total_feedback': 0, 'patterns': {}}
        
        feedback_types = Counter()
        user_choices = []
        
        for feedback in feedbacks:
            feedback_types[feedback.get('feedback_type', 'unknown')] += 1
            if 'user_choice' in feedback:
                user_choices.append(feedback['user_choice'])
        
        patterns = {
            'feedback_distribution': dict(feedback_types.most_common()),
            'total_feedback': len(feedbacks),
            'common_choices': Counter(user_choices).most_common(5)
        }
        
        return patterns
    
    def _analyze_user_preferences(self, user_data) -> Dict[str, Any]:
        """分析用户偏好"""
        profile = user_data.profile
        
        preferences = {
            'basic_info': {
                'age': profile.get('age', 'unknown'),
                'gender': profile.get('gender', 'unknown'),
                'activity_level': profile.get('activity_level', 'unknown')
            },
            'taste_preferences': profile.get('taste_preferences', {}),
            'dietary_restrictions': {
                'allergies': profile.get('allergies', []),
                'dislikes': profile.get('dislikes', []),
                'dietary_preferences': profile.get('dietary_preferences', [])
            },
            'health_goals': profile.get('health_goals', [])
        }
        
        return preferences
    
    def _generate_personalized_recommendations(self, user_data, meal_analysis, 
                                            feedback_analysis, preference_analysis) -> Dict[str, Any]:
        """生成个性化建议"""
        recommendations = {
            'food_recommendations': [],
            'meal_suggestions': [],
            'health_tips': [],
            'improvement_suggestions': []
        }
        
        # 基于食物频率推荐
        favorite_foods = meal_analysis.get('favorite_foods', [])
        if favorite_foods:
            recommendations['food_recommendations'].extend(favorite_foods[:3])
        
        # 基于反馈推荐
        feedback_patterns = feedback_analysis.get('feedback_distribution', {})
        if feedback_patterns.get('like', 0) > feedback_patterns.get('dislike', 0):
            recommendations['meal_suggestions'].append("继续选择您喜欢的食物")
        
        # 基于健康目标推荐
        health_goals = preference_analysis.get('health_goals', [])
        if '减重' in health_goals:
            recommendations['health_tips'].append("建议增加蔬菜摄入，减少高热量食物")
        elif '增重' in health_goals:
            recommendations['health_tips'].append("建议增加蛋白质和健康脂肪摄入")
        
        # 基于满意度推荐
        avg_satisfaction = meal_analysis.get('avg_satisfaction', 0)
        if avg_satisfaction < 3:
            recommendations['improvement_suggestions'].append("尝试新的食物组合以提高满意度")
        
        return recommendations
    
    def _update_precomputed_data(self, results: Dict[str, Any]):
        """更新预计算数据"""
        with self.cache_lock:
            # 更新食物频率
            for user_id, result in results.items():
                if 'error' in result:
                    continue
                
                meal_analysis = result.get('meal_analysis', {})
                favorite_foods = meal_analysis.get('favorite_foods', [])
                
                for food in favorite_foods:
                    self.food_frequency[food] = self.food_frequency.get(food, 0) + 1
            
            # 更新用户偏好
            for user_id, result in results.items():
                if 'error' in result:
                    continue
                
                preference_analysis = result.get('preference_analysis', {})
                self.user_preferences[user_id] = preference_analysis
            
            # 更新营养模式
            for user_id, result in results.items():
                if 'error' in result:
                    continue
                
                meal_analysis = result.get('meal_analysis', {})
                self.nutrition_patterns[user_id] = {
                    'avg_calories': meal_analysis.get('avg_calories', 0),
                    'avg_satisfaction': meal_analysis.get('avg_satisfaction', 0),
                    'food_diversity': meal_analysis.get('food_diversity', 0)
                }
            
            # 保存预计算数据
            self._save_precomputed_data()
    
    def get_popular_foods(self, limit: int = 10) -> List[Tuple[str, int]]:
        """获取热门食物"""
        return sorted(self.food_frequency.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_user_similarity(self, user_id: str) -> List[Tuple[str, float]]:
        """获取相似用户"""
        if user_id not in self.user_preferences:
            return []
        
        target_prefs = self.user_preferences[user_id]
        similarities = []
        
        for other_user_id, other_prefs in self.user_preferences.items():
            if other_user_id == user_id:
                continue
            
            # 计算相似度（简化版本）
            similarity = self._calculate_preference_similarity(target_prefs, other_prefs)
            similarities.append((other_user_id, similarity))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:5]
    
    def _calculate_preference_similarity(self, prefs1: Dict, prefs2: Dict) -> float:
        """计算偏好相似度"""
        # 简化的相似度计算
        score = 0.0
        total = 0.0
        
        # 比较基本特征
        basic1 = prefs1.get('basic_info', {})
        basic2 = prefs2.get('basic_info', {})
        
        if basic1.get('gender') == basic2.get('gender'):
            score += 0.3
        total += 0.3
        
        if basic1.get('activity_level') == basic2.get('activity_level'):
            score += 0.2
        total += 0.2
        
        # 比较口味偏好
        taste1 = prefs1.get('taste_preferences', {})
        taste2 = prefs2.get('taste_preferences', {})
        
        for key in taste1:
            if key in taste2 and taste1[key] == taste2[key]:
                score += 0.1
            total += 0.1
        
        return score / total if total > 0 else 0.0
    
    def export_analysis_report(self, user_id: str, output_file: str = None) -> str:
        """导出分析报告"""
        if not output_file:
            output_file = self.data_dir / f"analysis_report_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            # 获取用户数据
            from core.base import AppCore
            app_core = AppCore()
            user_data = app_core.get_user_data(user_id)
            
            if not user_data:
                raise ValueError("用户数据不存在")
            
            # 生成分析报告
            report = {
                'user_id': user_id,
                'generated_at': datetime.now().isoformat(),
                'user_profile': user_data.profile,
                'meal_statistics': self._analyze_meal_patterns(user_data.meals),
                'feedback_statistics': self._analyze_feedback_patterns(user_data.feedback),
                'recommendations': self._generate_personalized_recommendations(
                    user_data,
                    self._analyze_meal_patterns(user_data.meals),
                    self._analyze_feedback_patterns(user_data.feedback),
                    self._analyze_user_preferences(user_data)
                ),
                'similar_users': self.get_user_similarity(user_id),
                'popular_foods': self.get_popular_foods(10)
            }
            
            # 保存报告
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"分析报告已导出到: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"导出分析报告失败: {e}")
            raise


class FastTrainingPipeline:
    """快速训练管道"""
    
    def __init__(self, data_processor: EfficientDataProcessor):
        self.data_processor = data_processor
        self.models = {}
        self.training_cache = {}
        self._background_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
    
    def train_recommendation_model(self, user_ids: List[str]) -> Dict[str, Any]:
        """训练推荐模型"""
        logger.info(f"开始训练推荐模型，用户数量: {len(user_ids)}")
        
        # 批量处理用户数据
        processed_data = self.data_processor.batch_process_user_data(user_ids)
        
        # 提取特征
        features = self._extract_features(processed_data)
        
        # 训练模型（简化版本）
        model_results = self._train_simple_recommendation_model(features)
        
        # 缓存模型
        self.models['recommendation'] = model_results
        
        logger.info("推荐模型训练完成")
        return model_results

    def start_background_training(self, user_ids_provider=None, interval_minutes: int = 60) -> None:
        """后台周期训练。
        user_ids_provider: 可选的函数，返回需要训练的user_id列表；若为空则从预计算偏好中取键。
        """
        if self._background_thread and self._background_thread.is_alive():
            return

        self._stop_event.clear()

        def _loop():
            while not self._stop_event.is_set():
                try:
                    if user_ids_provider is not None:
                        user_ids = list(user_ids_provider()) or list(self.data_processor.user_preferences.keys())
                    else:
                        user_ids = list(self.data_processor.user_preferences.keys())
                    if user_ids:
                        self.train_recommendation_model(user_ids)
                except Exception as e:
                    logger.warning(f"后台训练失败: {e}")
                finally:
                    self._stop_event.wait(interval_minutes * 60)

        self._background_thread = threading.Thread(target=_loop, daemon=True)
        self._background_thread.start()

    def stop_background_training(self) -> None:
        """停止后台训练"""
        self._stop_event.set()
        if self._background_thread and self._background_thread.is_alive():
            self._background_thread.join(timeout=1.0)
    
    def _extract_features(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取特征"""
        features = {
            'user_features': {},
            'food_features': {},
            'interaction_features': {}
        }
        
        for user_id, data in processed_data.items():
            if 'error' in data:
                continue
            
            # 用户特征
            preference_analysis = data.get('preference_analysis', {})
            features['user_features'][user_id] = {
                'age': preference_analysis.get('basic_info', {}).get('age', 25),
                'gender': preference_analysis.get('basic_info', {}).get('gender', 'unknown'),
                'activity_level': preference_analysis.get('basic_info', {}).get('activity_level', 'moderate')
            }
            
            # 食物特征
            meal_analysis = data.get('meal_analysis', {})
            favorite_foods = meal_analysis.get('favorite_foods', [])
            for food in favorite_foods:
                if food not in features['food_features']:
                    features['food_features'][food] = 0
                features['food_features'][food] += 1
            
            # 交互特征
            features['interaction_features'][user_id] = {
                'avg_satisfaction': meal_analysis.get('avg_satisfaction', 0),
                'avg_calories': meal_analysis.get('avg_calories', 0),
                'food_diversity': meal_analysis.get('food_diversity', 0)
            }
        
        return features
    
    def _train_simple_recommendation_model(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """训练简单推荐模型"""
        # 这里是一个简化的推荐模型
        # 在实际应用中，可以使用更复杂的机器学习算法
        
        model_results = {
            'model_type': 'simple_collaborative_filtering',
            'trained_at': datetime.now().isoformat(),
            'user_count': len(features['user_features']),
            'food_count': len(features['food_features']),
            'recommendation_rules': self._generate_recommendation_rules(features),
            'performance_metrics': {
                'accuracy': 0.75,  # 模拟指标
                'precision': 0.72,
                'recall': 0.68,
                'f1_score': 0.70
            }
        }
        
        return model_results
    
    def _generate_recommendation_rules(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成推荐规则"""
        rules = []
        
        # 基于食物频率的规则
        food_features = features['food_features']
        popular_foods = sorted(food_features.items(), key=lambda x: x[1], reverse=True)[:10]
        
        for food, count in popular_foods:
            rules.append({
                'type': 'popular_food',
                'condition': f"food_popularity >= {count}",
                'recommendation': f"推荐 {food}",
                'confidence': min(count / 10.0, 1.0)
            })
        
        # 基于用户特征的规则
        user_features = features['user_features']
        for user_id, user_feat in user_features.items():
            if user_feat['gender'] == '女':
                rules.append({
                    'type': 'gender_based',
                    'condition': f"gender == '女'",
                    'recommendation': "推荐富含铁质的食物",
                    'confidence': 0.8
                })
        
        return rules
    
    def predict_recommendations(self, user_id: str, meal_type: str = "lunch") -> List[Dict[str, Any]]:
        """预测推荐"""
        if 'recommendation' not in self.models:
            return []
        
        # 获取用户数据
        from core.base import AppCore
        app_core = AppCore()
        user_data = app_core.get_user_data(user_id)
        
        if not user_data:
            return []
        
        # 基于规则生成推荐
        recommendations = []
        rules = self.models['recommendation'].get('recommendation_rules', [])
        
        for rule in rules:
            if self._evaluate_rule(rule, user_data):
                recommendations.append({
                    'food': rule['recommendation'],
                    'confidence': rule['confidence'],
                    'reason': rule['type']
                })
        
        return recommendations[:5]  # 返回前5个推荐
    
    def _evaluate_rule(self, rule: Dict[str, Any], user_data) -> bool:
        """评估规则"""
        # 简化的规则评估
        rule_type = rule.get('type', '')
        
        if rule_type == 'popular_food':
            return True  # 总是推荐热门食物
        elif rule_type == 'gender_based':
            return user_data.profile.get('gender') == '女'
        
        return False


# 全局实例
data_processor = EfficientDataProcessor()
training_pipeline = FastTrainingPipeline(data_processor)


# 便捷函数
def batch_process_users(user_ids: List[str]) -> Dict[str, Any]:
    """批量处理用户数据"""
    return data_processor.batch_process_user_data(user_ids)


def train_recommendation_model(user_ids: List[str]) -> Dict[str, Any]:
    """训练推荐模型"""
    return training_pipeline.train_recommendation_model(user_ids)


def get_user_recommendations(user_id: str, meal_type: str = "lunch") -> List[Dict[str, Any]]:
    """获取用户推荐"""
    return training_pipeline.predict_recommendations(user_id, meal_type)


def export_user_report(user_id: str, output_file: str = None) -> str:
    """导出用户报告"""
    return data_processor.export_analysis_report(user_id, output_file)


if __name__ == "__main__":
    # 测试数据处理
    print("测试高效数据处理...")
    
    # 测试批量处理
    test_users = ["user1", "user2", "user3"]
    results = batch_process_users(test_users)
    print(f"批量处理结果: {len(results)} 个用户")
    
    # 测试训练
    model_results = train_recommendation_model(test_users)
    print(f"模型训练完成: {model_results['model_type']}")
    
    print("测试完成！")
