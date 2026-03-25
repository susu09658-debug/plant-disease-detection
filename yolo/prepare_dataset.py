"""
植物病害数据集统一准备工具
Unified Plant Disease Dataset Preparation Tool

支持多种数据集格式的自动检测、转换与划分:
  - FieldPlant (Roboflow YOLO 格式，预划分 train/valid/test)
  - FieldPlant (仅 train/ 目录时自动按比例划分为 train/val/test)
  - PlantDoc  (DatasetNinja Supervisely JSON / Pascal VOC XML 格式)

使用说明:
    # FieldPlant 数据集 (YOLO 格式，完整 train/valid/test 划分)
    python yolo/prepare_dataset.py --source /path/to/FieldPlant.v11 --dataset fieldplant

    # FieldPlant 数据集 (仅有 train/ 目录，自动按 80/10/10 划分)
    python yolo/prepare_dataset.py --source /path/to/FieldPlant.v11 --dataset fieldplant

    # 自定义划分比例 (仅 train/ 目录时生效)
    python yolo/prepare_dataset.py --source /path/to/FieldPlant.v11 --train-ratio 0.8 --val-ratio 0.1

    # PlantDoc 数据集 (Supervisely JSON 格式)
    python yolo/prepare_dataset.py --source /path/to/plantdoc_raw --dataset plantdoc

    # 自动检测数据集类型
    python yolo/prepare_dataset.py --source /path/to/dataset

    # 仅验证现有数据集
    python yolo/prepare_dataset.py --validate

    # 显示数据集类别信息
    python yolo/prepare_dataset.py --info

FieldPlant 数据集来源:
    https://universe.roboflow.com/plant-disease-detection/fieldplant/dataset/11

PlantDoc 数据集来源:
    https://datasetninja.com/plantdoc
"""

import argparse
import hashlib
import json
import random
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / 'datasets' / 'plant_disease'

# Windows MAX_PATH 安全阈值
_MAX_SAFE_PATH = 240

# ============================================================
# FieldPlant 数据集定义 (27 类)
# 来源: Roboflow FieldPlant v11
# https://universe.roboflow.com/plant-disease-detection/fieldplant/dataset/11
# ============================================================

FIELDPLANT_CLASSES = [
    'Cassava Bacterial Blight',
    'Cassava Brown Leaf Spot',
    'Cassava Healthy',
    'Cassava Mosaic',
    'Cassava Root Rot',
    'Corn Brown Spots',
    'Corn Charcoal',
    'Corn Chlorotic Leaf Spot',
    'Corn Gray leaf spot',
    'Corn Healthy',
    'Corn Insects Damages',
    'Corn Mildew',
    'Corn Purple Discoloration',
    'Corn Smut',
    'Corn Streak',
    'Corn Stripe',
    'Corn Violet Decoloration',
    'Corn Yellow Spots',
    'Corn Yellowing',
    'Corn leaf blight',
    'Corn rust leaf',
    'Tomato Brown Spots',
    'Tomato bacterial wilt',
    'Tomato blight leaf',
    'Tomato healthy',
    'Tomato leaf mosaic virus',
    'Tomato leaf yellow virus',
]

# ============================================================
# PlantDoc 数据集定义 (29 类)
# 来源: DatasetNinja PlantDoc Dataset
# https://datasetninja.com/plantdoc
# ============================================================

PLANTDOC_CLASSES = [
    'Apple_Scab_Leaf',
    'Apple_leaf',
    'Apple_rust_leaf',
    'Bell_pepper_leaf',
    'Bell_pepper_leaf_spot',
    'Blueberry_leaf',
    'Cherry_leaf',
    'Corn_Gray_leaf_spot',
    'Corn_leaf_blight',
    'Corn_rust_leaf',
    'Grape_leaf',
    'Grape_leaf_black_rot',
    'Peach_leaf',
    'Potato_leaf',
    'Potato_leaf_early_blight',
    'Potato_leaf_late_blight',
    'Raspberry_leaf',
    'Soybean_leaf',
    'Squash_Powdery_mildew_leaf',
    'Strawberry_leaf',
    'Tomato_Early_blight_leaf',
    'Tomato_Septoria_leaf_spot',
    'Tomato_leaf',
    'Tomato_leaf_bacterial_spot',
    'Tomato_leaf_late_blight',
    'Tomato_leaf_mosaic_virus',
    'Tomato_leaf_yellow_virus',
    'Tomato_mold_leaf',
    'Tomato_two_spotted_spider_mites_leaf',
]

