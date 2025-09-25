"""
智能食物数据库和热量估算模块
简化用户数据录入过程
"""

from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path


class SmartFoodDatabase:
    """智能食物数据库"""
    
    def __init__(self):
        self.food_database = self._load_food_database()
        self.portion_sizes = self._load_portion_sizes()
        self.calorie_estimates = self._load_calorie_estimates()
        
        # 添加缓存
        self.ai_cache = {}  # AI分析结果缓存
        self.calorie_cache = {}  # 热量估算缓存
        self.search_cache = {}  # 搜索结果缓存
        
        # 预计算常用食物
        self._precompute_common_foods()
    
    def _load_food_database(self) -> Dict[str, Dict]:
        """加载食物数据库"""
        return {
            # 主食类
            "米饭": {"category": "主食", "calories_per_100g": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
            "面条": {"category": "主食", "calories_per_100g": 131, "protein": 5, "carbs": 25, "fat": 1.1},
            "馒头": {"category": "主食", "calories_per_100g": 221, "protein": 7, "carbs": 47, "fat": 1.1},
            "包子": {"category": "主食", "calories_per_100g": 227, "protein": 7.3, "carbs": 45, "fat": 2.6},
            "饺子": {"category": "主食", "calories_per_100g": 250, "protein": 11, "carbs": 35, "fat": 8},
            "粥": {"category": "主食", "calories_per_100g": 50, "protein": 1.1, "carbs": 10, "fat": 0.3},
            "燕麦": {"category": "主食", "calories_per_100g": 389, "protein": 17, "carbs": 66, "fat": 7},
            "面包": {"category": "主食", "calories_per_100g": 265, "protein": 9, "carbs": 49, "fat": 3.2},
            "饼干": {"category": "主食", "calories_per_100g": 433, "protein": 9, "carbs": 71, "fat": 12},
            "薯条": {"category": "主食", "calories_per_100g": 319, "protein": 4, "carbs": 41, "fat": 15},
            "玉米": {"category": "主食", "calories_per_100g": 86, "protein": 3.4, "carbs": 19, "fat": 1.2},
            "红薯": {"category": "主食", "calories_per_100g": 86, "protein": 1.6, "carbs": 20, "fat": 0.1},
            
            # 蛋白质类
            "鸡蛋": {"category": "蛋白质", "calories_per_100g": 155, "protein": 13, "carbs": 1.1, "fat": 11},
            "鸡肉": {"category": "蛋白质", "calories_per_100g": 165, "protein": 31, "carbs": 0, "fat": 3.6},
            "猪肉": {"category": "蛋白质", "calories_per_100g": 143, "protein": 20, "carbs": 0, "fat": 6.2},
            "牛肉": {"category": "蛋白质", "calories_per_100g": 250, "protein": 26, "carbs": 0, "fat": 15},
            "鱼肉": {"category": "蛋白质", "calories_per_100g": 206, "protein": 22, "carbs": 0, "fat": 12},
            "豆腐": {"category": "蛋白质", "calories_per_100g": 76, "protein": 8, "carbs": 2, "fat": 4.8},
            "牛奶": {"category": "蛋白质", "calories_per_100g": 42, "protein": 3.4, "carbs": 5, "fat": 1},
            "酸奶": {"category": "蛋白质", "calories_per_100g": 59, "protein": 3.3, "carbs": 4.7, "fat": 3.2},
            "虾": {"category": "蛋白质", "calories_per_100g": 99, "protein": 24, "carbs": 0, "fat": 0.2},
            "蟹": {"category": "蛋白质", "calories_per_100g": 97, "protein": 20, "carbs": 0, "fat": 1.5},
            "鸭肉": {"category": "蛋白质", "calories_per_100g": 183, "protein": 25, "carbs": 0, "fat": 9},
            "羊肉": {"category": "蛋白质", "calories_per_100g": 203, "protein": 25, "carbs": 0, "fat": 11},
            "火腿": {"category": "蛋白质", "calories_per_100g": 145, "protein": 18, "carbs": 1.5, "fat": 7.5},
            "香肠": {"category": "蛋白质", "calories_per_100g": 301, "protein": 13, "carbs": 2, "fat": 25},
            
            # 蔬菜类
            "白菜": {"category": "蔬菜", "calories_per_100g": 17, "protein": 1.5, "carbs": 3.2, "fat": 0.1},
            "菠菜": {"category": "蔬菜", "calories_per_100g": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4},
            "西兰花": {"category": "蔬菜", "calories_per_100g": 34, "protein": 2.8, "carbs": 7, "fat": 0.4},
            "胡萝卜": {"category": "蔬菜", "calories_per_100g": 41, "protein": 0.9, "carbs": 10, "fat": 0.2},
            "土豆": {"category": "蔬菜", "calories_per_100g": 77, "protein": 2, "carbs": 17, "fat": 0.1},
            "西红柿": {"category": "蔬菜", "calories_per_100g": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
            "黄瓜": {"category": "蔬菜", "calories_per_100g": 16, "protein": 0.7, "carbs": 4, "fat": 0.1},
            "茄子": {"category": "蔬菜", "calories_per_100g": 25, "protein": 1.1, "carbs": 6, "fat": 0.2},
            "豆角": {"category": "蔬菜", "calories_per_100g": 31, "protein": 2.1, "carbs": 7, "fat": 0.2},
            "韭菜": {"category": "蔬菜", "calories_per_100g": 25, "protein": 2.4, "carbs": 4, "fat": 0.4},
            "芹菜": {"category": "蔬菜", "calories_per_100g": 16, "protein": 0.7, "carbs": 4, "fat": 0.1},
            "洋葱": {"category": "蔬菜", "calories_per_100g": 40, "protein": 1.1, "carbs": 9, "fat": 0.1},
            "大蒜": {"category": "蔬菜", "calories_per_100g": 149, "protein": 6.4, "carbs": 33, "fat": 0.5},
            "生姜": {"category": "蔬菜", "calories_per_100g": 80, "protein": 1.8, "carbs": 18, "fat": 0.8},
            
            # 水果类
            "苹果": {"category": "水果", "calories_per_100g": 52, "protein": 0.3, "carbs": 14, "fat": 0.2},
            "香蕉": {"category": "水果", "calories_per_100g": 89, "protein": 1.1, "carbs": 23, "fat": 0.3},
            "橙子": {"category": "水果", "calories_per_100g": 47, "protein": 0.9, "carbs": 12, "fat": 0.1},
            "葡萄": {"category": "水果", "calories_per_100g": 44, "protein": 0.2, "carbs": 11, "fat": 0.2},
            "草莓": {"category": "水果", "calories_per_100g": 32, "protein": 0.7, "carbs": 8, "fat": 0.3},
            "西瓜": {"category": "水果", "calories_per_100g": 30, "protein": 0.6, "carbs": 8, "fat": 0.1},
            "梨": {"category": "水果", "calories_per_100g": 57, "protein": 0.4, "carbs": 15, "fat": 0.1},
            "桃子": {"category": "水果", "calories_per_100g": 39, "protein": 0.9, "carbs": 10, "fat": 0.3},
            "樱桃": {"category": "水果", "calories_per_100g": 63, "protein": 1.1, "carbs": 16, "fat": 0.2},
            "柠檬": {"category": "水果", "calories_per_100g": 29, "protein": 1.1, "carbs": 9, "fat": 0.3},
            "芒果": {"category": "水果", "calories_per_100g": 60, "protein": 0.8, "carbs": 15, "fat": 0.4},
            "菠萝": {"category": "水果", "calories_per_100g": 50, "protein": 0.5, "carbs": 13, "fat": 0.1},
            "猕猴桃": {"category": "水果", "calories_per_100g": 61, "protein": 1.1, "carbs": 15, "fat": 0.5},
            
            # 坚果类
            "花生": {"category": "坚果", "calories_per_100g": 567, "protein": 25, "carbs": 16, "fat": 49},
            "核桃": {"category": "坚果", "calories_per_100g": 654, "protein": 15, "carbs": 14, "fat": 65},
            "杏仁": {"category": "坚果", "calories_per_100g": 579, "protein": 21, "carbs": 22, "fat": 50},
            "腰果": {"category": "坚果", "calories_per_100g": 553, "protein": 18, "carbs": 30, "fat": 44},
            "开心果": {"category": "坚果", "calories_per_100g": 560, "protein": 20, "carbs": 28, "fat": 45},
            "瓜子": {"category": "坚果", "calories_per_100g": 606, "protein": 19, "carbs": 20, "fat": 53},
            
            # 饮料类
            "水": {"category": "饮料", "calories_per_100g": 0, "protein": 0, "carbs": 0, "fat": 0},
            "茶": {"category": "饮料", "calories_per_100g": 1, "protein": 0.1, "carbs": 0.3, "fat": 0},
            "咖啡": {"category": "饮料", "calories_per_100g": 2, "protein": 0.1, "carbs": 0.3, "fat": 0},
            "果汁": {"category": "饮料", "calories_per_100g": 45, "protein": 0.3, "carbs": 11, "fat": 0.1},
            "可乐": {"category": "饮料", "calories_per_100g": 42, "protein": 0, "carbs": 10.6, "fat": 0},
            "雪碧": {"category": "饮料", "calories_per_100g": 40, "protein": 0, "carbs": 10, "fat": 0},
            "啤酒": {"category": "饮料", "calories_per_100g": 43, "protein": 0.5, "carbs": 3.6, "fat": 0},
            "红酒": {"category": "饮料", "calories_per_100g": 83, "protein": 0.1, "carbs": 2.6, "fat": 0},
            "白酒": {"category": "饮料", "calories_per_100g": 298, "protein": 0, "carbs": 0, "fat": 0},
            
            # 调料类
            "盐": {"category": "调料", "calories_per_100g": 0, "protein": 0, "carbs": 0, "fat": 0},
            "糖": {"category": "调料", "calories_per_100g": 387, "protein": 0, "carbs": 100, "fat": 0},
            "酱油": {"category": "调料", "calories_per_100g": 63, "protein": 7, "carbs": 7, "fat": 0},
            "醋": {"category": "调料", "calories_per_100g": 31, "protein": 0.1, "carbs": 7, "fat": 0},
            "油": {"category": "调料", "calories_per_100g": 884, "protein": 0, "carbs": 0, "fat": 100},
            "辣椒": {"category": "调料", "calories_per_100g": 40, "protein": 1.9, "carbs": 9, "fat": 0.4},
            "胡椒": {"category": "调料", "calories_per_100g": 251, "protein": 10, "carbs": 64, "fat": 3.3},
            "花椒": {"category": "调料", "calories_per_100g": 258, "protein": 6, "carbs": 37, "fat": 8.9},
        }
    
    def _load_portion_sizes(self) -> Dict[str, List[str]]:
        """加载分量选项"""
        return {
            "主食": ["1小碗", "1中碗", "1大碗", "1个", "2个", "3个", "半份", "1份", "2份"],
            "蛋白质": ["1个", "2个", "3个", "1小块", "2小块", "1片", "2片", "1杯", "2杯", "适量"],
            "蔬菜": ["1小份", "1中份", "1大份", "1把", "2把", "1根", "2根", "适量", "很多"],
            "水果": ["1个", "2个", "3个", "1小个", "1大个", "1片", "2片", "适量"],
            "坚果": ["1小把", "1把", "2把", "1颗", "2颗", "3颗", "适量"],
            "饮料": ["1杯", "2杯", "3杯", "1小杯", "1大杯", "1瓶", "2瓶", "适量"],
            "调料": ["1小勺", "1勺", "2勺", "1小匙", "1匙", "2匙", "适量", "少许"]
        }
    
    def _load_calorie_estimates(self) -> Dict[str, Dict]:
        """加载热量估算"""
        return {
            "1小碗": {"米饭": 130, "面条": 131, "粥": 50},
            "1中碗": {"米饭": 195, "面条": 196, "粥": 75},
            "1大碗": {"米饭": 260, "面条": 262, "粥": 100},
            "1个": {"鸡蛋": 77, "苹果": 52, "香蕉": 89, "馒头": 221, "包子": 227},
            "2个": {"鸡蛋": 154, "苹果": 104, "香蕉": 178, "馒头": 442, "包子": 454},
            "1小块": {"鸡肉": 50, "猪肉": 50, "牛肉": 50, "豆腐": 50},
            "2小块": {"鸡肉": 100, "猪肉": 100, "牛肉": 100, "豆腐": 100},
            "1杯": {"牛奶": 150, "酸奶": 150, "水": 0, "茶": 0, "咖啡": 0},
            "2杯": {"牛奶": 300, "酸奶": 300, "水": 0, "茶": 0, "咖啡": 0},
            "1小份": {"白菜": 50, "菠菜": 50, "西兰花": 50, "胡萝卜": 50},
            "1中份": {"白菜": 100, "菠菜": 100, "西兰花": 100, "胡萝卜": 100},
            "1大份": {"白菜": 150, "菠菜": 150, "西兰花": 150, "胡萝卜": 150},
            "1小把": {"花生": 30, "核桃": 30, "杏仁": 30},
            "1把": {"花生": 60, "核桃": 60, "杏仁": 60},
            "适量": {"default": 50},  # 默认适量为50卡路里
            "很多": {"default": 150},  # 默认很多为150卡路里
            "1小勺": {"盐": 0, "糖": 16, "酱油": 3, "醋": 2, "油": 44, "辣椒": 2, "胡椒": 13, "花椒": 13},
            "1勺": {"盐": 0, "糖": 32, "酱油": 6, "醋": 4, "油": 88, "辣椒": 4, "胡椒": 25, "花椒": 26},
            "2勺": {"盐": 0, "糖": 64, "酱油": 12, "醋": 8, "油": 176, "辣椒": 8, "胡椒": 50, "花椒": 52},
            "1小匙": {"盐": 0, "糖": 8, "酱油": 1.5, "醋": 1, "油": 22, "辣椒": 1, "胡椒": 6, "花椒": 6},
            "1匙": {"盐": 0, "糖": 16, "酱油": 3, "醋": 2, "油": 44, "辣椒": 2, "胡椒": 13, "花椒": 13},
            "2匙": {"盐": 0, "糖": 32, "酱油": 6, "醋": 4, "油": 88, "辣椒": 4, "胡椒": 25, "花椒": 26},
            "少许": {"default": 5},  # 默认少许为5卡路里
        }
    
    def search_foods(self, query: str) -> List[Dict]:
        """搜索食物（优化版本）"""
        query = query.lower().strip()
        
        # 检查缓存
        if query in self.search_cache:
            return self.search_cache[query]
        
        results = []
        
        # 精确匹配优先
        for food_name, food_info in self.food_database.items():
            if query == food_name.lower():
                results.insert(0, {
                    "name": food_name,
                    "category": food_info["category"],
                    "calories_per_100g": food_info["calories_per_100g"],
                    "match_type": "exact"
                })
        
        # 包含匹配
        for food_name, food_info in self.food_database.items():
            if query in food_name.lower() and query != food_name.lower():
                results.append({
                    "name": food_name,
                    "category": food_info["category"],
                    "calories_per_100g": food_info["calories_per_100g"],
                    "match_type": "contains"
                })
        
        # 关键词匹配
        if len(results) < 5:
            keywords = query.split()
            for food_name, food_info in self.food_database.items():
                if any(keyword in food_name.lower() for keyword in keywords):
                    if not any(r["name"] == food_name for r in results):
                        results.append({
                            "name": food_name,
                            "category": food_info["category"],
                            "calories_per_100g": food_info["calories_per_100g"],
                            "match_type": "keyword"
                        })
        
        # 限制结果数量并缓存
        results = results[:10]
        self.search_cache[query] = results
        
        return results
    
    def get_food_info(self, food_name: str) -> Optional[Dict]:
        """获取食物信息"""
        return self.food_database.get(food_name)
    
    def get_portion_options(self, food_name: str) -> List[str]:
        """获取分量选项"""
        food_info = self.get_food_info(food_name)
        if not food_info:
            return ["适量"]
        
        category = food_info["category"]
        return self.portion_sizes.get(category, ["适量"])
    
    def estimate_calories(self, food_name: str, portion: str) -> int:
        """估算热量（优化版本）"""
        # 检查缓存
        cache_key = f"{food_name}_{portion}"
        if cache_key in self.calorie_cache:
            return self.calorie_cache[cache_key]
        
        # 首先尝试精确匹配
        if portion in self.calorie_estimates:
            portion_data = self.calorie_estimates[portion]
            if food_name in portion_data:
                calories = portion_data[food_name]
                self.calorie_cache[cache_key] = calories
                return calories
            elif "default" in portion_data:
                calories = portion_data["default"]
                self.calorie_cache[cache_key] = calories
                return calories
        
        # 使用快速估算
        calories = self._calculate_calories_fast(food_name, portion)
        self.calorie_cache[cache_key] = calories
        return calories
    
    def _estimate_weight(self, portion: str, category: str) -> int:
        """估算重量（克）"""
        weight_estimates = {
            "1小碗": 100, "1中碗": 150, "1大碗": 200,
            "1个": 50, "2个": 100, "3个": 150,
            "1小块": 30, "2小块": 60,
            "1片": 20, "2片": 40,
            "1杯": 150, "2杯": 300,
            "1小份": 50, "1中份": 100, "1大份": 150,
            "1把": 30, "2把": 60,
            "1根": 100, "2根": 200,
            "1小把": 15, "1把": 30, "2把": 60,
            "1颗": 10, "2颗": 20, "3颗": 30,
            "1小勺": 5, "1勺": 10, "2勺": 20,
            "1小匙": 3, "1匙": 5, "2匙": 10,
            "适量": 50, "很多": 150, "少许": 2
        }
        
        return weight_estimates.get(portion, 50)
    
    def _precompute_common_foods(self):
        """预计算常用食物的热量"""
        common_foods = [
            "米饭", "面条", "馒头", "包子", "饺子", "粥", "面包",
            "鸡蛋", "鸡肉", "猪肉", "牛肉", "鱼肉", "豆腐", "牛奶", "酸奶",
            "白菜", "菠菜", "西兰花", "胡萝卜", "土豆", "西红柿", "黄瓜",
            "苹果", "香蕉", "橙子", "葡萄", "草莓", "西瓜"
        ]
        
        common_portions = ["1小碗", "1中碗", "1大碗", "1个", "2个", "1小块", "2小块", "1杯", "2杯"]
        
        for food in common_foods:
            for portion in common_portions:
                cache_key = f"{food}_{portion}"
                if cache_key not in self.calorie_cache:
                    calories = self._calculate_calories_fast(food, portion)
                    self.calorie_cache[cache_key] = calories
    
    def _calculate_calories_fast(self, food_name: str, portion: str) -> int:
        """快速计算热量（不使用AI）"""
        # 首先尝试精确匹配
        if portion in self.calorie_estimates:
            portion_data = self.calorie_estimates[portion]
            if food_name in portion_data:
                return portion_data[food_name]
            elif "default" in portion_data:
                return portion_data["default"]
        
        # 使用食物数据库估算
        food_info = self.get_food_info(food_name)
        if food_info:
            weight_estimate = self._estimate_weight(portion, food_info["category"])
            calories = int(food_info["calories_per_100g"] * weight_estimate / 100)
            return max(calories, 10)
        
        # 基于食物名称的快速估算
        return self._quick_estimate_by_name(food_name, portion)
    
    def _quick_estimate_by_name(self, food_name: str, portion: str) -> int:
        """基于食物名称的快速估算"""
        # 食物类型快速估算
        if any(keyword in food_name for keyword in ["米饭", "面条", "馒头", "包子", "饺子", "粥", "面包"]):
            base_calories = 200  # 主食基础热量
        elif any(keyword in food_name for keyword in ["鸡蛋", "鸡肉", "猪肉", "牛肉", "鱼肉", "豆腐", "牛奶", "酸奶"]):
            base_calories = 150  # 蛋白质基础热量
        elif any(keyword in food_name for keyword in ["白菜", "菠菜", "西兰花", "胡萝卜", "土豆", "西红柿", "黄瓜"]):
            base_calories = 50   # 蔬菜基础热量
        elif any(keyword in food_name for keyword in ["苹果", "香蕉", "橙子", "葡萄", "草莓", "西瓜"]):
            base_calories = 80   # 水果基础热量
        else:
            base_calories = 100  # 默认基础热量
        
        # 根据分量调整
        portion_multiplier = {
            "1小碗": 0.8, "1中碗": 1.0, "1大碗": 1.5,
            "1个": 0.6, "2个": 1.2, "3个": 1.8,
            "1小块": 0.4, "2小块": 0.8,
            "1杯": 1.0, "2杯": 2.0,
            "适量": 0.8, "很多": 1.5
        }
        
        multiplier = portion_multiplier.get(portion, 1.0)
        return int(base_calories * multiplier)
    
    def _estimate_calories_with_ai(self, food_name: str, portion: str) -> int:
        """使用AI估算食物热量"""
        try:
            from llm_integration.qwen_client import get_qwen_client
            
            client = get_qwen_client()
            
            # 构建AI提示词
            system_prompt = """
你是一个专业的营养师，擅长估算食物的热量和营养成分。

你的任务是：
1. 根据食物名称和分量估算热量
2. 提供准确的营养信息
3. 考虑食物的常见制作方式

请以JSON格式返回结果，包含以下字段：
- calories: 估算的热量值（整数）
- category: 食物分类
- confidence: 置信度(0-1)
- reasoning: 估算理由

注意：
- 热量值应该是整数
- 考虑食物的常见分量
- 基于科学的营养学知识
- 如果不确定，给出保守估算
"""
            
            user_prompt = f"""
请估算以下食物的热量：

食物名称: {food_name}
分量: {portion}

请提供：
1. 估算的热量值（卡路里）
2. 食物分类
3. 估算理由
4. 置信度

请以JSON格式返回结果。
"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = client.chat_completion(messages, temperature=0.2, max_tokens=500)
            
            if response and 'choices' in response:
                content = response['choices'][0]['message']['content']
                result = self._parse_ai_calorie_result(content)
                
                if result.get('success'):
                    calories = result.get('calories', 50)
                    # 将AI估算的食物添加到缓存
                    self._cache_ai_food_info(food_name, result)
                    return max(calories, 10)
                else:
                    print(f"AI解析失败: {result}")
                    return 50
            
        except Exception as e:
            print(f"AI热量估算失败: {e}")
        
        # 如果AI估算失败，返回默认值
        return 50
    
    def _parse_ai_calorie_result(self, content: str) -> Dict:
        """解析AI热量估算结果"""
        try:
            import json
            
            # 尝试提取JSON部分
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                result_dict = json.loads(json_str)
                
                return {
                    'success': True,
                    'calories': int(result_dict.get('calories', 50)),
                    'category': result_dict.get('category', '其他'),
                    'confidence': float(result_dict.get('confidence', 0.5)),
                    'reasoning': result_dict.get('reasoning', 'AI估算')
                }
        except Exception as e:
            print(f"解析AI结果失败: {e}")
        
        return {'success': False, 'calories': 50}
    
    def _cache_ai_food_info(self, food_name: str, ai_result: Dict):
        """缓存AI估算的食物信息"""
        try:
            # 将AI估算的食物添加到内存数据库
            self.food_database[food_name] = {
                "category": ai_result.get('category', '其他'),
                "calories_per_100g": ai_result.get('calories', 50),
                "protein": 0,  # AI暂时不提供详细营养成分
                "carbs": 0,
                "fat": 0,
                "ai_estimated": True,  # 标记为AI估算
                "confidence": ai_result.get('confidence', 0.5)
            }
        except Exception as e:
            print(f"缓存AI食物信息失败: {e}")
    
    def get_food_categories(self) -> List[str]:
        """获取食物分类"""
        return ["主食", "蛋白质", "蔬菜", "水果", "坚果", "饮料", "调料"]
    
    def get_foods_by_category(self, category: str) -> List[str]:
        """根据分类获取食物列表"""
        foods = []
        for food_name, food_info in self.food_database.items():
            if food_info["category"] == category:
                foods.append(food_name)
        return foods
    
    def analyze_food_with_ai(self, food_name: str, portion: str) -> Dict:
        """使用AI分析食物详细信息"""
        try:
            from llm_integration.qwen_client import get_qwen_client
            
            client = get_qwen_client()
            
            # 构建AI提示词
            system_prompt = """
你是一个专业的营养师和食物分析专家，擅长分析食物的营养成分和健康价值。

你的任务是：
1. 分析食物的详细营养成分
2. 估算热量和主要营养素含量
3. 提供健康建议
4. 考虑食物的制作方式

请以JSON格式返回结果，包含以下字段：
- calories: 热量值（整数）
- protein: 蛋白质含量（克）
- carbs: 碳水化合物含量（克）
- fat: 脂肪含量（克）
- fiber: 纤维含量（克）
- category: 食物分类
- health_tips: 健康建议列表
- cooking_suggestions: 制作建议列表
- confidence: 置信度(0-1)
- reasoning: 分析理由

注意：
- 所有数值应该是数字
- 基于科学的营养学知识
- 考虑食物的常见制作方式
- 提供实用的健康建议
"""
            
            user_prompt = f"""
请详细分析以下食物：

食物名称: {food_name}
分量: {portion}

请提供：
1. 详细的营养成分分析
2. 热量和主要营养素含量
3. 食物分类
4. 健康建议
5. 制作建议
6. 分析理由

请以JSON格式返回结果。
"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = client.chat_completion(messages, temperature=0.2, max_tokens=800)
            
            if response and 'choices' in response:
                content = response['choices'][0]['message']['content']
                result = self._parse_ai_food_analysis(content)
                
                if result.get('success'):
                    # 缓存AI分析结果
                    self._cache_ai_food_analysis(food_name, result)
                    return result
                else:
                    print(f"AI食物分析解析失败: {result}")
                    return self._get_fallback_food_analysis(food_name, portion)
            
        except Exception as e:
            print(f"AI食物分析失败: {e}")
        
        # 如果AI分析失败，返回基础估算
        return self._get_fallback_food_analysis(food_name, portion)
    
    def _get_fallback_food_analysis(self, food_name: str, portion: str) -> Dict:
        """获取备用食物分析结果"""
        return {
            'success': False,
            'calories': self.estimate_calories(food_name, portion),
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'fiber': 0,
            'category': '其他',
            'health_tips': ['保持均衡饮食'],
            'cooking_suggestions': ['简单烹饪'],
            'confidence': 0.3,
            'reasoning': '基础估算'
        }
    
    def _parse_ai_food_analysis(self, content: str) -> Dict:
        """解析AI食物分析结果"""
        try:
            import json
            
            # 尝试提取JSON部分
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                result_dict = json.loads(json_str)
                
                return {
                    'success': True,
                    'calories': int(result_dict.get('calories', 50)),
                    'protein': float(result_dict.get('protein', 0)),
                    'carbs': float(result_dict.get('carbs', 0)),
                    'fat': float(result_dict.get('fat', 0)),
                    'fiber': float(result_dict.get('fiber', 0)),
                    'category': result_dict.get('category', '其他'),
                    'health_tips': result_dict.get('health_tips', ['保持均衡饮食']),
                    'cooking_suggestions': result_dict.get('cooking_suggestions', ['简单烹饪']),
                    'confidence': float(result_dict.get('confidence', 0.5)),
                    'reasoning': result_dict.get('reasoning', 'AI分析')
                }
        except Exception as e:
            print(f"解析AI食物分析结果失败: {e}")
        
        return {'success': False}
    
    def _cache_ai_food_analysis(self, food_name: str, analysis_result: Dict):
        """缓存AI食物分析结果"""
        try:
            # 将AI分析的食物添加到内存数据库
            self.food_database[food_name] = {
                "category": analysis_result.get('category', '其他'),
                "calories_per_100g": analysis_result.get('calories', 50),
                "protein": analysis_result.get('protein', 0),
                "carbs": analysis_result.get('carbs', 0),
                "fat": analysis_result.get('fat', 0),
                "fiber": analysis_result.get('fiber', 0),
                "ai_estimated": True,
                "confidence": analysis_result.get('confidence', 0.5),
                "health_tips": analysis_result.get('health_tips', []),
                "cooking_suggestions": analysis_result.get('cooking_suggestions', [])
            }
        except Exception as e:
            print(f"缓存AI食物分析结果失败: {e}")


class SmartMealRecorder:
    """智能餐食记录器"""
    
    def __init__(self):
        self.food_db = SmartFoodDatabase()
    
    def record_meal_smart(self, user_id: str, meal_data: Dict) -> bool:
        """智能记录餐食"""
        try:
            # 自动估算热量
            total_calories = 0
            for food_item in meal_data.get("foods", []):
                food_name = food_item.get("name", "")
                portion = food_item.get("portion", "适量")
                calories = self.food_db.estimate_calories(food_name, portion)
                total_calories += calories
                food_item["estimated_calories"] = calories
            
            # 更新总热量
            meal_data["total_calories"] = total_calories
            
            # 保存到数据库
            from modules.data_collection import record_meal
            return record_meal(user_id, meal_data)
            
        except Exception as e:
            print(f"智能记录餐食失败: {e}")
            return False
    
    def suggest_foods(self, category: str = None) -> List[str]:
        """建议食物"""
        if category:
            return self.food_db.get_foods_by_category(category)
        else:
            # 返回所有食物
            return list(self.food_db.food_database.keys())
    
    def search_foods(self, query: str) -> List[Dict]:
        """搜索食物"""
        return self.food_db.search_foods(query)


# 全局实例
smart_meal_recorder = SmartMealRecorder()


# 便捷函数
def search_foods(query: str) -> List[Dict]:
    """搜索食物"""
    return smart_meal_recorder.search_foods(query)


def get_food_categories() -> List[str]:
    """获取食物分类"""
    return smart_meal_recorder.food_db.get_food_categories()


def get_foods_by_category(category: str) -> List[str]:
    """根据分类获取食物"""
    return smart_meal_recorder.food_db.get_foods_by_category(category)


def get_portion_options(food_name: str) -> List[str]:
    """获取分量选项"""
    return smart_meal_recorder.food_db.get_portion_options(food_name)


def estimate_calories(food_name: str, portion: str) -> int:
    """估算热量"""
    return smart_meal_recorder.food_db.estimate_calories(food_name, portion)


def record_meal_smart(user_id: str, meal_data: Dict) -> bool:
    """智能记录餐食"""
    return smart_meal_recorder.record_meal_smart(user_id, meal_data)


def analyze_food_with_ai(food_name: str, portion: str) -> Dict:
    """使用AI分析食物详细信息"""
    return smart_meal_recorder.food_db.analyze_food_with_ai(food_name, portion)


def get_food_ai_suggestions(food_name: str) -> Dict:
    """获取食物的AI建议"""
    try:
        food_info = smart_meal_recorder.food_db.get_food_info(food_name)
        if food_info and food_info.get('ai_estimated'):
            return {
                'health_tips': food_info.get('health_tips', ['保持均衡饮食']),
                'cooking_suggestions': food_info.get('cooking_suggestions', ['简单烹饪']),
                'confidence': food_info.get('confidence', 0.5)
            }
        else:
            # 如果数据库中没有AI分析结果，进行AI分析
            analysis = analyze_food_with_ai(food_name, "适量")
            return {
                'health_tips': analysis.get('health_tips', ['保持均衡饮食']),
                'cooking_suggestions': analysis.get('cooking_suggestions', ['简单烹饪']),
                'confidence': analysis.get('confidence', 0.5)
            }
    except Exception as e:
        print(f"获取AI建议失败: {e}")
        return {
            'health_tips': ['保持均衡饮食'],
            'cooking_suggestions': ['简单烹饪'],
            'confidence': 0.3
        }


if __name__ == "__main__":
    # 测试智能食物数据库
    print("测试智能食物数据库...")
    
    # 测试搜索
    results = search_foods("鸡")
    print(f"搜索'鸡'的结果: {results}")
    
    # 测试分类
    categories = get_food_categories()
    print(f"食物分类: {categories}")
    
    # 测试分量选项
    portions = get_portion_options("鸡肉")
    print(f"鸡肉的分量选项: {portions}")
    
    # 测试热量估算
    calories = estimate_calories("鸡肉", "1小块")
    print(f"1小块鸡肉的热量: {calories}卡路里")
    
    print("智能食物数据库测试完成！")
