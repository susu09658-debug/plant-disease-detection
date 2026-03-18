"""
YOLOv11 植物病害检测 - 模型训练脚本
Plant Disease Detection - Model Training Script (YOLOv11 + PlantDoc)

使用说明:
    python yolo/train.py                           # 使用默认参数训练
    python yolo/train.py --model yolo11s.pt        # 使用 YOLO11s 模型
    python yolo/train.py --epochs 200 --batch 32   # 自定义训练参数
    python yolo/train.py --device 0                # 指定 GPU

训练完成后，最优权重保存在: runs/train/plant_disease/weights/best.pt
可将 best.pt 复制到 model/ 目录供系统推理使用。
"""

import argparse
import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def parse_args():
    parser = argparse.ArgumentParser(description='YOLOv11 植物病害检测模型训练')

    # 模型参数
    parser.add_argument('--model', type=str, default='yolo11n.pt',
                        help='预训练模型名称或路径 (yolo11n/s/m/l/x.pt)')
    parser.add_argument('--data', type=str, default=str(ROOT / 'yolo' / 'configs' / 'data.yaml'),
                        help='数据集配置文件路径')

    # 训练参数
    parser.add_argument('--epochs', type=int, default=100, help='训练轮数')
    parser.add_argument('--batch', type=int, default=16, help='批次大小')
    parser.add_argument('--imgsz', type=int, default=640, help='输入图片尺寸')
    parser.add_argument('--patience', type=int, default=20, help='早停轮数')

    # 优化器参数
    parser.add_argument('--optimizer', type=str, default='SGD',
                        choices=['SGD', 'Adam', 'AdamW'], help='优化器')
    parser.add_argument('--lr0', type=float, default=0.01, help='初始学习率')

    # 输出参数
    parser.add_argument('--project', type=str, default=str(ROOT / 'runs' / 'train'),
                        help='训练结果保存目录')
    parser.add_argument('--name', type=str, default='plant_disease', help='实验名称')
    parser.add_argument('--resume', action='store_true', help='从上次中断处继续训练')

    # 设备参数
    parser.add_argument('--device', type=str, default='',
                        help='训练设备 (空=自动, cpu, 0, 0,1 等)')

    return parser.parse_args()


def main():
    args = parse_args()

    # 导入 ultralytics（延迟导入，便于查看帮助信息）
    try:
        from ultralytics import YOLO
    except ImportError:
        print('错误: 请先安装 ultralytics 库')
        print('  pip install ultralytics')
        sys.exit(1)

    print('=' * 60)
    print('  YOLOv11 植物病害检测模型训练 (PlantDoc)')
    print('=' * 60)
    print(f'  模型:     {args.model}')
    print(f'  数据集:   {args.data}')
    print(f'  轮数:     {args.epochs}')
    print(f'  批次大小: {args.batch}')
    print(f'  图片尺寸: {args.imgsz}')
    print(f'  优化器:   {args.optimizer}')
    print(f'  学习率:   {args.lr0}')
    print(f'  保存路径: {args.project}/{args.name}')
    print('=' * 60)

    # 检查数据集配置文件
    data_path = Path(args.data)
    if not data_path.exists():
        print(f'错误: 数据集配置文件不存在: {data_path}')
        sys.exit(1)

    # 加载预训练模型
    print(f'\n正在加载预训练模型: {args.model} ...')
    model = YOLO(args.model)

    # 构造训练参数
    train_kwargs = {
        'data': str(data_path),
        'epochs': args.epochs,
        'batch': args.batch,
        'imgsz': args.imgsz,
        'patience': args.patience,
        'optimizer': args.optimizer,
        'lr0': args.lr0,
        'project': args.project,
        'name': args.name,
        'plots': True,
        'save_period': 10,
        'resume': args.resume,
    }

    if args.device:
        train_kwargs['device'] = args.device

    # 开始训练
    print('\n开始训练...\n')
    results = model.train(**train_kwargs)

    # 训练完成
    print('\n' + '=' * 60)
    print('  训练完成!')
    print('=' * 60)

    # 输出关键指标
    result_dir = Path(args.project) / args.name
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