# PlantDoc 常见类名变体映射
CLASS_ALIASES = {
    'Apple Scab Leaf': 'Apple_Scab_Leaf',
    'Apple leaf': 'Apple_leaf',
    'Apple rust leaf': 'Apple_rust_leaf',
    'Bell_pepper leaf spot': 'Bell_pepper_leaf_spot',
    'Bell_pepper leaf': 'Bell_pepper_leaf',
    'Bell pepper leaf spot': 'Bell_pepper_leaf_spot',
    'Bell pepper leaf': 'Bell_pepper_leaf',
    'Blueberry leaf': 'Blueberry_leaf',
    'Cherry leaf': 'Cherry_leaf',
    'Corn Gray leaf spot': 'Corn_Gray_leaf_spot',
    'Corn leaf blight': 'Corn_leaf_blight',
    'Corn rust leaf': 'Corn_rust_leaf',
    'Grape Leaf black rot': 'Grape_leaf_black_rot',
    'Grape leaf black rot': 'Grape_leaf_black_rot',
    'grape leaf black rot': 'Grape_leaf_black_rot',
    'Grape leaf': 'Grape_leaf',
    'grape leaf': 'Grape_leaf',
    'Peach leaf': 'Peach_leaf',
    'Potato leaf': 'Potato_leaf',
    'Potato leaf early blight': 'Potato_leaf_early_blight',
    'Potato leaf late blight': 'Potato_leaf_late_blight',
    'Raspberry leaf': 'Raspberry_leaf',
    'Soyabean leaf': 'Soybean_leaf',
    'Soybean leaf': 'Soybean_leaf',
    'Squash Powdery mildew leaf': 'Squash_Powdery_mildew_leaf',
    'Strawberry leaf': 'Strawberry_leaf',
    'Tomato Early blight leaf': 'Tomato_Early_blight_leaf',
    'Tomato Septoria leaf spot': 'Tomato_Septoria_leaf_spot',
    'Tomato leaf': 'Tomato_leaf',
    'Tomato leaf bacterial spot': 'Tomato_leaf_bacterial_spot',
    'Tomato leaf late blight': 'Tomato_leaf_late_blight',
    'Tomato leaf mosaic virus': 'Tomato_leaf_mosaic_virus',
    'Tomato leaf yellow virus': 'Tomato_leaf_yellow_virus',
    'Tomato mold leaf': 'Tomato_mold_leaf',
    'Tomato two spotted spider mites leaf': 'Tomato_two_spotted_spider_mites_leaf',
    'Tomato Two Spotted Spider Mites Leaf': 'Tomato_two_spotted_spider_mites_leaf',
}

# 预构建小写查找表（用于 PlantDoc 大小写不敏感的回退匹配）
_LOWERCASE_ALIASES = {k.lower(): v for k, v in CLASS_ALIASES.items()}
_LOWERCASE_CLASSES = {c.lower(): c for c in PLANTDOC_CLASSES}


# ============================================================
# 数据集类型自动检测
# ============================================================

def detect_dataset_type(source_dir):
    """
    自动检测数据集类型和标注格式。

    Returns:
        str: 'fieldplant' | 'plantdoc_supervisely' | 'plantdoc_voc' | 'unknown'
    """
    source = Path(source_dir)

    # FieldPlant: Roboflow YOLO 格式 (train/images + train/labels 或 data.yaml 存在)
    if _is_roboflow_yolo(source):
        return 'fieldplant'

    # PlantDoc Supervisely: meta.json 或子目录包含 ann/
    if (source / 'meta.json').exists():
        return 'plantdoc_supervisely'
    for subdir in source.iterdir():
        if subdir.is_dir() and (subdir / 'ann').is_dir():
            return 'plantdoc_supervisely'

    # PlantDoc VOC: 包含 XML 文件
    xml_files = list(source.rglob('*.xml'))
    if xml_files:
        return 'plantdoc_voc'

    return 'unknown'


def _is_roboflow_yolo(source):
    """
    检测是否为 Roboflow YOLO 导出格式。

    典型结构:
        dataset/
        ├── data.yaml
        ├── train/
        │   ├── images/
        │   └── labels/
        ├── valid/
        │   ├── images/
        │   └── labels/
        └── test/
            ├── images/
            └── labels/
    """
    # 检查 data.yaml 存在
    if (source / 'data.yaml').exists():
        return True

    # 检查 train/images + train/labels 或 train/images 目录结构
    train_dir = source / 'train'
    if train_dir.is_dir():
        if (train_dir / 'images').is_dir() and (train_dir / 'labels').is_dir():
            return True
        # 也可能只有 images 目录配合外部 labels
        if (train_dir / 'images').is_dir():
            return True

    return False


# ============================================================
# FieldPlant 数据集处理 (YOLO 格式)
# ============================================================

