import os
import yaml
from collections import Counter
from pathlib import Path

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.authentication import JWTAuthentication
from utils.permissions import IsAdminUser


# 移除或者保留作为默认值 fallback
# DATASET_DIR = settings.BASE_DIR.parent / 'datasets' / 'plant_disease'
# YOLO_CONFIG_DIR = settings.BASE_DIR.parent / 'yolo' / 'configs'

def get_dynamic_paths(request):
    """从请求中解析数据集路径，支持 GET (query_params) 和 POST (data)"""
    # 优先尝试从 URL 参数或 POST Body 中获取
    custom_path = request.query_params.get('dataset_path') or request.data.get('dataset_path')

    if custom_path:
        dataset_dir = Path(custom_path)
        # 约定：自定义数据集模式下，data.yaml 就在数据集根目录
        yaml_path = dataset_dir / 'data.yaml'
    else:
        # 默认路径（原硬编码路径）
        dataset_dir = settings.BASE_DIR.parent / 'datasets' / 'plant_disease'
        yaml_path = settings.BASE_DIR.parent / 'yolo' / 'configs' / 'data.yaml'

    return dataset_dir, yaml_path

# --- 辅助工具函数 (性能优化版) ---

def _get_data_config(yaml_path):
    """根据传入的 yaml 路径读取配置"""
    if not yaml_path.exists():
        return {}
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def _get_dataset_stats(dataset_dir, split_list=('train', 'val', 'test')):
    """接收 dataset_dir 动态参数"""
    stats = {}
    total_dist = Counter()

    for split in split_list:
        img_dir = dataset_dir / 'images' / split
        lbl_dir = dataset_dir / 'labels' / split
        
        img_count = 0
        lbl_count = 0
        split_dist = Counter()

        # 统计图片 (快速迭代器)
        if img_dir.exists():
            img_count = sum(1 for f in img_dir.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.bmp'))

        # 统计标签和分布 (合并扫描)
        if lbl_dir.exists():
            for lbl_file in lbl_dir.glob('*.txt'):
                lbl_count += 1
                try:
                    with open(lbl_file, 'r') as f:
                        for line in f:
                            parts = line.strip().split()
                            if parts:
                                cls_id = int(parts[0])
                                split_dist[cls_id] += 1
                                total_dist[cls_id] += 1
                except (ValueError, OSError):
                    continue

        stats[split] = {
            'images': img_count,
            'labels': lbl_count,
            'distribution': dict(split_dist)
        }
    
    return stats, dict(total_dist)


# --- 视图类 ---

class DatasetOverviewView(APIView):
    """获取数据集概览 (修复了动态路径丢失的 Bug)"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # 【修复】必须先解析出动态路径，否则默认读取不到切换后的数据集
        dataset_dir, yaml_path = get_dynamic_paths(request)
        config = _get_data_config(yaml_path)

        nc = config.get('nc', 0)
        names = config.get('names', {})
        names_cn = config.get('names_cn', {})

        # 【修复】将解析出的 dataset_dir 传给统计函数
        splits_data, all_dist = _get_dataset_stats(dataset_dir)

        # 汇总基础数据
        total_images = sum(v['images'] for v in splits_data.values())
        total_labels = sum(v['labels'] for v in splits_data.values())

        # 构建类别详情 (全内存操作)
        class_details = []
        for i in range(nc):
            # 兼容 YOLO 名字格式 (List 或 Dict)
            name = names[i] if isinstance(names, list) else names.get(i, names.get(str(i), f"Class_{i}"))
            name_cn = names_cn.get(i, names_cn.get(str(i), ""))
            
            class_details.append({
                'id': i,
                'name': name,
                'name_cn': name_cn,
                'count': all_dist.get(i, 0),
                'train_count': splits_data['train']['distribution'].get(i, 0),
                'val_count': splits_data['val']['distribution'].get(i, 0),
                'test_count': splits_data['test']['distribution'].get(i, 0),
            })

        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {
                'dataset_exists': total_images > 0,
                'num_classes': nc,
                'total_images': total_images,
                'total_labels': total_labels,
                'splits': splits_data,
                'class_details': class_details,
                'dataset_path': str(dataset_dir),
            }
        })


class DatasetClassListView(APIView):
    """获取类别列表"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        dataset_dir, yaml_path = get_dynamic_paths(request)
        config = _get_data_config(yaml_path)

        nc = config.get('nc', 0)
        names = config.get('names', {})
        names_cn = config.get('names_cn', {})

        # 统计分布也需要基于动态路径
        _, all_dist = _get_dataset_stats(dataset_dir)

        classes = []
        for i in range(nc):
            name = names[i] if isinstance(names, list) else names.get(i, names.get(str(i), f"Class_{i}"))
            classes.append({
                'id': i,
                'name': name,
                'name_cn': names_cn.get(i, names_cn.get(str(i), "")),
                'total_count': all_dist.get(i, 0)
            })

        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {'num_classes': nc, 'classes': classes, 'current_path': str(dataset_dir)}
        })


