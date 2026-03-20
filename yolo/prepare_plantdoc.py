"""
PlantDoc 数据集准备脚本
PlantDoc Dataset Preparation Script

本脚本用于将 DatasetNinja PlantDoc 数据集转换为 YOLOv11 训练所需的格式。
支持自动下载（从 GitHub Releases）、Supervisely JSON 与 VOC XML 标注格式自动检测、
目录结构转换、标注格式验证和数据集划分。

使用说明:
    # 方式一：已下载数据集并解压到指定目录
    python yolo/prepare_plantdoc.py --source /path/to/plantdoc_raw

    # 方式二：从 DatasetNinja GitHub Releases 自动下载
    python yolo/prepare_plantdoc.py --download

    # 仅验证现有数据集
    python yolo/prepare_plantdoc.py --validate

PlantDoc 数据集来源:
    https://datasetninja.com/plantdoc
    https://github.com/dataset-ninja/PlantDoc/releases
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

# Windows MAX_PATH 安全阈值：路径总长超过此值时截断文件名
# Windows 默认 MAX_PATH = 260，留 20 字符余量
_MAX_SAFE_PATH = 240

# PlantDoc 类别定义（30 个类别，与 data.yaml 保持一致）
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
    'Grape_leaf_blight',
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

# 常见的 PlantDoc 类名变体映射（处理数据集中名称不一致的情况）
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
    'Grape leaf blight': 'Grape_leaf_blight',
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


# 预构建小写查找表，用于大小写不敏感的回退匹配
_LOWERCASE_ALIASES = {k.lower(): v for k, v in CLASS_ALIASES.items()}
_LOWERCASE_CLASSES = {c.lower(): c for c in PLANTDOC_CLASSES}


def normalize_class_name(name):
    """标准化类名，处理空格、下划线和大小写不一致的情况"""
    name = name.strip()
    if name in CLASS_ALIASES:
        return CLASS_ALIASES[name]
    # 尝试用下划线替换空格再匹配
    normalized = name.replace(' ', '_')
    if normalized in PLANTDOC_CLASSES:
        return normalized
    # 大小写不敏感的回退匹配
    name_lower = name.lower()
    if name_lower in _LOWERCASE_ALIASES:
        return _LOWERCASE_ALIASES[name_lower]
    normalized_lower = normalized.lower()
    if normalized_lower in _LOWERCASE_CLASSES:
        return _LOWERCASE_CLASSES[normalized_lower]
    return name


def get_class_id(class_name):
    """获取类名对应的类别 ID"""
    normalized = normalize_class_name(class_name)
    if normalized in PLANTDOC_CLASSES:
        return PLANTDOC_CLASSES.index(normalized)
    return -1


def _safe_copy_image(img_path, dst_dir):
    """
    将图片复制到目标目录，处理 Windows MAX_PATH (260 字符) 限制。

    DatasetNinja 数据集中图片文件名可能非常长（来源于网络爬取的 URL 路径），
    当目标路径总长超过 Windows MAX_PATH (260) 时，_winapi.CopyFile2 会以
    FileNotFoundError: [WinError 3] 失败。本函数在必要时截断文件名并附加
    8 位 MD5 哈希后缀以确保唯一性，同时保留原始扩展名。

    Args:
        img_path: 原始图片路径（Path 对象）
        dst_dir:  目标目录路径（Path 对象，必须已存在）

    Returns:
        Path: 实际写入的目标文件路径；复制失败时返回 None
    """
    suffix = img_path.suffix
    dst_img = dst_dir / img_path.name

    # 路径超过安全阈值时截断文件名（主要针对 Windows MAX_PATH 限制）
    if len(str(dst_img)) > _MAX_SAFE_PATH:
        name_hash = hashlib.md5(img_path.name.encode()).hexdigest()[:8]
        # 可分配给主干的字符数：总阈值 - 目录长度 - 分隔符 - 扩展名 - '_hash'
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


def convert_voc_to_yolo(xml_path, img_width, img_height):
    """
    将 Pascal VOC XML 标注转换为 YOLO TXT 格式。

    Args:
        xml_path: XML 标注文件路径
        img_width: 图片宽度
        img_height: 图片高度

    Returns:
        list: YOLO 格式标注行列表
    """
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

        # 转换为 YOLO 格式（归一化的中心坐标和宽高）
        cx = ((xmin + xmax) / 2.0) / img_width
        cy = ((ymin + ymax) / 2.0) / img_height
        w = (xmax - xmin) / img_width
        h = (ymax - ymin) / img_height

        # 裁剪到 [0, 1] 范围
        cx = max(0.0, min(1.0, cx))
        cy = max(0.0, min(1.0, cy))
        w = max(0.0, min(1.0, w))
        h = max(0.0, min(1.0, h))

        lines.append(f'{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}')

    return lines


def convert_supervisely_to_yolo(ann_path):
    """
    将 Supervisely JSON 标注转换为 YOLO TXT 格式。

    Supervisely JSON 标注结构:
        {
            "size": {"height": H, "width": W},
            "objects": [
                {
                    "classTitle": "Apple Scab Leaf",
                    "points": {"exterior": [[x1,y1],[x2,y2]], "interior": []},
                    ...
                }
            ]
        }

    Args:
        ann_path: Supervisely JSON 标注文件路径

    Returns:
        list: YOLO 格式标注行列表
    """
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

        # 从多边形点集中提取边界框
        xs = [p[0] for p in exterior]
        ys = [p[1] for p in exterior]
        xmin = min(xs)
        ymin = min(ys)
        xmax = max(xs)
        ymax = max(ys)

        # 转换为 YOLO 格式（归一化的中心坐标和宽高）
        cx = ((xmin + xmax) / 2.0) / img_width
        cy = ((ymin + ymax) / 2.0) / img_height
        w = (xmax - xmin) / img_width
        h = (ymax - ymin) / img_height

        # 裁剪到 [0, 1] 范围
        cx = max(0.0, min(1.0, cx))
        cy = max(0.0, min(1.0, cy))
        w = max(0.0, min(1.0, w))
        h = max(0.0, min(1.0, h))

        lines.append(f'{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}')

    return lines


def detect_annotation_format(source_dir):
    """
    自动检测数据集的标注格式。

    Returns:
        str: 'supervisely' | 'voc' | 'unknown'
    """
    source = Path(source_dir)

    # 检查是否存在 meta.json（Supervisely 格式标志）
    if (source / 'meta.json').exists():
        return 'supervisely'

    # 检查子目录中是否有 ann/ 目录（Supervisely 格式）
    for subdir in source.iterdir():
        if subdir.is_dir() and (subdir / 'ann').is_dir():
            return 'supervisely'

    # 检查是否有 XML 文件（VOC 格式）
    xml_files = list(source.rglob('*.xml'))
    if xml_files:
        return 'voc'

    return 'unknown'


def setup_directories():
    """创建 YOLO 数据集目录结构"""
    for split in ['train', 'val', 'test']:
        (DATASET_DIR / 'images' / split).mkdir(parents=True, exist_ok=True)
        (DATASET_DIR / 'labels' / split).mkdir(parents=True, exist_ok=True)
    print('  数据集目录结构已创建')


def _collect_supervisely_pairs(source):
    """
    收集 Supervisely 格式数据集中的图片-标注对。

    Supervisely 目录结构:
        dataset/
        ├── meta.json
        ├── train/
        │   ├── img/
        │   └── ann/
        └── test/
            ├── img/
            └── ann/

    Returns:
        list: [(img_path, ann_path), ...] 图片-标注对列表（已去重）
    """
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
                # 用 resolve() 规范化路径，避免在 Windows 大小写不敏感文件系统上重复收集
                img_key = img_path.resolve()
                if img_key in seen:
                    continue
                seen.add(img_key)
                # Supervisely JSON: 原图文件名.json (e.g. img.jpg -> img.jpg.json)
                # 也兼容 stem.json 格式 (e.g. img.jpg -> img.json)
                ann_path = ann_dir / (img_path.name + '.json')
                if not ann_path.exists():
                    ann_path = ann_dir / (img_path.stem + '.json')
                if ann_path.exists():
                    pairs.append((img_path, ann_path))
    return pairs


def _has_presplit_dirs(source):
    """
    检测是否为 DatasetNinja 预划分格式（train/test 子目录各含 img/ann）。

    DatasetNinja 下载解压后的目录结构:
        plantdoc-DatasetNinja/
        ├── train/
        │   ├── img/
        │   └── ann/
        └── test/
            ├── img/
            └── ann/

    Returns:
        bool: True 表示检测到预划分目录结构
    """
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


def convert_dataset(source_dir, train_ratio=0.8, val_ratio=0.1):
    """
    将 PlantDoc 原始数据集转换为 YOLO 格式。

    自动检测标注格式（Supervisely JSON 或 VOC XML）并调用对应转换器。
    如果检测到 DatasetNinja 预划分目录（train/test 各含 img/ann），
    将保留 test 集不变，从 train 中拆分出 val 集。

    Args:
        source_dir: 原始数据集目录
        train_ratio: 训练集比例（仅在无预划分时使用）
        val_ratio: 验证集比例（预划分时从原 train 中拆分的比例）
    """
    source = Path(source_dir)
    if not source.exists():
        print(f'错误: 源数据集目录不存在: {source}')
        sys.exit(1)

    setup_directories()

    # 自动检测标注格式
    ann_format = detect_annotation_format(source)
    print(f'  检测到标注格式: {ann_format}')

    if ann_format == 'supervisely':
        if _has_presplit_dirs(source):
            print('  检测到 DatasetNinja 预划分目录结构 (train/test)')
            _convert_supervisely_presplit(source, val_ratio)
        else:
            _convert_supervisely(source, train_ratio, val_ratio)
    elif ann_format == 'voc':
        _convert_voc(source, train_ratio, val_ratio)
    else:
        print('  错误: 无法识别数据集标注格式')
        print('  支持的格式: Supervisely JSON, Pascal VOC XML')
        sys.exit(1)


def _collect_split_pairs(split_dir):
    """
    收集单个划分目录（如 train/ 或 test/）中的图片-标注对。

    在 Windows 大小写不敏感的文件系统上，同时匹配 *.jpg 和 *.JPG 等模式
    会返回同一文件的重复路径。此函数通过 resolve() 规范化路径去重，
    确保每张图片只被收集一次。

    Args:
        split_dir: 包含 img/ 和 ann/ 的目录

    Returns:
        list: [(img_path, ann_path), ...] 图片-标注对列表（已去重）
    """
    pairs = []
    seen = set()
    img_dir = split_dir / 'img'
    ann_dir = split_dir / 'ann'
    if not img_dir.is_dir() or not ann_dir.is_dir():
        return pairs
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG']:
        for img_path in img_dir.glob(ext):
            # 用 resolve() 规范化路径，避免在 Windows 大小写不敏感文件系统上重复收集
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
    """
    转换 DatasetNinja 预划分格式的 Supervisely JSON 数据集。

    保留原始 test 集不变，从原始 train 集中拆分出 val 集。

    Args:
        source: DatasetNinja 数据集根目录
        val_ratio: 从 train 中拆分为 val 的比例
    """
    train_pairs = _collect_split_pairs(source / 'train')
    test_pairs = _collect_split_pairs(source / 'test')

    print(f'  原始 train 集: {len(train_pairs)} 对图片-标注')
    print(f'  原始 test 集:  {len(test_pairs)} 对图片-标注')

    if not train_pairs and not test_pairs:
        print('  警告: 没有找到 Supervisely 格式的图片-标注对')
        print('  请确保目录结构为: train/img/, train/ann/, test/img/, test/ann/')
        return

    # 从 train 中拆分 val
    random.seed(42)
    random.shuffle(train_pairs)

    n_val = int(len(train_pairs) * val_ratio)
    val_pairs = train_pairs[:n_val]
    new_train_pairs = train_pairs[n_val:]

    splits = {
        'train': new_train_pairs,
        'val': val_pairs,
        'test': test_pairs,
    }

    stats = Counter()

    for split_name, split_pairs in splits.items():
        print(f'\n  处理 {split_name} 集 ({len(split_pairs)} 张) ...')
        for img_path, ann_path in split_pairs:
            yolo_lines = convert_supervisely_to_yolo(ann_path)
            if not yolo_lines:
                continue

            # 复制图片（自动处理长文件名导致的 Windows MAX_PATH 限制）
            dst_img = _safe_copy_image(img_path, DATASET_DIR / 'images' / split_name)
            if dst_img is None:
                continue

            # 写入标注（使用实际写入的目标文件主干，与可能被截断的文件名保持一致）
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
        print('  请确保目录结构为: <split>/img/ 和 <split>/ann/')
        return

    # 随机打乱并划分数据集
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

            # 复制图片（自动处理长文件名导致的 Windows MAX_PATH 限制）
            dst_img = _safe_copy_image(img_path, DATASET_DIR / 'images' / split_name)
            if dst_img is None:
                continue

            # 写入标注（使用实际写入的目标文件主干，与可能被截断的文件名保持一致）
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
        stem = xml_path.stem
        xml_files[stem] = xml_path

    print(f'  找到 {len(image_files)} 张图片')
    print(f'  找到 {len(xml_files)} 个标注文件')

    matched_pairs = []
    for img_path in image_files:
        stem = img_path.stem
        if stem in xml_files:
            matched_pairs.append((img_path, xml_files[stem]))

    print(f'  成功匹配 {len(matched_pairs)} 对图片-标注')

    if not matched_pairs:
        print('  警告: 没有匹配到任何图片-标注对')
        print('  请确保图片和 XML 标注文件名称一致')
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


def validate_dataset():
    """验证数据集完整性"""
    print('\n验证数据集...')

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
                    if class_id < 0 or class_id >= len(PLANTDOC_CLASSES):
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


def download_dataset():
    """从 DatasetNinja GitHub Releases 下载 PlantDoc 数据集"""
    import subprocess
    import urllib.request
    import zipfile

    print('正在从 DatasetNinja GitHub Releases 下载 PlantDoc 数据集...\n')

    download_dir = ROOT / 'datasets' / 'plantdoc_raw'
    download_dir.mkdir(parents=True, exist_ok=True)

    release_url = 'https://github.com/dataset-ninja/PlantDoc/releases'

    try:
        # 查询最新 release 信息
        api_url = 'https://api.github.com/repos/dataset-ninja/PlantDoc/releases/latest'
        print(f'  查询最新版本: {api_url}')

        req = urllib.request.Request(
            api_url, headers={'Accept': 'application/vnd.github+json'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            release_info = json.loads(resp.read().decode())

        assets = release_info.get('assets', [])
        tarball_url = release_info.get('tarball_url', '')

        # 优先下载 release assets（如果有 zip/tar 文件）
        download_url = None
        archive_path = None
        for asset in assets:
            name = asset.get('name', '')
            if name.endswith(('.zip', '.tar', '.tar.gz')):
                download_url = asset['browser_download_url']
                archive_path = download_dir / name
                break

        if not download_url and tarball_url:
            download_url = tarball_url
            archive_path = download_dir / 'PlantDoc.tar.gz'

        if download_url and archive_path:
            print(f'  下载地址: {download_url}')
            urllib.request.urlretrieve(download_url, str(archive_path))

            if not archive_path.exists():
                raise RuntimeError(f'下载后文件不存在: {archive_path}')

            print(f'  下载完成: {archive_path}')

            # 解压
            if str(archive_path).endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(download_dir)
            else:
                result = subprocess.run(
                    ['tar', 'xf', str(archive_path), '-C', str(download_dir)],
                    capture_output=True, text=True,
                )
                if result.returncode != 0:
                    raise RuntimeError(f'解压失败: {result.stderr}')

            print(f'  解压完成: {download_dir}')
            return str(download_dir)

    except Exception as e:
        print(f'  自动下载失败: {e}')

    print('\n  自动下载未成功，请手动下载:')
    print(f'  1. 访问 {release_url}')
    print('     或 https://datasetninja.com/plantdoc')
    print(f'  2. 下载并解压到 {download_dir}/')
    print(f'  3. 运行: python yolo/prepare_plantdoc.py --source {download_dir}')
    sys.exit(1)


def print_dataset_summary():
    """打印数据集摘要信息"""
    print('\n' + '=' * 60)
    print('  PlantDoc 数据集信息 (DatasetNinja)')
    print('=' * 60)
    print(f'  类别数: {len(PLANTDOC_CLASSES)}')
    print(f'  来源: https://datasetninja.com/plantdoc')
    print(f'  目录: {DATASET_DIR}')
    print('\n  类别列表:')
    for i, name in enumerate(PLANTDOC_CLASSES):
        print(f'    {i:2d}: {name}')
    print('=' * 60)


def parse_args():
    parser = argparse.ArgumentParser(description='PlantDoc 数据集准备工具')
    parser.add_argument('--source', type=str, help='PlantDoc 原始数据集目录路径')
    parser.add_argument('--download', action='store_true',
                        help='从 DatasetNinja GitHub Releases 下载数据集')
    parser.add_argument('--validate', action='store_true', help='验证现有数据集')
    parser.add_argument('--train-ratio', type=float, default=0.8, help='训练集比例')
    parser.add_argument('--val-ratio', type=float, default=0.1, help='验证集比例')
    parser.add_argument('--info', action='store_true', help='显示数据集类别信息')
    return parser.parse_args()


def main():
    args = parse_args()

    if args.info:
        print_dataset_summary()
        return

    if args.validate:
        validate_dataset()
        return

    if args.download:
        source = download_dataset()
        convert_dataset(source, args.train_ratio, args.val_ratio)
        validate_dataset()
        return

    if args.source:
        convert_dataset(args.source, args.train_ratio, args.val_ratio)
        validate_dataset()
        return

    # 默认：显示帮助
    print('PlantDoc 数据集准备工具 (DatasetNinja)')
    print()
    print('用法:')
    print('  python yolo/prepare_plantdoc.py --source /path/to/plantdoc_raw')
    print('  python yolo/prepare_plantdoc.py --download')
    print('  python yolo/prepare_plantdoc.py --validate')
    print('  python yolo/prepare_plantdoc.py --info')


if __name__ == '__main__':
    main()