def convert_fieldplant(source_dir, train_ratio=0.8, val_ratio=0.1):
    """
    将 FieldPlant (Roboflow YOLO 格式) 数据集复制到统一目录结构。

    支持两种场景:
      1. 完整划分: 同时存在 train/ + (valid|val)/ + test/ 目录
         → 直接复制到 datasets/plant_disease/{train,val,test}/
      2. 仅有 train/: 只解压了 train/ 目录 (仅含 images/ 和 labels/)
         → 自动按 train_ratio/val_ratio 随机划分为 train/val/test

    Roboflow 导出的 YOLO 格式标注已经是 (class_id cx cy w h)，
    无需格式转换。

    Args:
        source_dir: FieldPlant 数据集根目录
        train_ratio: 训练集比例 (仅在自动划分时使用，默认 0.8)
        val_ratio: 验证集比例 (仅在自动划分时使用，默认 0.1)
    """
    source = Path(source_dir)
    if not source.exists():
        print(f'错误: 源数据集目录不存在: {source}')
        sys.exit(1)

    setup_directories()

    # 检测是否需要自动划分:
    # 仅当 train/ 存在且 valid/val/ 和 test/ 都不存在时自动划分
    has_train = (source / 'train').is_dir()
    has_val = (source / 'valid').is_dir() or (source / 'val').is_dir()
    has_test = (source / 'test').is_dir()

    if has_train and not has_val and not has_test:
        print('  检测到仅有 train/ 目录，将自动划分为 train/val/test')
        _fieldplant_auto_split(source / 'train', train_ratio, val_ratio)
        return

    # 完整划分模式: 直接复制各目录
    # Roboflow 目录名映射: valid -> val
    split_map = {
        'train': ['train'],
        'val': ['valid', 'val'],
        'test': ['test'],
    }

    stats = Counter()
    split_counts = {}

    for target_split, source_names in split_map.items():
        # 查找实际存在的源目录
        src_split_dir = None
        for name in source_names:
            candidate = source / name
            if candidate.is_dir():
                src_split_dir = candidate
                break

        if src_split_dir is None:
            print(f'  警告: 未找到 {target_split} 划分目录，跳过')
            split_counts[target_split] = 0
            continue

        count = _copy_yolo_split(src_split_dir, target_split, stats)
        split_counts[target_split] = count
        print(f'  {target_split}: 已复制 {count} 张图片')

    _print_fieldplant_stats(split_counts, stats)


def _collect_yolo_pairs(split_dir):
    """
    收集 YOLO 格式目录中的 (图片路径, 标注路径) 对。

    Args:
        split_dir: 包含 images/ 和 labels/ 子目录的划分目录

    Returns:
        list: [(img_path, lbl_path), ...] 图片-标注对列表（已去重）
    """
    img_dir = split_dir / 'images'
    lbl_dir = split_dir / 'labels'
    if not img_dir.is_dir():
        return []

    pairs = []
    seen = set()
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG']:
        for img_path in img_dir.glob(ext):
            img_key = img_path.resolve()
            if img_key in seen:
                continue
            seen.add(img_key)
            lbl_path = lbl_dir / (img_path.stem + '.txt')
            # 保留有标注的图片-标注对
            if lbl_path.exists():
                pairs.append((img_path, lbl_path))
    return pairs


def _copy_yolo_split(src_split_dir, target_split, stats):
    """
    复制一个 YOLO 格式划分目录到目标位置。

    Args:
        src_split_dir: 源划分目录 (包含 images/ 和 labels/)
        target_split: 目标划分名 ('train', 'val', 'test')
        stats: Counter 对象，用于统计类别分布

    Returns:
        int: 成功复制的图片数量
    """
    src_img_dir = src_split_dir / 'images'
    src_lbl_dir = src_split_dir / 'labels'

    if not src_img_dir.is_dir():
        print(f'  警告: {src_split_dir}/images/ 目录不存在，跳过')
        return 0

    dst_img_dir = DATASET_DIR / 'images' / target_split
    dst_lbl_dir = DATASET_DIR / 'labels' / target_split

    count = 0
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG']:
        for img_path in src_img_dir.glob(ext):
            # 复制图片
            dst_img = _safe_copy_image(img_path, dst_img_dir)
            if dst_img is None:
                continue

            # 复制对应标注文件
            lbl_name = img_path.stem + '.txt'
            src_lbl = src_lbl_dir / lbl_name
            if src_lbl.exists():
                dst_lbl = dst_lbl_dir / (dst_img.stem + '.txt')
                try:
                    shutil.copy2(src_lbl, dst_lbl)
                except (OSError, shutil.Error) as e:
                    print(f'  警告: 复制标注失败 {lbl_name}: {e}')
                    continue

                _count_yolo_classes(src_lbl, stats)

            count += 1

    return count