class DatasetSamplesView(APIView):
    """获取样本图片 (增加采样上限，防止大循环)"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        dataset_dir, _ = get_dynamic_paths(request)  # 采样仅需根目录

        split = request.query_params.get('split', 'train')
        class_id = request.query_params.get('class_id')
        limit = min(int(request.query_params.get('limit', 20)), 100)

        img_dir = dataset_dir / 'images' / split
        lbl_dir = dataset_dir / 'labels' / split
        
        samples = []
        if not img_dir.exists():
            return Response({'code': 200, 'data': {'samples': []}})

        # 如果指定了类别，搜索标签文件
        if class_id is not None:
            target_id = int(class_id)
            # 限制扫描范围，避免全量扫描
            count = 0
            for lbl_file in lbl_dir.glob('*.txt'):
                if count >= limit: break
                with open(lbl_file, 'r') as f:
                    if any(line.startswith(f"{target_id} ") for line in f):
                        # 寻找匹配图片
                        for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                            img_path = img_dir / f"{lbl_file.stem}{ext}"
                            if img_path.exists():
                                samples.append({'filename': img_path.name, 'split': split})
                                count += 1
                                break
        else:
            # 快速随机采样图片
            for f in img_dir.iterdir():
                if len(samples) >= limit: break
                if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.bmp'):
                    samples.append({'filename': f.name, 'split': split})

        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {'samples': samples, 'split': split}
        })


class DatasetSplitInfoView(APIView):
    """获取划分详细信息 (增加文件大小统计)"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        dataset_dir, _ = get_dynamic_paths(request)
        res = {}
        for split in ['train', 'val', 'test']:
            img_dir = dataset_dir / 'images' / split
            lbl_dir = dataset_dir / 'labels' / split

            # 使用动态路径计算大小和数量
            size_bytes = sum(f.stat().st_size for f in img_dir.glob('*') if f.is_file()) if img_dir.exists() else 0
            img_count = sum(1 for _ in img_dir.iterdir()) if img_dir.exists() else 0
            lbl_count = sum(1 for _ in lbl_dir.iterdir()) if lbl_dir.exists() else 0

            res[split] = {
                'images': img_count,
                'labels': lbl_count,
                'size_mb': round(size_bytes / (1024 * 1024), 2)
            }
        return Response({'code': 200, 'data': {'splits': res, 'path': str(dataset_dir)}})


class DatasetValidateView(APIView):
    """验证数据集完整性 (Admin Only)"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        # 注意：POST 请求 get_dynamic_paths 会尝试从 request.data 获取 dataset_path
        dataset_dir, yaml_path = get_dynamic_paths(request)
        config = _get_data_config(yaml_path)

        issues = []
        for split in ['train', 'val', 'test']:
            img_dir = dataset_dir / 'images' / split
            lbl_dir = dataset_dir / 'labels' / split

            if not img_dir.exists() or not lbl_dir.exists():
                issues.append(f"{split} 目录缺失: {img_dir}")
                continue
            
            img_stems = {f.stem for f in img_dir.iterdir()}
            lbl_stems = {f.stem for f in lbl_dir.iterdir() if f.suffix == '.txt'}
            
            # 找不匹配
            missing_lbls = img_stems - lbl_stems
            if missing_lbls:
                issues.append(f"{split}: {len(missing_lbls)} 张图片缺失标签")
        
        return Response({
            'code': 200,
            'msg': '验证完成',
            'data': {'is_valid': len(issues) == 0, 'issues': issues[:20]}
        })


class DatasetListView(APIView):
    """获取 datasets 目录下的所有可用数据集文件夹"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # 根据你的目录结构，datasets 在 BASE_DIR 的上一级
        datasets_root = settings.BASE_DIR.parent / 'datasets'

        dataset_list = []
        if datasets_root.exists() and datasets_root.is_dir():
            for item in datasets_root.iterdir():
                # 只将文件夹加入列表
                if item.is_dir():
                    dataset_list.append({
                        'label': item.name,  # 前端展示的名称，例如 'FieldPlant'
                        'value': str(item.resolve())  # 前端传递的绝对路径
                    })

        return Response({
            'code': 200,
            'msg': '获取成功',
            'data': dataset_list
        })