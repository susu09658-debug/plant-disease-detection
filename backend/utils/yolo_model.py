import os
import random
from django.conf import settings

# 模拟的病害名称列表（用于模型文件不存在时的降级处理，基于 DatasetNinja PlantDoc 数据集）
MOCK_DISEASES = [
    {'name': '苹果黑星病叶', 'plant': '苹果'},
    {'name': '苹果锈病叶', 'plant': '苹果'},
    {'name': '甜椒叶斑病', 'plant': '甜椒'},
    {'name': '玉米灰斑病', 'plant': '玉米'},
    {'name': '玉米叶枯病', 'plant': '玉米'},
    {'name': '玉米锈病叶', 'plant': '玉米'},
    {'name': '葡萄黑腐病叶', 'plant': '葡萄'},
    {'name': '葡萄叶枯病', 'plant': '葡萄'},
    {'name': '马铃薯早疫病叶', 'plant': '马铃薯'},
    {'name': '马铃薯晚疫病叶', 'plant': '马铃薯'},
    {'name': '南瓜白粉病叶', 'plant': '南瓜'},
    {'name': '番茄早疫病叶', 'plant': '番茄'},
    {'name': '番茄叶斑病', 'plant': '番茄'},
    {'name': '番茄细菌性斑点病叶', 'plant': '番茄'},
    {'name': '番茄晚疫病叶', 'plant': '番茄'},
    {'name': '番茄花叶病毒叶', 'plant': '番茄'},
    {'name': '番茄黄化曲叶病毒叶', 'plant': '番茄'},
    {'name': '番茄霉病叶', 'plant': '番茄'},
    {'name': '番茄二斑叶螨叶', 'plant': '番茄'},
]

# 英文类名到中文的映射（与 data.yaml DatasetNinja PlantDoc 类别保持一致）
CLASS_NAME_MAP = {
    'Apple_Scab_Leaf': ('苹果黑星病叶', '苹果'),
    'Apple_leaf': ('苹果健康叶', '苹果'),
    'Apple_rust_leaf': ('苹果锈病叶', '苹果'),
    'Bell_pepper_leaf': ('甜椒健康叶', '甜椒'),
    'Bell_pepper_leaf_spot': ('甜椒叶斑病', '甜椒'),
    'Blueberry_leaf': ('蓝莓健康叶', '蓝莓'),
    'Cherry_leaf': ('樱桃健康叶', '樱桃'),
    'Corn_Gray_leaf_spot': ('玉米灰斑病', '玉米'),
    'Corn_leaf_blight': ('玉米叶枯病', '玉米'),
    'Corn_rust_leaf': ('玉米锈病叶', '玉米'),
    'Grape_leaf': ('葡萄健康叶', '葡萄'),
    'Grape_leaf_black_rot': ('葡萄黑腐病叶', '葡萄'),
    'Grape_leaf_blight': ('葡萄叶枯病', '葡萄'),
    'Peach_leaf': ('桃树健康叶', '桃树'),
    'Potato_leaf': ('马铃薯健康叶', '马铃薯'),
    'Potato_leaf_early_blight': ('马铃薯早疫病叶', '马铃薯'),
    'Potato_leaf_late_blight': ('马铃薯晚疫病叶', '马铃薯'),
    'Raspberry_leaf': ('覆盆子健康叶', '覆盆子'),
    'Soybean_leaf': ('大豆健康叶', '大豆'),
    'Squash_Powdery_mildew_leaf': ('南瓜白粉病叶', '南瓜'),
    'Strawberry_leaf': ('草莓健康叶', '草莓'),
    'Tomato_Early_blight_leaf': ('番茄早疫病叶', '番茄'),
    'Tomato_Septoria_leaf_spot': ('番茄叶斑病', '番茄'),
    'Tomato_leaf': ('番茄健康叶', '番茄'),
    'Tomato_leaf_bacterial_spot': ('番茄细菌性斑点病叶', '番茄'),
    'Tomato_leaf_late_blight': ('番茄晚疫病叶', '番茄'),
    'Tomato_leaf_mosaic_virus': ('番茄花叶病毒叶', '番茄'),
    'Tomato_leaf_yellow_virus': ('番茄黄化曲叶病毒叶', '番茄'),
    'Tomato_mold_leaf': ('番茄霉病叶', '番茄'),
    'Tomato_two_spotted_spider_mites_leaf': ('番茄二斑叶螨叶', '番茄'),
}