def _copy_yolo_pair(img_path, lbl_path, target_split, stats):
    """
    复制单个图片-标注对到目标划分。

    Args:
        img_path: 源图片路径
        lbl_path: 源标注路径
        target_split: 目标划分名 ('train', 'val', 'test')
        stats: Counter 对象

    Returns:
        bool: 是否成功
    """
    dst_img_dir = DATASET_DIR / 'images' / target_split
    dst_lbl_dir = DATASET_DIR / 'labels' / target_split

    dst_img = _safe_copy_image(img_path, dst_img_dir)
    if dst_img is None:
        return False

    dst_lbl = dst_lbl_dir / (dst_img.stem + '.txt')
    try:
        shutil.copy2(lbl_path, dst_lbl)
    except (OSError, shutil.Error) as e:
        print(f'  警告: 复制标注失败 {lbl_path.name}: {e}')
        return False

    _count_yolo_classes(lbl_path, stats)
    return True


def _count_yolo_classes(lbl_path, stats):
    """统计标注文件中的类别分布"""
    with open(lbl_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                try:
                    cid = int(parts[0])
                    if 0 <= cid < len(FIELDPLANT_CLASSES):
                        stats[FIELDPLANT_CLASSES[cid]] += 1
                except ValueError:
                    pass


def _fieldplant_auto_split(train_dir, train_ratio=0.8, val_ratio=0.1):
    """
    当仅有 train/ 目录时，自动将数据划分为 train/val/test。

    随机打乱后按 train_ratio : val_ratio : (1-train_ratio-val_ratio) 比例划分。

    Args:
        train_dir: 源 train/ 目录 (包含 images/ 和 labels/)
        train_ratio: 训练集比例 (默认 0.8)
        val_ratio: 验证集比例 (默认 0.1)
    """
    pairs = _collect_yolo_pairs(train_dir)
    print(f'  找到 {len(pairs)} 对图片-标注')

    if not pairs:
        print('  警告: 没有找到 YOLO 格式的图片-标注对')
        print('  请确保目录结构为: train/images/ + train/labels/')
        return

    # 随机打乱
    random.seed(42)
    random.shuffle(pairs)

    # 按比例划分
    n_total = len(pairs)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)

    splits = {
        'train': pairs[:n_train],
        'val': pairs[n_train:n_train + n_val],
        'test': pairs[n_train + n_val:],
    }

    stats = Counter()
    split_counts = {}

    for split_name, split_pairs in splits.items():
        count = 0
        for img_path, lbl_path in split_pairs:
            if _copy_yolo_pair(img_path, lbl_path, split_name, stats):
                count += 1
        split_counts[split_name] = count
        print(f'  {split_name}: 已复制 {count} 张图片')

    _print_fieldplant_stats(split_counts, stats)


def _print_fieldplant_stats(split_counts, stats):
    """输出 FieldPlant 数据集转换统计信息"""
    print('\n' + '=' * 50)
    print('  FieldPlant 数据集准备完成!')
    print('=' * 50)
    for split, cnt in split_counts.items():
        print(f'  {split}: {cnt} 张')
    print(f'\n  类别分布 (共 {len(stats)} 个类别):')
    for cls_name, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f'    {cls_name}: {count}')
    print(f'\n  数据集保存在: {DATASET_DIR}')


# ============================================================
# PlantDoc 数据集处理 (Supervisely JSON / VOC XML)
# ============================================================

def normalize_class_name(name):
    """标准化 PlantDoc 类名，处理空格、下划线和大小写不一致"""
    name = name.strip()
    if name in CLASS_ALIASES:
        return CLASS_ALIASES[name]
    normalized = name.replace(' ', '_')
    if normalized in PLANTDOC_CLASSES:
        return normalized
    name_lower = name.lower()
    if name_lower in _LOWERCASE_ALIASES:
        return _LOWERCASE_ALIASES[name_lower]
    normalized_lower = normalized.lower()
    if normalized_lower in _LOWERCASE_CLASSES:
        return _LOWERCASE_CLASSES[normalized_lower]
    return name


def get_class_id(class_name):
    """获取 PlantDoc 类名对应的类别 ID"""
    normalized = normalize_class_name(class_name)
    if normalized in PLANTDOC_CLASSES:
        return PLANTDOC_CLASSES.index(normalized)
    return -1


def convert_voc_to_yolo(xml_path, img_width, img_height):
    """将 Pascal VOC XML 标注转换为 YOLO TXT 格式"""
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as e:
        print(f'  警告: XML 文件解析失败 {xml_path}: {e}')
        return []
    root_elem = tree.getroot()
    lines = []

    for obj in root_elem.findall('object'):
        class_name = obj.find('name').text
        class_id = get_class_id(class_name)
        if class_id < 0:
            print(f'  警告: 未知类别 "{class_name}"，跳过')
            continue

        bbox = obj.find('bndbox')
        xmin = float(bbox.find('xmin').text)
        ymin = float(bbox.find('ymin').text)
        xmax = float(bbox.find('xmax').text)
        ymax = float(bbox.find('ymax').text)

        cx = max(0.0, min(1.0, ((xmin + xmax) / 2.0) / img_width))
        cy = max(0.0, min(1.0, ((ymin + ymax) / 2.0) / img_height))
        w = max(0.0, min(1.0, (xmax - xmin) / img_width))
        h = max(0.0, min(1.0, (ymax - ymin) / img_height))

        lines.append(f'{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}')
    return lines


