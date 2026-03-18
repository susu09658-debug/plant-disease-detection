"""
YOLOv8 植物病害检测 - 模型导出脚本
Plant Disease Detection - Model Export Utility

使用说明:
    python yolo/export_model.py                                 # 导出为 ONNX
    python yolo/export_model.py --format torchscript            # 导出为 TorchScript
    python yolo/export_model.py --model runs/train/plant_disease/weights/best.pt

支持的导出格式:
    onnx, torchscript, openvino, engine (TensorRT), coreml, tflite
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def parse_args():
    parser = argparse.ArgumentParser(description='YOLOv8 模型导出')
    parser.add_argument('--model', type=str, default=str(ROOT / 'model' / 'best.pt'),
                        help='模型权重路径')
    parser.add_argument('--format', type=str, default='onnx',
                        choices=['onnx', 'torchscript', 'openvino', 'engine', 'coreml', 'tflite'],
                        help='导出格式')
    parser.add_argument('--imgsz', type=int, default=640, help='输入图片尺寸')
    parser.add_argument('--half', action='store_true', help='使用 FP16 半精度')
    parser.add_argument('--dynamic', action='store_true', help='动态输入尺寸 (ONNX)')
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

    print('=' * 60)
    print('  YOLOv8 模型导出')
    print('=' * 60)
    print(f'  模型:   {args.model}')
    print(f'  格式:   {args.format}')
    print(f'  尺寸:   {args.imgsz}')
    print(f'  半精度: {args.half}')
    print('=' * 60)

    model = YOLO(str(model_path))

    export_path = model.export(
        format=args.format,
        imgsz=args.imgsz,
        half=args.half,
        dynamic=args.dynamic,
    )

    print(f'\n模型已导出到: {export_path}')


if __name__ == '__main__':
    main()
