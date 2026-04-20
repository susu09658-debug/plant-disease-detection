"""
实验结果 API 视图

提供以下接口:
  - GET /api/experiment/metrics/       — 获取模型评估指标 (mAP, Precision, Recall 等)
  - GET /api/experiment/curves/        — 获取训练曲线数据 (loss, mAP 随 epoch 变化)
  - GET /api/experiment/model-info/    — 获取当前模型基本信息
  - GET /api/experiment/train-history/ — 获取历史训练记录列表
  - GET /api/experiment/train-config/  — 获取训练配置参数
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
TRAIN_RUNS_DIR = settings.BASE_DIR.parent / 'runs'  / 'detect'/ 'runs' / 'train'
YOLO_CONFIG_DIR = settings.BASE_DIR.parent / 'yolo' / 'configs'


def _get_run_dir(run_name=None):
    """
    根据名称获取指定的训练目录；如果未指定或不存在，则回退到获取最新目录
    """
    if not TRAIN_RUNS_DIR.exists():
        return None

    # 如果指定了 run_name，尝试查找
    if run_name:
        target_dir = TRAIN_RUNS_DIR / run_name
        if target_dir.exists() and target_dir.is_dir():
            return target_dir

    # 默认回退：查找最新
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
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # 接收可选的 run 参数
        run_name = request.GET.get('run')
        run_dir = _get_run_dir(run_name)

        if not run_dir:
            data_config = _get_data_config()
            return Response({
                'code': 200,
                'msg': '暂无训练数据',
                'data': {
                    'metrics': self._demo_metrics(),
                    'train_config': {
                        'model': 'yolo11n.pt',
                        'epochs': 100,
                        'batch': 16,
                        'imgsz': 640,
                        'optimizer': 'SGD',
                        'lr0': 0.01,
                    },
                    'class_names': data_config.get('names', {}),
                    'class_names_cn': data_config.get('names_cn', {}),
                    'num_classes': data_config.get('nc', 0),
                    'charts': {},
                    'run_name': '',
                },
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
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # 接收可选的 run 参数
        run_name = request.GET.get('run')
        run_dir = _get_run_dir(run_name)

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
        data_config = _get_data_config()

        # 获取当前选中的运行记录名称 (例如: 'thesis_optimized')
        run_name = request.GET.get('run')
        run_dir = _get_run_dir(run_name)
        args = _parse_args_yaml(run_dir) if run_dir else {}

        # 项目根目录 (根据你的截图，BASE_DIR.parent 就是 plant-disease-detectio)
        project_root = settings.BASE_DIR.parent

        model_exists = False
        model_path = None
        # 默认展示 args 里的基础预训练模型名，如果有具体的 pt 文件会覆盖它
        display_model_name = args.get('model', 'yolo11n.pt')

        # --- 核心：根据训练记录名称动态拼接模型路径 ---
        if run_name:
            # 方案 A: 你的标准路径 -> 根目录/model/[run_name].pt
            target_path = project_root / 'model' / f'{run_name}.pt'

            # 方案 B: YOLO 默认保存路径 -> runs/.../[run_name]/weights/best.pt
            backup_path = run_dir / 'weights' / 'best.pt' if run_dir else None

            # 优先检查 model 目录下的同名文件
            if target_path.exists():
                model_path = target_path
                model_exists = True
                display_model_name = target_path.name  # 例如: thesis_optimized.pt

            # 其次检查 runs 目录下的 best.pt
            elif backup_path and backup_path.exists():
                model_path = backup_path
                model_exists = True
                display_model_name = f"{run_name} (runs目录下)"

            # 如果都没找到，假定目标路径是 target_path，用于前端排错
            else:
                model_path = target_path
                display_model_name = f"{run_name}.pt (未找到文件)"
        else:
            # 如果没有选择具体的记录，使用全局默认路径
            # 优先级 1：检查 settings.py 中是否明确配置了 YOLO_MODEL_PATH 且文件真实存在
            yolo_path_str = getattr(settings, 'YOLO_MODEL_PATH', None)

            if yolo_path_str and Path(yolo_path_str).exists():
                model_path = Path(yolo_path_str)
                model_exists = True
                display_model_name = model_path.name
            else:
                # 优先级 2：智能扫描项目根目录下的 model 文件夹
                model_dir = project_root / 'model'

                if model_dir.exists() and model_dir.is_dir():
                    # 获取该目录下所有的 .pt 权重文件
                    pt_files = list(model_dir.glob('*.pt'))

                    if pt_files:
                        # 策略：如果文件夹里有多个模型，按文件的最后修改时间排序，自动选择最新放进去的那个
                        pt_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                        model_path = pt_files[0]
                        model_exists = True
                        display_model_name = model_path.name
                    else:
                        # 降级 1：model 文件夹存在，但里面没有 .pt 文件
                        model_path = model_dir / '未找到模型.pt'
                        model_exists = False
                        display_model_name = "未检测到模型文件"
                else:
                    # 降级 2：连 model 文件夹都不存在
                    model_path = project_root / 'model' / '目录不存在.pt'
                    model_exists = False
                    display_model_name = "模型目录缺失"

        # 构造返回给前端的模型信息
        model_info = {
            'model_loaded': model_exists,
            'model_path': str(model_path).replace(str(project_root), ''),  # 截取相对路径，方便前端好看
            'model_version': display_model_name,
            'num_classes': data_config.get('nc', 0),
            'class_names': data_config.get('names', {}),
            'class_names_cn': data_config.get('names_cn', {}),
            'input_size': args.get('imgsz', 640),
        }

        # 如果模型文件真实存在，计算其大小
        if model_exists:
            file_size = model_path.stat().st_size
            model_info['file_size_mb'] = round(file_size / (1024 * 1024), 2)

        # 附加训练相关的基础信息
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


class TrainHistoryView(APIView):
    """获取历史训练记录列表"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        if not TRAIN_RUNS_DIR.exists():
            return Response({
                'code': 200,
                'msg': '暂无训练记录',
                'data': {'runs': []},
            })

        runs = []
        for d in sorted(TRAIN_RUNS_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if not d.is_dir():
                continue

            args = _parse_args_yaml(d)
            rows = _parse_results_csv(d)
            best_weight = d / 'weights' / 'best.pt'
            last_weight = d / 'weights' / 'last.pt'

            # 最终指标
            final_metrics = {}
            if rows:
                last = rows[-1]
                final_metrics = {
                    'mAP50': last.get('metrics/mAP50(B)', 0),
                    'mAP50_95': last.get('metrics/mAP50-95(B)', 0),
                    'precision': last.get('metrics/precision(B)', 0),
                    'recall': last.get('metrics/recall(B)', 0),
                }

            import datetime
            mtime = d.stat().st_mtime
            run_info = {
                'name': d.name,
                'model': args.get('model', ''),
                'epochs': args.get('epochs', 0),
                'epochs_completed': len(rows),
                'batch': args.get('batch', 0),
                'imgsz': args.get('imgsz', 640),
                'optimizer': args.get('optimizer', ''),
                'lr0': args.get('lr0', 0),
                'has_best_weight': best_weight.exists(),
                'has_last_weight': last_weight.exists(),
                'metrics': final_metrics,
                'modified_time': datetime.datetime.fromtimestamp(mtime).isoformat(),
            }

            if best_weight.exists():
                run_info['best_weight_size_mb'] = round(
                    best_weight.stat().st_size / (1024 * 1024), 2)

            runs.append(run_info)

        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {'runs': runs},
        })


class TrainConfigView(APIView):
    """获取/返回推荐的训练配置参数"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # 读取训练配置文件
        config_path = YOLO_CONFIG_DIR / 'train_config.yaml'
        config = {}
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}

        data_config = _get_data_config()

        # 可选的模型列表
        model_options = [
            {'name': 'yolo11n.pt', 'params': '2.6M', 'desc': '超轻量 - 适合快速实验'},
            {'name': 'yolo11s.pt', 'params': '9.4M', 'desc': '轻量 - 平衡精度与速度'},
            {'name': 'yolo11m.pt', 'params': '20.1M', 'desc': '中型 - 较高精度'},
            {'name': 'yolo11l.pt', 'params': '25.3M', 'desc': '大型 - 高精度'},
            {'name': 'yolo11x.pt', 'params': '56.9M', 'desc': '超大 - 最高精度'},
        ]

        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {
                'config': config,
                'model_options': model_options,
                'num_classes': data_config.get('nc', 0),
                'class_names': data_config.get('names', {}),
                'optimizer_options': ['SGD', 'Adam', 'AdamW'],
            }
        })