def convert_supervisely_to_yolo(ann_path):
    """将 Supervisely JSON 标注转换为 YOLO TXT 格式"""
    try:
        with open(ann_path, 'r', encoding='utf-8') as f:
            ann_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f'  警告: JSON 文件解析失败 {ann_path}: {e}')
        return []

    img_height = ann_data.get('size', {}).get('height', 0)
    img_width = ann_data.get('size', {}).get('width', 0)
    if img_height <= 0 or img_width <= 0:
        print(f'  警告: 无效的图片尺寸 {ann_path}: {img_width}x{img_height}')
        return []

    lines = []
    for obj in ann_data.get('objects', []):
        class_name = obj.get('classTitle', '')
        class_id = get_class_id(class_name)
        if class_id < 0:
            print(f'  警告: 未知类别 "{class_name}"，跳过')
            continue

        exterior = obj.get('points', {}).get('exterior', [])
        if len(exterior) < 2:
            continue

        xs = [p[0] for p in exterior]
        ys = [p[1] for p in exterior]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)

        cx = max(0.0, min(1.0, ((xmin + xmax) / 2.0) / img_width))
        cy = max(0.0, min(1.0, ((ymin + ymax) / 2.0) / img_height))
        w = max(0.0, min(1.0, (xmax - xmin) / img_width))
        h = max(0.0, min(1.0, (ymax - ymin) / img_height))

        lines.append(f'{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}')
    return lines


def convert_plantdoc(source_dir, train_ratio=0.8, val_ratio=0.1):
    """
    将 PlantDoc 原始数据集转换为 YOLO 格式。

    自动检测标注格式（Supervisely JSON 或 VOC XML）并调用对应转换器。
    如果检测到 DatasetNinja 预划分目录（train/test 各含 img/ann），
    将保留 test 集不变，从 train 中拆分出 val 集。
    """
    source = Path(source_dir)
    if not source.exists():
        print(f'错误: 源数据集目录不存在: {source}')
        sys.exit(1)

    setup_directories()

    ds_type = detect_dataset_type(source)
    if ds_type == 'plantdoc_supervisely':
        if _has_presplit_dirs(source):
            print('  检测到 DatasetNinja 预划分目录结构 (train/test)')
            _convert_supervisely_presplit(source, val_ratio)
        else:
            _convert_supervisely(source, train_ratio, val_ratio)
    elif ds_type == 'plantdoc_voc':
        _convert_voc(source, train_ratio, val_ratio)
    else:
        print('  错误: 无法识别 PlantDoc 数据集标注格式')
        print('  支持的格式: Supervisely JSON, Pascal VOC XML')
        sys.exit(1)


# ============================================================
# 通用工具函数
# ============================================================

def _safe_copy_image(img_path, dst_dir):
    """
    将图片复制到目标目录，处理 Windows MAX_PATH 限制。

    在必要时截断文件名并附加 MD5 哈希后缀以确保唯一性。
    """
    suffix = img_path.suffix
    dst_img = dst_dir / img_path.name

    if len(str(dst_img)) > _MAX_SAFE_PATH:
        name_hash = hashlib.md5(img_path.name.encode()).hexdigest()[:8]
        available_stem = _MAX_SAFE_PATH - len(str(dst_dir)) - 1 - len(suffix) - 9
        truncated_stem = img_path.stem[:max(available_stem, 16)]
        dst_img = dst_dir / f'{truncated_stem}_{name_hash}{suffix}'

    dst_img.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(img_path, dst_img)
    except (OSError, shutil.Error) as e:
        print(f'  警告: 复制图片失败 {img_path.name}: {e}，跳过')
        return None
    return dst_img


def setup_directories():
    """创建 YOLO 数据集目录结构"""
    for split in ['train', 'val', 'test']:
        (DATASET_DIR / 'images' / split).mkdir(parents=True, exist_ok=True)
        (DATASET_DIR / 'labels' / split).mkdir(parents=True, exist_ok=True)
    print('  数据集目录结构已创建')


# ============================================================
# PlantDoc Supervisely 格式内部转换函数
# ============================================================

def _has_presplit_dirs(source):
    """检测是否为 DatasetNinja 预划分格式"""
    train_dir = source / 'train'
    test_dir = source / 'test'
    return (
        train_dir.is_dir()
        and test_dir.is_dir()
        and (train_dir / 'img').is_dir()
        and (train_dir / 'ann').is_dir()
        and (test_dir / 'img').is_dir()
        and (test_dir / 'ann').is_dir()
    )


