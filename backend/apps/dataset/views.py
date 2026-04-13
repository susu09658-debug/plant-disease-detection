import os
import yaml
from collections import Counter
from pathlib import Path

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.authentication import JWTAuthentication
from utils.permissions import IsAdminUser

# 路径定义
DATASET_DIR = settings.BASE_DIR.parent / 'datasets' / 'plant_disease'
YOLO_CONFIG_DIR = settings.BASE_DIR.parent / 'yolo' / 'configs'

# --- 辅助工具函数 (性能优化版) ---

def _get_data_config():
    """高效读取数据集配置"""
    data_yaml = YOLO_CONFIG_DIR / 'data.yaml'
    if not data_yaml.exists():
        return {}
    try:
        with open(data_yaml, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def _get_dataset_stats(split_list=('train', 'val', 'test')):
    """
    性能核心：一次性扫描所有划分的图片数、标签数和类别分布。
    避免了原代码中多次 glob 导致的 IO 堆积。
    """
    stats = {}
    total_dist = Counter()

    for split in split_list:
        img_dir = DATASET_DIR / 'images' / split
        lbl_dir = DATASET_DIR / 'labels' / split
        
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
    """获取数据集概览 (已优化)"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        config = _get_data_config()
        nc = config.get('nc', 0)
        names = config.get('names', {})
        names_cn = config.get('names_cn', {})

        # 一次性获取全量统计信息
        splits_data, all_dist = _get_dataset_stats()

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
                'dataset_path': str(DATASET_DIR),
            }
        })


class DatasetClassListView(APIView):
    """获取类别列表"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        config = _get_data_config()
        nc = config.get('nc', 0)
        names = config.get('names', {})
        names_cn = config.get('names_cn', {})
        
        _, all_dist = _get_dataset_stats()

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
            'data': {'num_classes': nc, 'classes': classes}
        })


class DatasetSamplesView(APIView):
    """获取样本图片 (增加采样上限，防止大循环)"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        split = request.query_params.get('split', 'train')
        class_id = request.query_params.get('class_id')
        limit = min(int(request.query_params.get('limit', 20)), 100) # 硬上限

        img_dir = DATASET_DIR / 'images' / split
        lbl_dir = DATASET_DIR / 'labels' / split
        
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
        res = {}
        for split in ['train', 'val', 'test']:
            img_dir = DATASET_DIR / 'images' / split
            lbl_dir = DATASET_DIR / 'labels' / split
            
            size_bytes = sum(f.stat().st_size for f in img_dir.glob('*') if f.is_file()) if img_dir.exists() else 0
            img_count = sum(1 for _ in img_dir.iterdir()) if img_dir.exists() else 0
            lbl_count = sum(1 for _ in lbl_dir.iterdir()) if lbl_dir.exists() else 0

            res[split] = {
                'images': img_count,
                'labels': lbl_count,
                'size_mb': round(size_bytes / (1024 * 1024), 2)
            }
        return Response({'code': 200, 'data': {'splits': res}})


class DatasetValidateView(APIView):
    """验证数据集完整性 (Admin Only)"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        # 验证逻辑耗时较长，建议仅在后台小规模运行或手动触发
        config = _get_data_config()
        nc = config.get('nc', 0)
        issues = []
        
        for split in ['train', 'val', 'test']:
            img_dir = DATASET_DIR / 'images' / split
            lbl_dir = DATASET_DIR / 'labels' / split
            if not img_dir.exists() or not lbl_dir.exists():
                issues.append(f"{split} 目录缺失")
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