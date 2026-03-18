"""
YOLOv8 植物病害检测 - 单张图片推理脚本
Plant Disease Detection - Single Image Prediction

使用说明:
    python yolo/predict.py --source path/to/image.jpg
    python yolo/predict.py --source path/to/images_dir/
    python yolo/predict.py --source path/to/image.jpg --model model/best.pt
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def parse_args():
    parser = argparse.ArgumentParser(description='YOLOv8 植物病害检测推理')
    parser.add_argument('--model', type=str, default=str(ROOT / 'model' / 'best.pt'),
                        help='模型权重路径')
    parser.add_argument('--source', type=str, required=True,
                        help='待检测图片路径或目录')
    parser.add_argument('--imgsz', type=int, default=640, help='输入图片尺寸')
    parser.add_argument('--conf', type=float, default=0.25, help='置信度阈值')
    parser.add_argument('--iou', type=float, default=0.45, help='NMS IoU 阈值')
    parser.add_argument('--device', type=str, default='', help='设备')
    parser.add_argument('--save', action='store_true', default=True,
                        help='保存检测结果图片')
    parser.add_argument('--project', type=str, default=str(ROOT / 'runs' / 'predict'),
                        help='推理结果保存目录')
    parser.add_argument('--name', type=str, default='plant_disease', help='实验名称')
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        from ultralytics import YOLO
    except ImportError:
        print('错误: 请先安装 ultralytics 库')
        print('  pip install ultralytics')
        sys.exit(1)

    model_path = Path(args.model)
    if not model_path.exists():
        print(f'错误: 模型文件不存在: {model_path}')
        sys.exit(1)

    source_path = Path(args.source)
    if not source_path.exists():
        print(f'错误: 图片路径不存在: {source_path}')
        sys.exit(1)

    print('=' * 60)
    print('  YOLOv8 植物病害检测推理')
    print('=' * 60)
    print(f'  模型:   {args.model}')
    print(f'  输入:   {args.source}')
    print(f'  置信度: {args.conf}')
    print('=' * 60)

    # 加载模型
    model = YOLO(str(model_path))

    # 执行推理
    results = model.predict(
        source=str(source_path),
        imgsz=args.imgsz,
        conf=args.conf,
        iou=args.iou,
        save=args.save,
        project=args.project,
        name=args.name,
    )

    # 输出结果
    print('\n检测结果:')
    for r in results:
        if r.boxes and len(r.boxes) > 0:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = r.names[cls_id]
                coords = box.xyxy[0].tolist()
                print(f'  - {label}: 置信度 {conf:.4f}, 位置 [{coords[0]:.0f}, {coords[1]:.0f}, {coords[2]:.0f}, {coords[3]:.0f}]')
        else:
            print('  - 未检测到病害')

    result_dir = Path(args.project) / args.name
    print(f'\n  结果保存在: {result_dir}/')


if __name__ == '__main__':
    main()
