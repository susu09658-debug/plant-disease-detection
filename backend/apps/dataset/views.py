"""
数据集管理 API 视图

提供以下接口:
  - GET  /api/dataset/overview/     — 获取数据集概览（数量统计、类别分布）
  - GET  /api/dataset/classes/      — 获取类别列表及各类别样本数
  - GET  /api/dataset/samples/      — 获取指定类别的样本图片
  - GET  /api/dataset/split-info/   — 获取数据集划分信息
  - POST /api/dataset/validate/     — 验证数据集完整性
"""

import os
from collections import Counter
from pathlib import Path

import yaml
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.authentication import JWTAuthentication
from utils.permissions import IsAdminUser

# 数据集根目录
DATASET_DIR = settings.BASE_DIR.parent / 'datasets' / 'plant_disease'
YOLO_CONFIG_DIR = settings.BASE_DIR.parent / 'yolo' / 'configs'


def _get_data_config():
    """读取数据集配置"""
    data_yaml = YOLO_CONFIG_DIR / 'data.yaml'
    if not data_yaml.exists():
        return {}
    with open(data_yaml, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def _count_files(directory, extensions=('*.jpg', '*.jpeg', '*.png', '*.bmp')):
    """统计目录下指定扩展名的文件数"""
    d = Path(directory)
    if not d.exists():
        return 0
    count = 0
    for ext in extensions:
        count += len(list(d.glob(ext)))
    return count


def _get_class_distribution(split='train'):
    """获取指定划分的类别分布"""
    label_dir = DATASET_DIR / 'labels' / split
    if not label_dir.exists():
        return {}

    counter = Counter()
    for label_file in label_dir.glob('*.txt'):
        with open(label_file) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 1:
                    try:
                        class_id = int(parts[0])
                        counter[class_id] += 1
                    except ValueError:
                        continue
    return dict(counter)


class DatasetOverviewView(APIView):
    """获取数据集概览"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        config = _get_data_config()
        class_names = config.get('names', {})
        class_names_cn = config.get('names_cn', {})
        nc = config.get('nc', 0)

        # 统计各划分数量
        splits = {}
        total_images = 0
        total_labels = 0
        for split in ['train', 'val', 'test']:
            img_count = _count_files(DATASET_DIR / 'images' / split)
            lbl_count = _count_files(DATASET_DIR / 'labels' / split, ('*.txt',))
            splits[split] = {
                'images': img_count,
                'labels': lbl_count,
            }
            total_images += img_count
            total_labels += lbl_count

        # 获取训练集类别分布
        class_dist = _get_class_distribution('train')

        # 整合各划分的类别分布
        all_class_dist = {}
        for split in ['train', 'val', 'test']:
            dist = _get_class_distribution(split)
            for cid, count in dist.items():
                if cid not in all_class_dist:
                    all_class_dist[cid] = 0
                all_class_dist[cid] += count

        # 构建类别详情
        class_details = []
        for i in range(nc):
            str_i = str(i)
            class_details.append({
                'id': i,
                'name': class_names.get(i, class_names.get(str_i, f'class_{i}')),
                'name_cn': class_names_cn.get(i, class_names_cn.get(str_i, '')),
                'count': all_class_dist.get(i, 0),
                'train_count': _get_class_distribution('train').get(i, 0),
                'val_count': _get_class_distribution('val').get(i, 0),
                'test_count': _get_class_distribution('test').get(i, 0),
            })

        dataset_exists = total_images > 0

        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {
                'dataset_exists': dataset_exists,
                'dataset_name': 'PlantDoc',
                'dataset_source': 'Kaggle (mrigaankbhatt/plantdoc-dataset)',
                'num_classes': nc,
                'total_images': total_images,
                'total_labels': total_labels,
                'splits': splits,
                'class_details': class_details,
                'class_names': class_names,
                'class_names_cn': class_names_cn,
                'dataset_path': str(DATASET_DIR),
            }
        })


class DatasetClassListView(APIView):
    """获取类别列表及各类别样本数"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        config = _get_data_config()
        class_names = config.get('names', {})
        class_names_cn = config.get('names_cn', {})
        nc = config.get('nc', 0)

        # 获取所有划分的类别分布
        train_dist = _get_class_distribution('train')
        val_dist = _get_class_distribution('val')
        test_dist = _get_class_distribution('test')

        classes = []
        for i in range(nc):
            str_i = str(i)
            train_count = train_dist.get(i, 0)
            val_count = val_dist.get(i, 0)
            test_count = test_dist.get(i, 0)
            classes.append({
                'id': i,
                'name': class_names.get(i, class_names.get(str_i, f'class_{i}')),
                'name_cn': class_names_cn.get(i, class_names_cn.get(str_i, '')),
                'train_count': train_count,
                'val_count': val_count,
                'test_count': test_count,
                'total_count': train_count + val_count + test_count,
            })

        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {
                'num_classes': nc,
                'classes': classes,
            }
        })


