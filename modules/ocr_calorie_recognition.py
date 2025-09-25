"""
图片OCR热量识别模块 - 基于基座架构
支持多种OCR技术识别食物热量信息，包含智能验证和修正机制
"""

import cv2
import numpy as np
import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import requests
import base64
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from core.base import BaseModule, ModuleType, UserData, AnalysisResult, BaseConfig

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """OCR识别结果"""
    text: str
    confidence: float
    bounding_boxes: List[Dict[str, Any]]
    processing_time: float
    method: str


@dataclass
class CalorieInfo:
    """热量信息"""
    food_name: str
    calories: Optional[float]
    serving_size: Optional[str]
    confidence: float
    source: str  # 'ocr', 'database', 'user_confirmed'
    raw_text: str
    validation_status: str  # 'pending', 'validated', 'corrected'


@dataclass
class FoodRecognitionResult:
    """食物识别结果"""
    image_path: str
    ocr_results: List[OCRResult]
    calorie_infos: List[CalorieInfo]
    overall_confidence: float
    processing_time: float
    suggestions: List[str]


class OCRCalorieRecognitionModule(BaseModule):
    """OCR热量识别模块"""
    
    def __init__(self, config: BaseConfig):
        super().__init__(config, ModuleType.DATA_COLLECTION)
        
        # OCR配置
        self.ocr_methods = ['tesseract', 'paddleocr', 'easyocr']
        self.min_confidence = 0.6
        self.max_processing_time = 30.0
        
        # 热量识别模式
        self.calorie_patterns = [
            r'(\d+(?:\.\d+)?)\s*[kK]?[cC][aA][lL](?:ories?)?',
            r'(\d+(?:\.\d+)?)\s*[kK][cC][aA][lL]',
            r'(\d+(?:\.\d+)?)\s*卡路里',
            r'(\d+(?:\.\d+)?)\s*千卡',
            r'(\d+(?:\.\d+)?)\s*大卡',
            r'(\d+(?:\.\d+)?)\s*[kK][jJ]',  # 千焦
        ]
        
        # 食物名称模式
        self.food_patterns = [
            r'([a-zA-Z\u4e00-\u9fff]+)\s*(?:\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*([a-zA-Z\u4e00-\u9fff]+)',
        ]
        
        # 食物数据库
        self.food_database = self._load_food_database()
        
        # 用户学习数据
        self.user_corrections = {}
        
        # 初始化OCR引擎
        self.ocr_engines = {}
        self._initialize_ocr_engines()
    
    def initialize(self) -> bool:
        """初始化模块"""
        try:
            self.logger.info("OCR热量识别模块初始化中...")
            
            # 创建必要的目录
            self._create_directories()
            
            # 加载用户学习数据
            self._load_user_corrections()
            
            self.is_initialized = True
            self.logger.info("OCR热量识别模块初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"OCR热量识别模块初始化失败: {e}")
            return False
    
    def process(self, input_data: Any, user_data: UserData) -> AnalysisResult:
        """处理OCR识别请求"""
        try:
            request_type = input_data.get('type', 'unknown')
            
            if request_type == 'recognize_image':
                result = self._recognize_image_calories(input_data, user_data)
            elif request_type == 'validate_result':
                result = self._validate_recognition_result(input_data, user_data)
            elif request_type == 'learn_correction':
                result = self._learn_from_correction(input_data, user_data)
            else:
                result = self._create_error_result("未知的请求类型")
            
            return AnalysisResult(
                module_type=self.module_type,
                user_id=user_data.user_id,
                input_data=input_data,
                result=result,
                confidence=result.get('confidence', 0.5)
            )
        except Exception as e:
            self.logger.error(f"OCR识别处理失败: {e}")
            return self._create_error_result(f"处理失败: {str(e)}")
    
    def _recognize_image_calories(self, input_data: Dict[str, Any], user_data: UserData) -> Dict[str, Any]:
        """识别图片中的热量信息"""
        start_time = datetime.now()
        
        try:
            image_path = input_data.get('image_path')
            if not image_path or not Path(image_path).exists():
                return self._create_error_result("图片文件不存在")
            
            # 预处理图片
            processed_image = self._preprocess_image(image_path)
            
            # 多OCR引擎识别
            ocr_results = []
            for method in self.ocr_methods:
                try:
                    result = self._ocr_recognize(processed_image, method)
                    if result:
                        ocr_results.append(result)
                except Exception as e:
                    self.logger.warning(f"OCR方法 {method} 失败: {e}")
            
            # 合并和去重OCR结果
            merged_text = self._merge_ocr_results(ocr_results)
            
            # 提取热量信息
            calorie_infos = self._extract_calorie_info(merged_text, user_data)
            
            # 数据库匹配和验证
            validated_infos = self._validate_with_database(calorie_infos, user_data)
            
            # 生成建议
            suggestions = self._generate_suggestions(validated_infos, user_data)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = FoodRecognitionResult(
                image_path=image_path,
                ocr_results=ocr_results,
                calorie_infos=validated_infos,
                overall_confidence=self._calculate_overall_confidence(ocr_results, validated_infos),
                processing_time=processing_time,
                suggestions=suggestions
            )
            
            return {
                'success': True,
                'result': result,
                'confidence': result.overall_confidence,
                'message': f"识别完成，处理时间: {processing_time:.2f}秒"
            }
            
        except Exception as e:
            self.logger.error(f"图片热量识别失败: {e}")
            return self._create_error_result(f"识别失败: {str(e)}")
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """预处理图片以提高OCR准确性"""
        try:
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("无法读取图片")
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 降噪
            denoised = cv2.medianBlur(gray, 3)
            
            # 增强对比度
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # 二值化
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 形态学操作
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            self.logger.error(f"图片预处理失败: {e}")
            return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    def _ocr_recognize(self, image: np.ndarray, method: str) -> Optional[OCRResult]:
        """使用指定方法进行OCR识别"""
        start_time = datetime.now()
        
        try:
            if method == 'tesseract':
                return self._tesseract_ocr(image)
            elif method == 'paddleocr':
                return self._paddleocr_recognize(image)
            elif method == 'easyocr':
                return self._easyocr_recognize(image)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"OCR方法 {method} 失败: {e}")
            return None
    
    def _tesseract_ocr(self, image: np.ndarray) -> OCRResult:
        """使用Tesseract进行OCR识别"""
        try:
            # 配置Tesseract
            config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz\u4e00-\u9fff'
            
            # OCR识别
            text = pytesseract.image_to_string(image, config=config, lang='chi_sim+eng')
            
            # 获取置信度
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=config, lang='chi_sim+eng')
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
            
            # 获取边界框
            bounding_boxes = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:
                    bounding_boxes.append({
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]) / 100.0,
                        'bbox': [data['left'][i], data['top'][i], data['width'][i], data['height'][i]]
                    })
            
            processing_time = (datetime.now() - datetime.now()).total_seconds()
            
            return OCRResult(
                text=text.strip(),
                confidence=avg_confidence,
                bounding_boxes=bounding_boxes,
                processing_time=processing_time,
                method='tesseract'
            )
            
        except Exception as e:
            self.logger.error(f"Tesseract OCR失败: {e}")
            return None
    
    def _paddleocr_recognize(self, image: np.ndarray) -> Optional[OCRResult]:
        """使用PaddleOCR进行识别"""
        try:
            # 这里需要安装paddleocr: pip install paddleocr
            from paddleocr import PaddleOCR
            
            if 'paddleocr' not in self.ocr_engines:
                self.ocr_engines['paddleocr'] = PaddleOCR(use_angle_cls=True, lang='ch')
            
            ocr = self.ocr_engines['paddleocr']
            result = ocr.ocr(image, cls=True)
            
            if not result or not result[0]:
                return None
            
            # 提取文本和置信度
            texts = []
            confidences = []
            bounding_boxes = []
            
            for line in result[0]:
                if line:
                    bbox, (text, confidence) = line
                    texts.append(text)
                    confidences.append(confidence)
                    bounding_boxes.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': bbox
                    })
            
            merged_text = ' '.join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return OCRResult(
                text=merged_text,
                confidence=avg_confidence,
                bounding_boxes=bounding_boxes,
                processing_time=0.0,
                method='paddleocr'
            )
            
        except ImportError:
            self.logger.warning("PaddleOCR未安装，跳过此方法")
            return None
        except Exception as e:
            self.logger.error(f"PaddleOCR识别失败: {e}")
            return None
    
    def _easyocr_recognize(self, image: np.ndarray) -> Optional[OCRResult]:
        """使用EasyOCR进行识别"""
        try:
            # 这里需要安装easyocr: pip install easyocr
            import easyocr
            
            if 'easyocr' not in self.ocr_engines:
                self.ocr_engines['easyocr'] = easyocr.Reader(['ch_sim', 'en'])
            
            reader = self.ocr_engines['easyocr']
            result = reader.readtext(image)
            
            if not result:
                return None
            
            # 提取文本和置信度
            texts = []
            confidences = []
            bounding_boxes = []
            
            for bbox, text, confidence in result:
                texts.append(text)
                confidences.append(confidence)
                bounding_boxes.append({
                    'text': text,
                    'confidence': confidence,
                    'bbox': bbox
                })
            
            merged_text = ' '.join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return OCRResult(
                text=merged_text,
                confidence=avg_confidence,
                bounding_boxes=bounding_boxes,
                processing_time=0.0,
                method='easyocr'
            )
            
        except ImportError:
            self.logger.warning("EasyOCR未安装，跳过此方法")
            return None
        except Exception as e:
            self.logger.error(f"EasyOCR识别失败: {e}")
            return None
    
    def _merge_ocr_results(self, ocr_results: List[OCRResult]) -> str:
        """合并多个OCR结果"""
        if not ocr_results:
            return ""
        
        # 按置信度排序
        sorted_results = sorted(ocr_results, key=lambda x: x.confidence, reverse=True)
        
        # 使用最高置信度的结果作为主要结果
        primary_result = sorted_results[0]
        
        # 如果有多个高置信度结果，尝试合并
        if len(sorted_results) > 1 and sorted_results[1].confidence > 0.7:
            # 简单的文本合并策略
            merged_text = self._smart_text_merge([r.text for r in sorted_results[:3]])
            return merged_text
        
        return primary_result.text
    
    def _smart_text_merge(self, texts: List[str]) -> str:
        """智能文本合并"""
        if not texts:
            return ""
        
        if len(texts) == 1:
            return texts[0]
        
        # 简单的合并策略：选择最长的文本
        return max(texts, key=len)
    
    def _extract_calorie_info(self, text: str, user_data: UserData) -> List[CalorieInfo]:
        """从文本中提取热量信息"""
        calorie_infos = []
        
        try:
            # 查找热量数值
            for pattern in self.calorie_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    calories = float(match.group(1))
                    
                    # 查找对应的食物名称
                    food_name = self._extract_food_name(text, match.start())
                    
                    calorie_info = CalorieInfo(
                        food_name=food_name,
                        calories=calories,
                        serving_size=None,
                        confidence=0.8,  # OCR基础置信度
                        source='ocr',
                        raw_text=match.group(0),
                        validation_status='pending'
                    )
                    
                    calorie_infos.append(calorie_info)
            
            # 如果没有找到热量信息，尝试查找食物名称
            if not calorie_infos:
                food_names = self._extract_all_food_names(text)
                for food_name in food_names:
                    calorie_info = CalorieInfo(
                        food_name=food_name,
                        calories=None,
                        serving_size=None,
                        confidence=0.6,
                        source='ocr',
                        raw_text=food_name,
                        validation_status='pending'
                    )
                    calorie_infos.append(calorie_info)
            
            return calorie_infos
            
        except Exception as e:
            self.logger.error(f"热量信息提取失败: {e}")
            return []
    
    def _extract_food_name(self, text: str, calorie_position: int) -> str:
        """提取食物名称"""
        try:
            # 在热量数值前后查找食物名称
            context_start = max(0, calorie_position - 50)
            context_end = min(len(text), calorie_position + 50)
            context = text[context_start:context_end]
            
            # 查找中文和英文食物名称
            food_pattern = r'([a-zA-Z\u4e00-\u9fff]{2,20})'
            matches = re.findall(food_pattern, context)
            
            if matches:
                # 选择最可能的食物名称
                return matches[0]
            
            return "未知食物"
            
        except Exception as e:
            self.logger.error(f"食物名称提取失败: {e}")
            return "未知食物"
    
    def _extract_all_food_names(self, text: str) -> List[str]:
        """提取所有可能的食物名称"""
        try:
            food_pattern = r'([a-zA-Z\u4e00-\u9fff]{2,20})'
            matches = re.findall(food_pattern, text)
            
            # 去重并过滤
            unique_foods = list(set(matches))
            return unique_foods[:5]  # 最多返回5个
            
        except Exception as e:
            self.logger.error(f"食物名称提取失败: {e}")
            return []
    
    def _validate_with_database(self, calorie_infos: List[CalorieInfo], user_data: UserData) -> List[CalorieInfo]:
        """使用数据库验证热量信息"""
        validated_infos = []
        
        for info in calorie_infos:
            try:
                # 在食物数据库中查找匹配
                db_match = self._find_database_match(info.food_name)
                
                if db_match:
                    # 使用数据库信息更新
                    info.calories = db_match.get('calories', info.calories)
                    info.serving_size = db_match.get('serving_size', info.serving_size)
                    info.confidence = max(info.confidence, 0.9)
                    info.source = 'database'
                
                # 应用用户学习数据
                user_correction = self._get_user_correction(user_data.user_id, info.food_name)
                if user_correction:
                    info.calories = user_correction.get('calories', info.calories)
                    info.confidence = max(info.confidence, 0.95)
                    info.source = 'user_confirmed'
                
                validated_infos.append(info)
                
            except Exception as e:
                self.logger.error(f"数据库验证失败: {e}")
                validated_infos.append(info)
        
        return validated_infos
    
    def _find_database_match(self, food_name: str) -> Optional[Dict[str, Any]]:
        """在数据库中查找食物匹配"""
        try:
            # 精确匹配
            if food_name in self.food_database:
                return self.food_database[food_name]
            
            # 模糊匹配
            for db_food, info in self.food_database.items():
                if food_name in db_food or db_food in food_name:
                    return info
            
            return None
            
        except Exception as e:
            self.logger.error(f"数据库匹配失败: {e}")
            return None
    
    def _get_user_correction(self, user_id: str, food_name: str) -> Optional[Dict[str, Any]]:
        """获取用户修正数据"""
        try:
            user_data = self.user_corrections.get(user_id, {})
            return user_data.get(food_name)
        except Exception as e:
            self.logger.error(f"获取用户修正数据失败: {e}")
            return None
    
    def _generate_suggestions(self, calorie_infos: List[CalorieInfo], user_data: UserData) -> List[str]:
        """生成建议"""
        suggestions = []
        
        try:
            for info in calorie_infos:
                if info.calories is None:
                    suggestions.append(f"未识别到 {info.food_name} 的热量信息，请手动输入")
                elif info.confidence < 0.8:
                    suggestions.append(f"{info.food_name} 的热量 {info.calories} 可能不准确，请确认")
                else:
                    suggestions.append(f"{info.food_name}: {info.calories} 卡路里")
            
            if not calorie_infos:
                suggestions.append("未识别到任何食物信息，请检查图片质量或手动输入")
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"生成建议失败: {e}")
            return ["识别过程中出现错误"]
    
    def _calculate_overall_confidence(self, ocr_results: List[OCRResult], calorie_infos: List[CalorieInfo]) -> float:
        """计算整体置信度"""
        try:
            if not ocr_results and not calorie_infos:
                return 0.0
            
            # OCR置信度
            ocr_confidence = sum(r.confidence for r in ocr_results) / len(ocr_results) if ocr_results else 0.0
            
            # 热量信息置信度
            calorie_confidence = sum(info.confidence for info in calorie_infos) / len(calorie_infos) if calorie_infos else 0.0
            
            # 综合置信度
            overall_confidence = (ocr_confidence * 0.4 + calorie_confidence * 0.6)
            
            return min(overall_confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"计算置信度失败: {e}")
            return 0.0
    
    def _validate_recognition_result(self, input_data: Dict[str, Any], user_data: UserData) -> Dict[str, Any]:
        """验证识别结果"""
        try:
            food_name = input_data.get('food_name')
            calories = input_data.get('calories')
            is_correct = input_data.get('is_correct', True)
            
            if not is_correct:
                # 用户修正
                corrected_calories = input_data.get('corrected_calories')
                self._save_user_correction(user_data.user_id, food_name, corrected_calories)
            
            return {
                'success': True,
                'message': '验证结果已保存',
                'confidence': 1.0
            }
            
        except Exception as e:
            self.logger.error(f"验证识别结果失败: {e}")
            return self._create_error_result(f"验证失败: {str(e)}")
    
    def _learn_from_correction(self, input_data: Dict[str, Any], user_data: UserData) -> Dict[str, Any]:
        """从用户修正中学习"""
        try:
            food_name = input_data.get('food_name')
            corrected_calories = input_data.get('corrected_calories')
            
            self._save_user_correction(user_data.user_id, food_name, corrected_calories)
            
            return {
                'success': True,
                'message': '学习数据已保存',
                'confidence': 1.0
            }
            
        except Exception as e:
            self.logger.error(f"学习修正数据失败: {e}")
            return self._create_error_result(f"学习失败: {str(e)}")
    
    def _save_user_correction(self, user_id: str, food_name: str, calories: float):
        """保存用户修正数据"""
        try:
            if user_id not in self.user_corrections:
                self.user_corrections[user_id] = {}
            
            self.user_corrections[user_id][food_name] = {
                'calories': calories,
                'timestamp': datetime.now().isoformat(),
                'correction_count': self.user_corrections[user_id].get(food_name, {}).get('correction_count', 0) + 1
            }
            
            # 保存到文件
            self._save_user_corrections_to_file()
            
        except Exception as e:
            self.logger.error(f"保存用户修正数据失败: {e}")
    
    def _load_food_database(self) -> Dict[str, Dict[str, Any]]:
        """加载食物数据库"""
        try:
            # 基础食物数据库
            food_db = {
                "米饭": {"calories": 130, "serving_size": "100g"},
                "面条": {"calories": 110, "serving_size": "100g"},
                "馒头": {"calories": 221, "serving_size": "100g"},
                "包子": {"calories": 250, "serving_size": "100g"},
                "饺子": {"calories": 250, "serving_size": "100g"},
                "鸡蛋": {"calories": 155, "serving_size": "100g"},
                "豆腐": {"calories": 76, "serving_size": "100g"},
                "鱼肉": {"calories": 206, "serving_size": "100g"},
                "鸡肉": {"calories": 165, "serving_size": "100g"},
                "瘦肉": {"calories": 250, "serving_size": "100g"},
                "青菜": {"calories": 25, "serving_size": "100g"},
                "西红柿": {"calories": 18, "serving_size": "100g"},
                "胡萝卜": {"calories": 41, "serving_size": "100g"},
                "土豆": {"calories": 77, "serving_size": "100g"},
                "西兰花": {"calories": 34, "serving_size": "100g"},
                "苹果": {"calories": 52, "serving_size": "100g"},
                "香蕉": {"calories": 89, "serving_size": "100g"},
                "橙子": {"calories": 47, "serving_size": "100g"},
                "葡萄": {"calories": 67, "serving_size": "100g"},
                "草莓": {"calories": 32, "serving_size": "100g"},
                "牛奶": {"calories": 42, "serving_size": "100ml"},
                "酸奶": {"calories": 59, "serving_size": "100g"},
                "豆浆": {"calories": 31, "serving_size": "100ml"},
                "坚果": {"calories": 607, "serving_size": "100g"},
                "红枣": {"calories": 264, "serving_size": "100g"},
            }
            
            # 尝试从文件加载扩展数据库
            db_file = Path("data/food_database.json")
            if db_file.exists():
                with open(db_file, 'r', encoding='utf-8') as f:
                    extended_db = json.load(f)
                    food_db.update(extended_db)
            
            return food_db
            
        except Exception as e:
            self.logger.error(f"加载食物数据库失败: {e}")
            return {}
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            'data/ocr_cache',
            'data/user_corrections',
            'data/food_images'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _load_user_corrections(self):
        """加载用户修正数据"""
        try:
            corrections_file = Path("data/user_corrections.json")
            if corrections_file.exists():
                with open(corrections_file, 'r', encoding='utf-8') as f:
                    self.user_corrections = json.load(f)
            else:
                self.user_corrections = {}
        except Exception as e:
            self.logger.error(f"加载用户修正数据失败: {e}")
            self.user_corrections = {}
    
    def _save_user_corrections_to_file(self):
        """保存用户修正数据到文件"""
        try:
            corrections_file = Path("data/user_corrections.json")
            with open(corrections_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_corrections, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存用户修正数据失败: {e}")
    
    def _initialize_ocr_engines(self):
        """初始化OCR引擎"""
        try:
            # 检查Tesseract是否可用
            try:
                pytesseract.get_tesseract_version()
                self.logger.info("Tesseract OCR引擎可用")
            except Exception:
                self.logger.warning("Tesseract OCR引擎不可用")
            
            # 其他OCR引擎将在需要时初始化
            self.logger.info("OCR引擎初始化完成")
            
        except Exception as e:
            self.logger.error(f"OCR引擎初始化失败: {e}")
    
    def _create_error_result(self, message: str) -> Dict[str, Any]:
        """创建错误结果"""
        return {
            'success': False,
            'error': message,
            'confidence': 0.0
        }
    
    def cleanup(self) -> bool:
        """清理资源"""
        try:
            # 保存用户修正数据
            self._save_user_corrections_to_file()
            
            # 清理OCR引擎
            self.ocr_engines.clear()
            
            self.is_initialized = False
            self.logger.info("OCR热量识别模块清理完成")
            return True
        except Exception as e:
            self.logger.error(f"OCR热量识别模块清理失败: {e}")
            return False


if __name__ == "__main__":
    # 测试OCR模块
    from core.base import BaseConfig
    
    config = BaseConfig()
    ocr_module = OCRCalorieRecognitionModule(config)
    
    if ocr_module.initialize():
        print("OCR模块初始化成功")
        
        # 测试图片识别
        test_data = {
            'type': 'recognize_image',
            'image_path': 'test_image.jpg'  # 需要提供测试图片
        }
        
        # 这里需要用户数据，暂时跳过实际测试
        print("OCR模块测试完成")
    else:
        print("OCR模块初始化失败")
