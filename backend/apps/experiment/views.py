"""
实验结果 API 视图

提供以下接口:
  - GET /api/experiment/metrics/   — 获取模型评估指标 (mAP, Precision, Recall 等)
  - GET /api/experiment/curves/    — 获取训练曲线数据 (loss, mAP 随 epoch 变化)
  - GET /api/experiment/model-info/ — 获取当前模型基本信息
"""

import csv
import os
from pathlib import Path

import yaml
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.authentication import JWTAuthentication

# 训练结果根目录
TRAIN_RUNS_DIR = settings.BASE_DIR.parent / 'runs' / 'train'
YOLO_CONFIG_DIR = settings.BASE_DIR.parent / 'yolo' / 'configs'


def _find_latest_run():
    """查找最新的训练结果目录"""
    if not TRAIN_RUNS_DIR.exists():
        return None
    runs = sorted(
        [d for d in TRAIN_RUNS_DIR.iterdir() if d.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return runs[0] if runs else None


def _parse_results_csv(run_dir):
    """
    解析 ultralytics 训练产生的 results.csv 文件。

    返回每个 epoch 的指标列表。
    """
    csv_path = run_dir / 'results.csv'
    if not csv_path.exists():
        return []

    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = {}
            for k, v in row.items():
                key = k.strip()
                try:
                    cleaned[key] = float(v.strip())
                except (ValueError, AttributeError):
                    cleaned[key] = v.strip() if isinstance(v, str) else v
            rows.append(cleaned)
    return rows


def _parse_args_yaml(run_dir):
    """解析训练参数文件 args.yaml"""
    args_path = run_dir / 'args.yaml'
    if not args_path.exists():
        return {}
    with open(args_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def _get_data_config():
    """读取数据集配置"""
    data_yaml = YOLO_CONFIG_DIR / 'data.yaml'
    if not data_yaml.exists():
        return {}
    with open(data_yaml, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def _collect_images(run_dir):
    """收集训练过程图表的 URL 路径列表"""
    chart_files = [
        'results.png',
        'confusion_matrix.png',
        'confusion_matrix_normalized.png',
        'PR_curve.png',
        'P_curve.png',
        'R_curve.png',
        'F1_curve.png',
        'labels.jpg',
        'labels_correlogram.jpg',
    ]
    images = {}
    for name in chart_files:
        fp = run_dir / name
        if fp.exists():
            # 返回相对于项目根目录的路径标识
            images[name.rsplit('.', 1)[0]] = name
    return images


class ExperimentMetricsView(APIView):
    """获取模型训练/评估的核心指标"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        run_dir = _find_latest_run()
        if not run_dir:
            return Response({
                'code': 200,
                'msg': '暂无训练数据',
                'data': self._demo_metrics(),
            })

        # 解析 CSV 获取最终指标
        rows = _parse_results_csv(run_dir)
        args = _parse_args_yaml(run_dir)
        data_config = _get_data_config()
        images = _collect_images(run_dir)

        if rows:
            last = rows[-1]
            metrics = {
                'mAP50': last.get('metrics/mAP50(B)', 0),
                'mAP50_95': last.get('metrics/mAP50-95(B)', 0),
                'precision': last.get('metrics/precision(B)', 0),
                'recall': last.get('metrics/recall(B)', 0),
                'train_box_loss': last.get('train/box_loss', 0),
                'train_cls_loss': last.get('train/cls_loss', 0),
                'val_box_loss': last.get('val/box_loss', 0),
                'val_cls_loss': last.get('val/cls_loss', 0),
                'epochs_completed': len(rows),
            }
            # 计算 F1：当 P 和 R 均为 0 时 F1 直接置 0
            p = metrics['precision']
            r = metrics['recall']
            metrics['f1_score'] = round(2 * p * r / (p + r), 4) if (p + r) > 0 else 0.0
        else:
            metrics = self._demo_metrics()

        # 训练配置信息
        train_config = {
            'model': args.get('model', 'yolo11n.pt'),
            'epochs': args.get('epochs', 100),
            'batch': args.get('batch', 16),
            'imgsz': args.get('imgsz', 640),
            'optimizer': args.get('optimizer', 'SGD'),
            'lr0': args.get('lr0', 0.01),
        }

        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {
                'metrics': metrics,
                'train_config': train_config,
                'class_names': data_config.get('names', {}),
                'class_names_cn': data_config.get('names_cn', {}),
                'num_classes': data_config.get('nc', 0),
                'charts': images,
                'run_name': run_dir.name,
            }
        })

    @staticmethod
    def _demo_metrics():
        """当没有实际训练数据时，返回演示指标（便于前端开发和展示）"""
        return {
            'mAP50': 0.8742,
            'mAP50_95': 0.6518,
            'precision': 0.8923,
            'recall': 0.8456,
            'f1_score': 0.8683,
            'train_box_loss': 0.0312,
            'train_cls_loss': 0.0245,
            'val_box_loss': 0.0489,
            'val_cls_loss': 0.0367,
            'epochs_completed': 100,
            'is_demo': True,
        }


class ExperimentTrainCurvesView(APIView):
    """获取训练过程曲线数据 (每个 epoch 的指标)"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        run_dir = _find_latest_run()
        if not run_dir:
            return Response({
                'code': 200,
                'msg': '暂无训练数据',
                'data': self._demo_curves(),
            })

        rows = _parse_results_csv(run_dir)
        if not rows:
            return Response({
                'code': 200,
                'msg': '暂无训练数据',
                'data': self._demo_curves(),
            })

        # 提取各曲线数据
        epochs = []
        train_box_loss = []
        train_cls_loss = []
        val_box_loss = []
        val_cls_loss = []
        map50_list = []
        map50_95_list = []
        precision_list = []
        recall_list = []

        for row in rows:
            epoch = row.get('epoch', len(epochs) + 1)
            epochs.append(epoch)
            train_box_loss.append(row.get('train/box_loss', 0))
            train_cls_loss.append(row.get('train/cls_loss', 0))
            val_box_loss.append(row.get('val/box_loss', 0))
            val_cls_loss.append(row.get('val/cls_loss', 0))
            map50_list.append(row.get('metrics/mAP50(B)', 0))
            map50_95_list.append(row.get('metrics/mAP50-95(B)', 0))
            precision_list.append(row.get('metrics/precision(B)', 0))
            recall_list.append(row.get('metrics/recall(B)', 0))

        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {
                'epochs': epochs,
                'train_box_loss': train_box_loss,
                'train_cls_loss': train_cls_loss,
                'val_box_loss': val_box_loss,
                'val_cls_loss': val_cls_loss,
                'mAP50': map50_list,
                'mAP50_95': map50_95_list,
                'precision': precision_list,
                'recall': recall_list,
            }
        })

    @staticmethod
    def _demo_curves():
        """生成演示用曲线数据"""
        import math
        epochs = list(range(1, 101))
        data = {
            'epochs': epochs,
            'train_box_loss': [],
            'train_cls_loss': [],
            'val_box_loss': [],
            'val_cls_loss': [],
            'mAP50': [],
            'mAP50_95': [],
            'precision': [],
            'recall': [],
            'is_demo': True,
        }

        for e in epochs:
            t = e / 100.0
            # 使用指数衰减模拟损失下降，使用 1-exp 模拟精度上升
            data['train_box_loss'].append(round(0.08 * math.exp(-3 * t) + 0.02, 4))
            data['train_cls_loss'].append(round(0.06 * math.exp(-3 * t) + 0.015, 4))
            data['val_box_loss'].append(round(0.10 * math.exp(-2.5 * t) + 0.03, 4))
            data['val_cls_loss'].append(round(0.08 * math.exp(-2.5 * t) + 0.025, 4))
            data['mAP50'].append(round(0.87 * (1 - math.exp(-4 * t)) + 0.005, 4))
            data['mAP50_95'].append(round(0.65 * (1 - math.exp(-3.5 * t)) + 0.002, 4))
            data['precision'].append(round(0.89 * (1 - math.exp(-4.5 * t)) + 0.003, 4))
            data['recall'].append(round(0.85 * (1 - math.exp(-3.8 * t)) + 0.002, 4))

        return data


class ModelInfoView(APIView):
    """获取当前系统使用的模型信息"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        model_path = settings.YOLO_MODEL_PATH
        model_exists = os.path.exists(model_path)

        data_config = _get_data_config()
        run_dir = _find_latest_run()
        args = _parse_args_yaml(run_dir) if run_dir else {}

        # 获取模型文件信息
        model_info = {
            'model_loaded': model_exists,
            'model_path': str(model_path),
            'model_version': args.get('model', 'yolo11n.pt'),
            'num_classes': data_config.get('nc', 0),
            'class_names': data_config.get('names', {}),
            'class_names_cn': data_config.get('names_cn', {}),
            'input_size': args.get('imgsz', 640),
        }

        if model_exists:
            file_size = os.path.getsize(model_path)
            model_info['file_size_mb'] = round(file_size / (1024 * 1024), 2)

        # 有训练记录时附加训练信息
        if run_dir:
            model_info['has_train_records'] = True
            model_info['latest_run'] = run_dir.name
            model_info['train_epochs'] = args.get('epochs', 0)
        else:
            model_info['has_train_records'] = False

        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': model_info,
        })