def _collect_split_pairs(split_dir):
    """收集单个划分目录中的图片-标注对 (已去重)"""
    pairs = []
    seen = set()
    img_dir = split_dir / 'img'
    ann_dir = split_dir / 'ann'
    if not img_dir.is_dir() or not ann_dir.is_dir():
        return pairs
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG']:
        for img_path in img_dir.glob(ext):
            img_key = img_path.resolve()
            if img_key in seen:
                continue
            seen.add(img_key)
            ann_path = ann_dir / (img_path.name + '.json')
            if not ann_path.exists():
                ann_path = ann_dir / (img_path.stem + '.json')
            if ann_path.exists():
                pairs.append((img_path, ann_path))
    return pairs


def _collect_supervisely_pairs(source):
    """收集 Supervisely 格式数据集中的图片-标注对"""
    pairs = []
    seen = set()
    for subdir in sorted(source.iterdir()):
        if not subdir.is_dir():
            continue
        img_dir = subdir / 'img'
        ann_dir = subdir / 'ann'
        if not img_dir.is_dir() or not ann_dir.is_dir():
            continue
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG']:
            for img_path in img_dir.glob(ext):
                img_key = img_path.resolve()
                if img_key in seen:
                    continue
                seen.add(img_key)
                ann_path = ann_dir / (img_path.name + '.json')
                if not ann_path.exists():
                    ann_path = ann_dir / (img_path.stem + '.json')
                if ann_path.exists():
                    pairs.append((img_path, ann_path))
    return pairs


def _convert_supervisely_presplit(source, val_ratio=0.1):
    """转换 DatasetNinja 预划分格式的 Supervisely JSON 数据集"""
    train_pairs = _collect_split_pairs(source / 'train')
    test_pairs = _collect_split_pairs(source / 'test')

    print(f'  原始 train 集: {len(train_pairs)} 对图片-标注')
    print(f'  原始 test 集:  {len(test_pairs)} 对图片-标注')

    if not train_pairs and not test_pairs:
        print('  警告: 没有找到 Supervisely 格式的图片-标注对')
        return

    random.seed(42)
    random.shuffle(train_pairs)

    n_val = int(len(train_pairs) * val_ratio)
    val_pairs = train_pairs[:n_val]
    new_train_pairs = train_pairs[n_val:]

    splits = {'train': new_train_pairs, 'val': val_pairs, 'test': test_pairs}
    stats = Counter()

    for split_name, split_pairs in splits.items():
        print(f'\n  处理 {split_name} 集 ({len(split_pairs)} 张) ...')
        for img_path, ann_path in split_pairs:
            yolo_lines = convert_supervisely_to_yolo(ann_path)
            if not yolo_lines:
                continue
            dst_img = _safe_copy_image(img_path, DATASET_DIR / 'images' / split_name)
            if dst_img is None:
                continue
            dst_label = DATASET_DIR / 'labels' / split_name / (dst_img.stem + '.txt')
            with open(dst_label, 'w') as f:
                f.write('\n'.join(yolo_lines) + '\n')
            for line in yolo_lines:
                class_id = int(line.split()[0])
                stats[PLANTDOC_CLASSES[class_id]] += 1

    _print_conversion_stats(splits, stats)


def _convert_supervisely(source, train_ratio, val_ratio):
    """转换 Supervisely JSON 格式数据集（无预划分时使用）"""
    pairs = _collect_supervisely_pairs(source)
    print(f'  找到 {len(pairs)} 对图片-标注 (Supervisely JSON)')

    if not pairs:
        print('  警告: 没有找到 Supervisely 格式的图片-标注对')
        return

    random.seed(42)
    random.shuffle(pairs)

    n_total = len(pairs)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)

    splits = {
        'train': pairs[:n_train],
        'val': pairs[n_train:n_train + n_val],
        'test': pairs[n_train + n_val:],
    }
    stats = Counter()

    for split_name, split_pairs in splits.items():
        print(f'\n  处理 {split_name} 集 ({len(split_pairs)} 张) ...')
        for img_path, ann_path in split_pairs:
            yolo_lines = convert_supervisely_to_yolo(ann_path)
            if not yolo_lines:
                continue
            dst_img = _safe_copy_image(img_path, DATASET_DIR / 'images' / split_name)
            if dst_img is None:
                continue
            dst_label = DATASET_DIR / 'labels' / split_name / (dst_img.stem + '.txt')
            with open(dst_label, 'w') as f:
                f.write('\n'.join(yolo_lines) + '\n')
            for line in yolo_lines:
                class_id = int(line.split()[0])
                stats[PLANTDOC_CLASSES[class_id]] += 1

    _print_conversion_stats(splits, stats)