class DatasetSamplesView(APIView):
    """获取指定类别/划分的样本图片"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        split = request.query_params.get('split', 'train')
        class_id = request.query_params.get('class_id', None)
        limit = int(request.query_params.get('limit', 20))

        img_dir = DATASET_DIR / 'images' / split
        lbl_dir = DATASET_DIR / 'labels' / split

        if not img_dir.exists():
            return Response({
                'code': 200,
                'msg': '数据集目录不存在',
                'data': {'samples': [], 'total': 0},
            })

        samples = []

        if class_id is not None:
            class_id = int(class_id)
            # 筛选包含指定类别的样本
            for label_file in lbl_dir.glob('*.txt'):
                with open(label_file) as f:
                    has_class = False
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 1 and int(parts[0]) == class_id:
                            has_class = True
                            break
                if has_class:
                    stem = label_file.stem
                    # 查找对应图片
                    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                        img_path = img_dir / (stem + ext)
                        if img_path.exists():
                            samples.append({
                                'filename': img_path.name,
                                'split': split,
                            })
                            break
                if len(samples) >= limit:
                    break
        else:
            # 返回所有样本
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                for img_path in img_dir.glob(ext):
                    samples.append({
                        'filename': img_path.name,
                        'split': split,
                    })
                    if len(samples) >= limit:
                        break
                if len(samples) >= limit:
                    break

        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {
                'samples': samples[:limit],
                'total': len(samples),
                'split': split,
            }
        })


class DatasetSplitInfoView(APIView):
    """获取数据集划分统计"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        splits = {}
        for split in ['train', 'val', 'test']:
            img_dir = DATASET_DIR / 'images' / split
            lbl_dir = DATASET_DIR / 'labels' / split

            img_count = _count_files(img_dir)
            lbl_count = _count_files(lbl_dir, ('*.txt',))

            # 获取图片文件大小信息
            total_size = 0
            if img_dir.exists():
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                    for f in img_dir.glob(ext):
                        total_size += f.stat().st_size

            splits[split] = {
                'images': img_count,
                'labels': lbl_count,
                'size_mb': round(total_size / (1024 * 1024), 2),
                'matched': min(img_count, lbl_count),
            }

        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {'splits': splits},
        })


class DatasetValidateView(APIView):
    """验证数据集完整性"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        config = _get_data_config()
        nc = config.get('nc', 0)
        issues = []
        stats = {}

        for split in ['train', 'val', 'test']:
            img_dir = DATASET_DIR / 'images' / split
            lbl_dir = DATASET_DIR / 'labels' / split

            if not img_dir.exists():
                issues.append(f'{split}/images 目录不存在')
                continue
            if not lbl_dir.exists():
                issues.append(f'{split}/labels 目录不存在')
                continue

            images = set()
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                images.update(p.stem for p in img_dir.glob(ext))

            labels = {p.stem for p in lbl_dir.glob('*.txt')}

            n_images = len(images)
            n_labels = len(labels)
            missing_labels = images - labels
            orphan_labels = labels - images

            stats[split] = {
                'images': n_images,
                'labels': n_labels,
                'matched': len(images & labels),
                'missing_labels': len(missing_labels),
                'orphan_labels': len(orphan_labels),
            }

            if missing_labels:
                issues.append(f'{split}: {len(missing_labels)} 张图片缺少标注')
            if orphan_labels:
                issues.append(f'{split}: {len(orphan_labels)} 个标注无对应图片')

            # 抽样检查标注格式
            checked = 0
            for label_file in lbl_dir.glob('*.txt'):
                if checked >= 100:
                    break
                with open(label_file) as f:
                    for line_num, line in enumerate(f, 1):
                        parts = line.strip().split()
                        if not parts:
                            continue
                        if len(parts) != 5:
                            issues.append(
                                f'{split}/{label_file.name}:{line_num} 格式错误')
                            break
                        try:
                            cid = int(parts[0])
                            if cid < 0 or cid >= nc:
                                issues.append(
                                    f'{split}/{label_file.name}:{line_num} 无效类别 ID: {cid}')
                        except ValueError:
                            issues.append(
                                f'{split}/{label_file.name}:{line_num} 无效类别 ID')
                checked += 1

        is_valid = len(issues) == 0

        return Response({
            'code': 200,
            'msg': '验证完成',
            'data': {
                'is_valid': is_valid,
                'stats': stats,
                'issues': issues[:50],
                'total_issues': len(issues),
            }
        })
