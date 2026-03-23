"""
YOLOv11 植物病害检测 - 模型训练脚本
Plant Disease Detection - Model Training Script (YOLOv11 + PlantDoc)

使用说明:
    python yolo/train.py                           # 使用默认参数训练
    python yolo/train.py --model yolo11s.pt        # 使用 YOLO11s 模型
    python yolo/train.py --epochs 200 --batch 32   # 自定义训练参数
    python yolo/train.py --device 0                # 指定 GPU
    python yolo/train.py --strategy baseline       # 使用基线训练策略
    python yolo/train.py --strategy augment        # 使用数据增强策略
    python yolo/train.py --strategy finetune       # 使用微调策略
    python yolo/train.py --strategy lightweight    # 使用轻量化部署策略
    python yolo/train.py --strategy thesis         # 使用论文优化策略

训练完成后，最优权重保存在: runs/train/<name>/weights/best.pt
可将 best.pt 复制到 model/ 目录供系统推理使用。
"""

import argparse
import sys
from pathlib import Path

import yaml

# 确保项目根目录在 Python 路径中
ROOT = Path(__file__).resolve().parent.parent
CONFIGS_DIR = Path(__file__).resolve().parent / 'configs'

STRATEGY_MAP = {
    'baseline': CONFIGS_DIR / 'strategy_baseline.yaml',
    'augment': CONFIGS_DIR / 'strategy_augment.yaml',
    'finetune': CONFIGS_DIR / 'strategy_finetune.yaml',
    'lightweight': CONFIGS_DIR / 'strategy_lightweight.yaml',
    'thesis': CONFIGS_DIR / 'strategy_thesis.yaml',
}

sys.path.insert(0, str(ROOT))


def load_strategy(strategy_name):
    """加载预定义训练策略配置"""
    path = STRATEGY_MAP.get(strategy_name)
    if not path or not path.exists():
        print(f'错误: 未知策略 "{strategy_name}"')
        print(f'可用策略: {", ".join(STRATEGY_MAP.keys())}')
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def parse_args():
    parser = argparse.ArgumentParser(description='YOLOv11 植物病害检测模型训练')

    # 策略参数
    parser.add_argument('--strategy', type=str, default=None,
                        choices=list(STRATEGY_MAP.keys()),
                        help='预定义训练策略 (baseline/augment/finetune/lightweight)')

    # 模型参数
    parser.add_argument('--model', type=str, default=None,
                        help='预训练模型名称或路径 (yolo11n/s/m/l/x.pt)')
    parser.add_argument('--data', type=str, default=str(ROOT / 'yolo' / 'configs' / 'data.yaml'),
                        help='数据集配置文件路径')

    # 训练参数
    parser.add_argument('--epochs', type=int, default=None, help='训练轮数')
    parser.add_argument('--batch', type=int, default=None, help='批次大小')
    parser.add_argument('--imgsz', type=int, default=None, help='输入图片尺寸')
    parser.add_argument('--patience', type=int, default=None, help='早停轮数')

    # 优化器参数
    parser.add_argument('--optimizer', type=str, default=None,
                        choices=['SGD', 'Adam', 'AdamW'], help='优化器')
    parser.add_argument('--lr0', type=float, default=None, help='初始学习率')

    # 输出参数
    parser.add_argument('--project', type=str, default=None,
                        help='训练结果保存目录')
    parser.add_argument('--name', type=str, default=None, help='实验名称')
    parser.add_argument('--resume', action='store_true', help='从上次中断处继续训练')

    # 设备参数
    parser.add_argument('--device', type=str, default='',
                        help='训练设备 (空=自动, cpu, 0, 0,1 等)')

    return parser.parse_args()