def _convert_voc(source, train_ratio, val_ratio):
    """转换 VOC XML 格式数据集"""
    image_files = []
    xml_files = {}

    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG']:
        for img_path in source.rglob(ext):
            image_files.append(img_path)

    for xml_path in source.rglob('*.xml'):
        xml_files[xml_path.stem] = xml_path

    print(f'  找到 {len(image_files)} 张图片')
    print(f'  找到 {len(xml_files)} 个标注文件')

    matched_pairs = []
    for img_path in image_files:
        if img_path.stem in xml_files:
            matched_pairs.append((img_path, xml_files[img_path.stem]))

    print(f'  成功匹配 {len(matched_pairs)} 对图片-标注')

    if not matched_pairs:
        print('  警告: 没有匹配到任何图片-标注对')
        return

    random.seed(42)
    random.shuffle(matched_pairs)

    n_total = len(matched_pairs)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)

    splits = {
        'train': matched_pairs[:n_train],
        'val': matched_pairs[n_train:n_train + n_val],
        'test': matched_pairs[n_train + n_val:],
    }
    stats = Counter()

    for split_name, pairs in splits.items():
        print(f'\n  处理 {split_name} 集 ({len(pairs)} 张) ...')
        for img_path, xml_path in pairs:
            try:
                from PIL import Image
                with Image.open(img_path) as im:
                    img_w, img_h = im.size
            except ImportError:
                print('  错误: 需要安装 Pillow 库来读取图片尺寸')
                print('    pip install pillow')
                sys.exit(1)
            except (OSError, IOError) as e:
                print(f'  警告: 无法读取图片 {img_path}: {e}，跳过')
                continue

            yolo_lines = convert_voc_to_yolo(xml_path, img_w, img_h)
            if not yolo_lines:
                continue

            dst_img = _safe_copy_image(img_path, DATASET_DIR / 'images' / split_name)
            if dst_img is None:
                continue

            dst_label = DATASET_DIR / 'labels' / split_name / (dst_img.stem + '.txt')
            with open(dst_label, 'w') as f:
                f.write('\n'.join(yolo_lines) + '\n')

            for line in yolo_lines:
                class_id = int(line.split()[0])
                stats[PLANTDOC_CLASSES[class_id]] += 1

    _print_conversion_stats(splits, stats)


def _print_conversion_stats(splits, stats):
    """输出数据集转换统计信息"""
    print('\n' + '=' * 50)
    print('  数据集转换完成!')
    print('=' * 50)
    for split_name, pairs in splits.items():
        print(f'  {split_name}: {len(pairs)} 张')
    print(f'\n  类别分布:')
    for cls_name, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f'    {cls_name}: {count}')
    print(f'\n  数据集保存在: {DATASET_DIR}')


# ============================================================
# 数据集验证
# ============================================================

def validate_dataset(dataset_type='fieldplant'):
    """
    验证数据集完整性。

    Args:
        dataset_type: 数据集类型 ('fieldplant' 或 'plantdoc')
    """
    classes = FIELDPLANT_CLASSES if dataset_type == 'fieldplant' else PLANTDOC_CLASSES
    nc = len(classes)

    print(f'\n验证数据集 ({dataset_type}, {nc} 类) ...')

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
        n_matched = len(images & labels)
        missing_labels = images - labels
        orphan_labels = labels - images

        stats[split] = {
            'images': n_images,
            'labels': n_labels,
            'matched': n_matched,
        }

        if missing_labels:
            issues.append(f'{split}: {len(missing_labels)} 张图片缺少标注')
        if orphan_labels:
            issues.append(f'{split}: {len(orphan_labels)} 个标注无对应图片')

        # 检查标注格式
        for label_file in lbl_dir.glob('*.txt'):
            with open(label_file) as f:
                for line_num, line in enumerate(f, 1):
                    parts = line.strip().split()
                    if len(parts) != 5:
                        issues.append(
                            f'{split}/{label_file.name}:{line_num} 格式错误 (期望 5 个值, 得到 {len(parts)})')
                        continue
                    class_id = int(parts[0])
                    if class_id < 0 or class_id >= nc:
                        issues.append(
                            f'{split}/{label_file.name}:{line_num} 无效类别 ID: {class_id}')

    # 输出结果
    print('\n  数据集统计:')
    for split, s in stats.items():
        print(f'    {split}: {s["images"]} 张图片, {s["labels"]} 个标注, {s["matched"]} 已匹配')

    if issues:
        print(f'\n  发现 {len(issues)} 个问题:')
        for issue in issues[:20]:
            print(f'    ⚠ {issue}')
        if len(issues) > 20:
            print(f'    ... 还有 {len(issues) - 20} 个问题')
    else:
        print('\n  ✓ 数据集验证通过，无问题')


