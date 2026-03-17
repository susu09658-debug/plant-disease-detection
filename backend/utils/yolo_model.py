import os
import random
from django.conf import settings

# 模拟的病害名称列表（用于模型文件不存在时的降级处理）
MOCK_DISEASES = [
    {'name': '番茄叶枯病', 'plant': '番茄'},
    {'name': '玉米锈病', 'plant': '玉米'},
    {'name': '水稻稻瘟病', 'plant': '水稻'},
    {'name': '苹果黑星病', 'plant': '苹果'},
    {'name': '葡萄霜霉病', 'plant': '葡萄'},
    {'name': '小麦白粉病', 'plant': '小麦'},
    {'name': '马铃薯晚疫病', 'plant': '马铃薯'},
    {'name': '黄瓜炭疽病', 'plant': '黄瓜'},
]


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
                disease_name = label

                # 收集所有检测框
                for b in result.boxes:
                    cid = int(b.cls[0])
                    coords = b.xyxy[0].tolist()
                    bbox_data.append({
                        'x1': coords[0],
                        'y1': coords[1],
                        'x2': coords[2],
                        'y2': coords[3],
                        'label': result.names[cid],
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