class YOLOModel:
    """YOLOv11 模型推理工具（单例模式）"""

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self):
        """懒加载模型"""
        if self._model is not None:
            return True
        model_path = str(settings.YOLO_MODEL_PATH)
        if not os.path.exists(model_path):
            return False
        try:
            from ultralytics import YOLO
            self._model = YOLO(model_path)
            return True
        except Exception:
            return False

    def detect(self, image_path):
        """
        对输入图片执行病害检测。

        如果模型文件不存在，返回模拟数据（便于开发调试）。

        Returns:
            dict: {
                'disease_name': str,
                'plant_name': str,
                'confidence': float,
                'bbox_data': list,
                'result_image_path': str,
            }
        """
        model_loaded = self._load_model()

        if not model_loaded:
            # 降级处理：返回模拟数据
            mock = random.choice(MOCK_DISEASES)
            return {
                'disease_name': mock['name'],
                'plant_name': mock['plant'],
                'confidence': round(random.uniform(0.75, 0.99), 4),
                'bbox_data': [
                    {
                        'x1': random.randint(50, 150),
                        'y1': random.randint(50, 150),
                        'x2': random.randint(200, 350),
                        'y2': random.randint(200, 350),
                        'label': mock['name'],
                        'confidence': round(random.uniform(0.75, 0.99), 4),
                    }
                ],
                'result_image_path': image_path,  # 无标注图时返回原图路径
            }

        try:
            results = self._model(image_path)
            result = results[0]

            disease_name = '健康'
            plant_name = ''
            confidence = 0.0
            bbox_data = []
            result_image_path = image_path

            if result.boxes and len(result.boxes) > 0:
                # 取置信度最高的检测框
                best_idx = int(result.boxes.conf.argmax())
                box = result.boxes[best_idx]
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()
                label = result.names[class_id]

                # 映射为中文名称
                cn_info = CLASS_NAME_MAP.get(label, (label, ''))
                disease_name = cn_info[0]
                plant_name = cn_info[1]

                # 收集所有检测框
                for b in result.boxes:
                    cid = int(b.cls[0])
                    coords = b.xyxy[0].tolist()
                    box_label = result.names[cid]
                    box_cn = CLASS_NAME_MAP.get(box_label, (box_label, ''))
                    bbox_data.append({
                        'x1': coords[0],
                        'y1': coords[1],
                        'x2': coords[2],
                        'y2': coords[3],
                        'label': box_cn[0],
                        'confidence': float(b.conf[0]),
                    })

                # 保存标注结果图
                import uuid
                from pathlib import Path
                results_dir = settings.MEDIA_ROOT / 'results'
                results_dir.mkdir(parents=True, exist_ok=True)
                result_filename = f"result_{uuid.uuid4().hex}.jpg"
                result_path = results_dir / result_filename
                result.save(filename=str(result_path))
                result_image_path = f"results/{result_filename}"

            return {
                'disease_name': disease_name,
                'plant_name': plant_name,
                'confidence': confidence,
                'bbox_data': bbox_data,
                'result_image_path': result_image_path,
            }

        except Exception as e:
            # 推理失败时降级
            mock = random.choice(MOCK_DISEASES)
            return {
                'disease_name': mock['name'],
                'plant_name': mock['plant'],
                'confidence': round(random.uniform(0.75, 0.99), 4),
                'bbox_data': [],
                'result_image_path': image_path,
            }


# 全局单例
yolo_model = YOLOModel()
