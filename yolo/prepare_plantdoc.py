"""
PlantDoc 数据集准备脚本
PlantDoc Dataset Preparation Script

本脚本用于将 Kaggle PlantDoc 数据集转换为 YOLOv11 训练所需的格式。
支持自动下载（需 kaggle CLI）、目录结构转换、标注格式验证和数据集划分。

使用说明:
    # 方式一：已下载数据集并解压到指定目录
    python yolo/prepare_plantdoc.py --source /path/to/plantdoc_raw

    # 方式二：使用 kaggle CLI 自动下载
    python yolo/prepare_plantdoc.py --download

    # 仅验证现有数据集
    python yolo/prepare_plantdoc.py --validate

PlantDoc 数据集来源:
    https://www.kaggle.com/datasets/mrigaankbhatt/plantdoc-dataset
"""

import argparse
import os
import random
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / 'datasets' / 'plant_disease'

# PlantDoc 类别定义（28 个类别）
PLANTDOC_CLASSES = [
    'Apple_Scab_Leaf',
    'Apple_leaf',
    'Apple_rust_leaf',
    'Bell_pepper_leaf_spot',
    'Bell_pepper_leaf',
    'Blueberry_leaf',
    'Cherry_leaf',
    'Corn_Gray_leaf_spot',
    'Corn_leaf_blight',
    'Corn_rust_leaf',
    'Grape_leaf_black_rot',
    'Grape_leaf',
    'Grape_leaf_blight',
    'Peach_leaf',
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
]

# 常见的 PlantDoc 类名变体映射（处理数据集中名称不一致的情况）
CLASS_ALIASES = {
    'Apple Scab Leaf': 'Apple_Scab_Leaf',
    'Apple leaf': 'Apple_leaf',
    'Apple rust leaf': 'Apple_rust_leaf',
    'Bell_pepper leaf spot': 'Bell_pepper_leaf_spot',
    'Bell_pepper leaf': 'Bell_pepper_leaf',
    'Blueberry leaf': 'Blueberry_leaf',
    'Cherry leaf': 'Cherry_leaf',
    'Corn Gray leaf spot': 'Corn_Gray_leaf_spot',
    'Corn leaf blight': 'Corn_leaf_blight',
    'Corn rust leaf': 'Corn_rust_leaf',
    'Grape Leaf black rot': 'Grape_leaf_black_rot',
    'Grape leaf black rot': 'Grape_leaf_black_rot',
    'Grape leaf': 'Grape_leaf',
    'Grape leaf blight': 'Grape_leaf_blight',
    'Peach leaf': 'Peach_leaf',
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
}


def normalize_class_name(name):
    """标准化类名，处理空格和下划线不一致的情况"""
    name = name.strip()
    if name in CLASS_ALIASES:
        return CLASS_ALIASES[name]
    # 尝试用下划线替换空格再匹配
    normalized = name.replace(' ', '_')
    if normalized in PLANTDOC_CLASSES:
        return normalized
    return name


def get_class_id(class_name):
    """获取类名对应的类别 ID"""
    normalized = normalize_class_name(class_name)
    if normalized in PLANTDOC_CLASSES:
        return PLANTDOC_CLASSES.index(normalized)
    return -1


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
    tree = ET.parse(xml_path)
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


def setup_directories():
    """创建 YOLO 数据集目录结构"""
    for split in ['train', 'val', 'test']:
        (DATASET_DIR / 'images' / split).mkdir(parents=True, exist_ok=True)
        (DATASET_DIR / 'labels' / split).mkdir(parents=True, exist_ok=True)
    print('  数据集目录结构已创建')