def main():
    args = parse_args()

    # 加载策略配置（如果指定）
    strategy_cfg = {}
    if args.strategy:
        strategy_cfg = load_strategy(args.strategy)
        print(f'已加载训练策略: {args.strategy}')

    # 合并参数：命令行参数 > 策略配置 > 默认值
    defaults = {
        'model': 'yolo11n.pt',
        'epochs': 100,
        'batch': 16,
        'imgsz': 640,
        'patience': 20,
        'optimizer': 'SGD',
        'lr0': 0.01,
        'project': str(ROOT / 'runs' / 'train'),
        'name': 'plant_disease',
    }

    def resolve(key):
        cli_val = getattr(args, key, None)
        if cli_val is not None:
            return cli_val
        if key in strategy_cfg:
            return strategy_cfg[key]
        return defaults[key]

    model = resolve('model')
    epochs = resolve('epochs')
    batch = resolve('batch')
    imgsz = resolve('imgsz')
    patience = resolve('patience')
    optimizer = resolve('optimizer')
    lr0 = resolve('lr0')
    project = resolve('project')
    name = resolve('name')

    # 导入 ultralytics（延迟导入，便于查看帮助信息）
    try:
        from ultralytics import YOLO
    except ImportError:
        print('错误: 请先安装 ultralytics 库')
        print('  pip install ultralytics')
        sys.exit(1)

    print('=' * 60)
    print('  YOLOv11 植物病害检测模型训练 (PlantDoc)')
    if args.strategy:
        print(f'  策略:     {args.strategy}')
    print('=' * 60)
    print(f'  模型:     {model}')
    print(f'  数据集:   {args.data}')
    print(f'  轮数:     {epochs}')
    print(f'  批次大小: {batch}')
    print(f'  图片尺寸: {imgsz}')
    print(f'  优化器:   {optimizer}')
    print(f'  学习率:   {lr0}')
    print(f'  保存路径: {project}/{name}')
    print('=' * 60)

    # 检查数据集配置文件
    data_path = Path(args.data)
    if not data_path.exists():
        print(f'错误: 数据集配置文件不存在: {data_path}')
        sys.exit(1)

    # 加载预训练模型
    print(f'\n正在加载预训练模型: {model} ...')
    yolo_model = YOLO(model)

    # 构造训练参数
    train_kwargs = {
        'data': str(data_path),
        'epochs': epochs,
        'batch': batch,
        'imgsz': imgsz,
        'patience': patience,
        'optimizer': optimizer,
        'lr0': lr0,
        'project': project,
        'name': name,
        'plots': True,
        'save_period': strategy_cfg.get('save_period', 10),
        'resume': args.resume,
    }

    # 从策略配置中加载额外的训练参数（数据增强等）
    extra_keys = [
        'lrf', 'momentum', 'weight_decay',
        'warmup_epochs', 'warmup_momentum', 'warmup_bias_lr',
        'hsv_h', 'hsv_s', 'hsv_v',
        'degrees', 'translate', 'scale',
        'fliplr', 'flipud', 'mosaic', 'mixup',
        'copy_paste', 'label_smoothing',
    ]
    for key in extra_keys:
        if key in strategy_cfg:
            train_kwargs[key] = strategy_cfg[key]

    if args.device:
        train_kwargs['device'] = args.device

    # 开始训练
    print('\n开始训练...\n')
    results = yolo_model.train(**train_kwargs)

    # 训练完成
    print('\n' + '=' * 60)
    print('  训练完成!')
    print('=' * 60)

    # 输出关键指标
    result_dir = Path(project) / name
    best_weight = result_dir / 'weights' / 'best.pt'

    if best_weight.exists():
        print(f'  最优权重: {best_weight}')
        print(f'\n  若要在系统中使用此模型，请执行:')
        print(f'    cp {best_weight} {ROOT / "model" / "best.pt"}')
    else:
        print('  警告: 未找到最优权重文件')

    print(f'\n  训练日志和图表保存在: {result_dir}')
    print(f'  - 训练曲线: {result_dir}/results.png')
    print(f'  - 混淆矩阵: {result_dir}/confusion_matrix.png')
    print(f'  - PR 曲线:  {result_dir}/PR_curve.png')
    print(f'  - F1 曲线:  {result_dir}/F1_curve.png')


if __name__ == '__main__':
    main()
