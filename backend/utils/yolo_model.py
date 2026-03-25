import os
import random
from django.conf import settings

# 模拟的病害名称列表（用于模型文件不存在时的降级处理，基于 FieldPlant 数据集）
MOCK_DISEASES = [
    {'name': '木薯细菌性枯萎病', 'plant': '木薯'},
    {'name': '木薯褐斑病', 'plant': '木薯'},
    {'name': '木薯花叶病', 'plant': '木薯'},
    {'name': '木薯根腐病', 'plant': '木薯'},
    {'name': '玉米褐斑病', 'plant': '玉米'},
    {'name': '玉米灰斑病', 'plant': '玉米'},
    {'name': '玉米虫害', 'plant': '玉米'},
    {'name': '玉米黑穗病', 'plant': '玉米'},
    {'name': '玉米叶枯病', 'plant': '玉米'},
    {'name': '玉米锈病叶', 'plant': '玉米'},
    {'name': '玉米霉病', 'plant': '玉米'},
    {'name': '玉米条纹病', 'plant': '玉米'},
    {'name': '番茄褐斑病', 'plant': '番茄'},
    {'name': '番茄细菌性萎蔫病', 'plant': '番茄'},
    {'name': '番茄疫病叶', 'plant': '番茄'},
    {'name': '番茄花叶病毒', 'plant': '番茄'},
    {'name': '番茄黄化曲叶病毒', 'plant': '番茄'},
]

# 英文类名到中文的映射（与 data.yaml FieldPlant 类别保持一致）
CLASS_NAME_MAP = {
    'Cassava Bacterial Blight': ('木薯细菌性枯萎病', '木薯'),
    'Cassava Brown Leaf Spot': ('木薯褐斑病', '木薯'),
    'Cassava Healthy': ('木薯健康', '木薯'),
    'Cassava Mosaic': ('木薯花叶病', '木薯'),
    'Cassava Root Rot': ('木薯根腐病', '木薯'),
    'Corn Brown Spots': ('玉米褐斑病', '玉米'),
    'Corn Charcoal': ('玉米炭疽病', '玉米'),
    'Corn Chlorotic Leaf Spot': ('玉米褪绿叶斑病', '玉米'),
    'Corn Gray leaf spot': ('玉米灰斑病', '玉米'),
    'Corn Healthy': ('玉米健康', '玉米'),
    'Corn Insects Damages': ('玉米虫害', '玉米'),
    'Corn Mildew': ('玉米霉病', '玉米'),
    'Corn Purple Discoloration': ('玉米紫色变色', '玉米'),
    'Corn Smut': ('玉米黑穗病', '玉米'),
    'Corn Streak': ('玉米条纹病', '玉米'),
    'Corn Stripe': ('玉米条斑病', '玉米'),
    'Corn Violet Decoloration': ('玉米紫罗兰变色', '玉米'),
    'Corn Yellow Spots': ('玉米黄斑病', '玉米'),
    'Corn Yellowing': ('玉米黄化病', '玉米'),
    'Corn leaf blight': ('玉米叶枯病', '玉米'),
    'Corn rust leaf': ('玉米锈病叶', '玉米'),
    'Tomato Brown Spots': ('番茄褐斑病', '番茄'),
    'Tomato bacterial wilt': ('番茄细菌性萎蔫病', '番茄'),
    'Tomato blight leaf': ('番茄疫病叶', '番茄'),
    'Tomato healthy': ('番茄健康', '番茄'),
    'Tomato leaf mosaic virus': ('番茄花叶病毒', '番茄'),
    'Tomato leaf yellow virus': ('番茄黄化曲叶病毒', '番茄'),
}


class YOLOModel:
    """YOLOv11 模型推理工具（支持多模型切换）"""

    _instance = None
    _models = {}         # model_key -> loaded YOLO model
    _current_key = None  # 当前使用的模型 key

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def get_available_models():
        """
        获取可用模型列表。

        扫描 model/ 目录下的 .pt 文件，返回模型信息列表。

        Returns:
            list[dict]: [{'key': 'best', 'name': 'best.pt', 'path': '...', 'size_mb': 5.2}, ...]
        """
        model_dir = settings.YOLO_MODEL_PATH.parent
        models = []
        if model_dir.is_dir():
            for pt_file in sorted(model_dir.glob('*.pt')):
                size_mb = pt_file.stat().st_size / (1024 * 1024)
                if size_mb < 0.01:
                    continue  # 跳过空文件或损坏文件
                key = pt_file.stem  # e.g. 'best', 'yolo11n', 'yolo11s'
                models.append({
                    'key': key,
                    'name': pt_file.name,
                    'path': str(pt_file),
                    'size_mb': round(size_mb, 2),
                })
        # 如果目录为空或不存在，返回默认项
        if not models:
            models.append({
                'key': 'best',
                'name': 'best.pt',
                'path': str(settings.YOLO_MODEL_PATH),
                'size_mb': 0,
            })
        return models

    def _load_model(self, model_key=None):
        """
        懒加载指定模型。

        Args:
            model_key: 模型标识（.pt 文件的 stem 名），为 None 时使用默认模型

        Returns:
            bool: 是否加载成功
        """
        if model_key is None:
            model_key = 'best'

        # 如果已缓存直接返回
        if model_key in self._models:
            self._current_key = model_key
            return True

        # 查找模型文件
        model_dir = settings.YOLO_MODEL_PATH.parent
        model_path = model_dir / f'{model_key}.pt'
        if not model_path.exists():
            # 兼容默认路径
            model_path = settings.YOLO_MODEL_PATH
            if not model_path.exists():
                return False

        try:
            from ultralytics import YOLO
            self._models[model_key] = YOLO(str(model_path))
            self._current_key = model_key
            return True
        except Exception:
            return False

    def detect(self, image_path, model_key=None):
        """
        对输入图片执行病害检测。

        如果模型文件不存在，返回模拟数据（便于开发调试）。

        Args:
            image_path: 图片路径
            model_key: 使用的模型标识（可选，默认使用 best.pt）

        Returns:
            dict: {
                'disease_name': str,
                'plant_name': str,
                'confidence': float,
                'bbox_data': list,
                'result_image_path': str,
                'model_used': str,
            }
        """
        model_loaded = self._load_model(model_key)

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
                'model_used': '模拟数据（模型未加载）',
            }

        try:
            model = self._models[self._current_key]
            results = model(image_path)
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
                'model_used': f'{self._current_key}.pt',
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
                'model_used': '模拟数据（推理异常）',
            }


# 全局单例
yolo_model = YOLOModel()