def convert_dataset(source_dir, train_ratio=0.8, val_ratio=0.1):
    """
    将 PlantDoc 原始数据集转换为 YOLO 格式。

    PlantDoc 数据集通常有两种组织方式：
      1. images/ + annotations/ (XML) 的分离结构
      2. 按类别分目录的分类结构

    本函数自动检测并处理两种结构。

    Args:
        source_dir: 原始数据集目录
        train_ratio: 训练集比例
        val_ratio: 验证集比例
    """
    source = Path(source_dir)
    if not source.exists():
        print(f'错误: 源数据集目录不存在: {source}')
        sys.exit(1)

    setup_directories()

    # 收集所有图片和标注
    image_files = []
    xml_files = {}

    # 查找所有图片
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG']:
        for img_path in source.rglob(ext):
            image_files.append(img_path)

    # 查找所有 XML 标注
    for xml_path in source.rglob('*.xml'):
        stem = xml_path.stem
        xml_files[stem] = xml_path

    print(f'  找到 {len(image_files)} 张图片')
    print(f'  找到 {len(xml_files)} 个标注文件')

    # 匹配图片与标注
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

    # 随机打乱并划分数据集
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
            # 获取图片尺寸
            try:
                from PIL import Image
                with Image.open(img_path) as im:
                    img_w, img_h = im.size
            except ImportError:
                print('  错误: 需要安装 Pillow 库来读取图片尺寸')
                print('    pip install pillow')
                sys.exit(1)

            # 转换标注
            yolo_lines = convert_voc_to_yolo(xml_path, img_w, img_h)
            if not yolo_lines:
                continue

            # 复制图片
            dst_img = DATASET_DIR / 'images' / split_name / img_path.name
            shutil.copy2(img_path, dst_img)

            # 写入标注
            dst_label = DATASET_DIR / 'labels' / split_name / (img_path.stem + '.txt')
            with open(dst_label, 'w') as f:
                f.write('\n'.join(yolo_lines) + '\n')

            # 统计类别
            for line in yolo_lines:
                class_id = int(line.split()[0])
                stats[PLANTDOC_CLASSES[class_id]] += 1

    # 输出统计信息
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
    """使用 kaggle CLI 下载 PlantDoc 数据集"""
    try:
        import subprocess
        print('正在使用 Kaggle CLI 下载 PlantDoc 数据集...')
        print('  请确保已配置 ~/.kaggle/kaggle.json\n')

        download_dir = ROOT / 'datasets' / 'plantdoc_raw'
        download_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            'kaggle', 'datasets', 'download',
            '-d', 'mrigaankbhatt/plantdoc-dataset',
            '-p', str(download_dir),
            '--unzip',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f'  下载失败: {result.stderr}')
            print('\n  手动下载步骤:')
            print('  1. 访问 https://www.kaggle.com/datasets/mrigaankbhatt/plantdoc-dataset')
            print('  2. 下载并解压到 datasets/plantdoc_raw/')
            print('  3. 运行: python yolo/prepare_plantdoc.py --source datasets/plantdoc_raw')
            sys.exit(1)

        print(f'  下载完成: {download_dir}')
        return str(download_dir)

    except FileNotFoundError:
        print('错误: 未找到 kaggle 命令')
        print('  请先安装: pip install kaggle')
        print('  并配置 API Key: https://www.kaggle.com/docs/api')
        sys.exit(1)


def print_dataset_summary():
    """打印数据集摘要信息"""
    print('\n' + '=' * 60)
    print('  PlantDoc 数据集信息')
    print('=' * 60)
    print(f'  类别数: {len(PLANTDOC_CLASSES)}')
    print(f'  目录: {DATASET_DIR}')
    print('\n  类别列表:')
    for i, name in enumerate(PLANTDOC_CLASSES):
        print(f'    {i:2d}: {name}')
    print('=' * 60)


def parse_args():
    parser = argparse.ArgumentParser(description='PlantDoc 数据集准备工具')
    parser.add_argument('--source', type=str, help='PlantDoc 原始数据集目录路径')
    parser.add_argument('--download', action='store_true', help='使用 Kaggle CLI 下载数据集')
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
    print('PlantDoc 数据集准备工具')
    print()
    print('用法:')
    print('  python yolo/prepare_plantdoc.py --source /path/to/plantdoc_raw')
    print('  python yolo/prepare_plantdoc.py --download')
    print('  python yolo/prepare_plantdoc.py --validate')
    print('  python yolo/prepare_plantdoc.py --info')


if __name__ == '__main__':
    main()