# ============================================================
# 数据集信息打印
# ============================================================

def print_dataset_summary(dataset_type='fieldplant'):
    """打印数据集摘要信息"""
    if dataset_type == 'fieldplant':
        classes = FIELDPLANT_CLASSES
        name = 'FieldPlant'
        source = 'https://universe.roboflow.com/plant-disease-detection/fieldplant/dataset/11'
    else:
        classes = PLANTDOC_CLASSES
        name = 'PlantDoc'
        source = 'https://datasetninja.com/plantdoc'

    print('\n' + '=' * 60)
    print(f'  {name} 数据集信息')
    print('=' * 60)
    print(f'  类别数: {len(classes)}')
    print(f'  来源: {source}')
    print(f'  目录: {DATASET_DIR}')
    print('\n  类别列表:')
    for i, cls_name in enumerate(classes):
        print(f'    {i:2d}: {cls_name}')
    print('=' * 60)


# ============================================================
# 命令行入口
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='植物病害数据集统一准备工具 (支持 FieldPlant / PlantDoc)')

    parser.add_argument('--source', type=str,
                        help='数据集源目录路径')
    parser.add_argument('--dataset', type=str, default=None,
                        choices=['fieldplant', 'plantdoc'],
                        help='数据集类型 (fieldplant/plantdoc)，不指定则自动检测')
    parser.add_argument('--validate', action='store_true',
                        help='验证现有数据集')
    parser.add_argument('--train-ratio', type=float, default=0.8,
                        help='训练集比例 (仅在自动划分时使用，默认 0.8)')
    parser.add_argument('--val-ratio', type=float, default=0.1,
                        help='验证集比例 (仅在自动划分时使用，默认 0.1)')
    parser.add_argument('--info', action='store_true',
                        help='显示数据集类别信息')
    return parser.parse_args()


def main():
    args = parse_args()

    # 确定数据集类型
    dataset_type = args.dataset or 'fieldplant'

    if args.info:
        print_dataset_summary(dataset_type)
        return

    if args.validate:
        validate_dataset(dataset_type)
        return

    if args.source:
        source = Path(args.source)
        if not source.exists():
            print(f'错误: 数据集目录不存在: {source}')
            sys.exit(1)

        # 自动检测或使用指定的数据集类型
        if args.dataset:
            ds_type = args.dataset
        else:
            detected = detect_dataset_type(source)
            if detected == 'fieldplant':
                ds_type = 'fieldplant'
            elif detected in ('plantdoc_supervisely', 'plantdoc_voc'):
                ds_type = 'plantdoc'
            else:
                print('  错误: 无法自动识别数据集类型')
                print('  请使用 --dataset fieldplant 或 --dataset plantdoc 手动指定')
                sys.exit(1)
            print(f'  自动检测数据集类型: {ds_type}')

        print(f'\n准备 {ds_type} 数据集...')
        print(f'  源目录: {source}')

        if ds_type == 'fieldplant':
            convert_fieldplant(source, args.train_ratio, args.val_ratio)
        else:
            convert_plantdoc(source, args.train_ratio, args.val_ratio)

        validate_dataset(ds_type)
        return

    # 默认：显示帮助
    print('植物病害数据集统一准备工具')
    print()
    print('支持的数据集:')
    print('  FieldPlant - Roboflow YOLO 格式 (27 类, 木薯/玉米/番茄)')
    print('  PlantDoc   - DatasetNinja Supervisely/VOC 格式 (29 类)')
    print()
    print('用法:')
    print('  # FieldPlant 数据集 (完整 train/valid/test)')
    print('  python yolo/prepare_dataset.py --source /path/to/FieldPlant.v11')
    print()
    print('  # FieldPlant 数据集 (仅有 train/ 目录，自动按 80/10/10 划分)')
    print('  python yolo/prepare_dataset.py --source /path/to/FieldPlant.v11')
    print()
    print('  # 自定义划分比例')
    print('  python yolo/prepare_dataset.py --source /path/to/FieldPlant.v11 --train-ratio 0.8 --val-ratio 0.1')
    print()
    print('  # PlantDoc 数据集 (Supervisely 格式)')
    print('  python yolo/prepare_dataset.py --source /path/to/plantdoc_raw --dataset plantdoc')
    print()
    print('  # 自动检测数据集类型')
    print('  python yolo/prepare_dataset.py --source /path/to/dataset')
    print()
    print('  # 验证现有数据集')
    print('  python yolo/prepare_dataset.py --validate')
    print()
    print('  # 显示类别信息')
    print('  python yolo/prepare_dataset.py --info')
    print('  python yolo/prepare_dataset.py --info --dataset plantdoc')


if __name__ == '__main__':
    main()
