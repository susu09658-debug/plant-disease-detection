"""
YOLOv11 植物病害检测 - 模型评估脚本
Plant Disease Detection - Model Evaluation Script (YOLOv11 + PlantDoc)

使用说明:
    python yolo/evaluate.py                                    # 评估默认模型
    python yolo/evaluate.py --model runs/train/plant_disease/weights/best.pt
    python yolo/evaluate.py --model model/best.pt --split test # 在测试集上评估

本脚本生成以下评估指标（可用于毕设论文）:
    - mAP@0.5 / mAP@0.5:0.95
    - Precision / Recall / F1-score
    - 混淆矩阵
    - 各类别的 AP 值
    - 推理速度 (FPS)
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def parse_args():
    parser = argparse.ArgumentParser(description='YOLOv11 植物病害检测模型评估')
    parser.add_argument('--model', type=str, default=str(ROOT / 'model' / 'best.pt'),
                        help='模型权重路径')
    parser.add_argument('--data', type=str, default=str(ROOT / 'yolo' / 'configs' / 'data.yaml'),
                        help='数据集配置文件路径')
    parser.add_argument('--split', type=str, default='val', choices=['val', 'test'],
                        help='评估使用的数据集划分')
    parser.add_argument('--imgsz', type=int, default=640, help='输入图片尺寸')
    parser.add_argument('--batch', type=int, default=16, help='批次大小')
    parser.add_argument('--conf', type=float, default=0.25, help='置信度阈值')
    parser.add_argument('--iou', type=float, default=0.45, help='NMS IoU 阈值')
    parser.add_argument('--device', type=str, default='', help='设备')
    parser.add_argument('--save-json', action='store_true', help='保存结果为 JSON 文件')
    parser.add_argument('--project', type=str, default=str(ROOT / 'runs' / 'eval'),
                        help='评估结果保存目录')
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
        print(f'  请先完成训练或将权重文件放置到 {model_path}')
        sys.exit(1)

    print('=' * 60)
    print('  YOLOv11 植物病害检测模型评估 (PlantDoc)')
    print('=' * 60)
    print(f'  模型:     {args.model}')
    print(f'  数据集:   {args.data}')
    print(f'  评估集:   {args.split}')
    print(f'  置信度:   {args.conf}')
    print(f'  IoU 阈值: {args.iou}')
    print('=' * 60)

    # 加载模型
    print(f'\n正在加载模型: {args.model} ...')
    model = YOLO(str(model_path))

    # 构造评估参数
    val_kwargs = {
        'data': args.data,
        'split': args.split,
        'imgsz': args.imgsz,
        'batch': args.batch,
        'conf': args.conf,
        'iou': args.iou,
        'plots': True,
        'project': args.project,
        'name': args.name,
    }

    if args.device:
        val_kwargs['device'] = args.device

    # 执行评估
    print('\n正在评估...\n')
    metrics = model.val(**val_kwargs)

    # 输出评估结果
    print('\n' + '=' * 60)
    print('  评估结果')
    print('=' * 60)

    # 提取关键指标
    results_dict = {
        'mAP50': float(metrics.box.map50),
        'mAP50_95': float(metrics.box.map),
        'precision': float(metrics.box.mp),
        'recall': float(metrics.box.mr),
    }
    # F1 = 2PR/(P+R)；当 P 和 R 均为 0 时 F1 直接置 0
    p, r = results_dict['precision'], results_dict['recall']
    results_dict['f1_score'] = float(2 * p * r / (p + r)) if (p + r) > 0 else 0.0

    print(f'  mAP@0.5:      {results_dict["mAP50"]:.4f}')
    print(f'  mAP@0.5:0.95: {results_dict["mAP50_95"]:.4f}')
    print(f'  Precision:     {results_dict["precision"]:.4f}')
    print(f'  Recall:        {results_dict["recall"]:.4f}')
    print(f'  F1-Score:      {results_dict["f1_score"]:.4f}')

    # 输出各类别 AP
    if hasattr(metrics.box, 'ap50') and metrics.box.ap50 is not None:
        class_names = metrics.names if hasattr(metrics, 'names') else {}
        print('\n  各类别 AP@0.5:')
        print(f'  {"类别":<30} {"AP@0.5":>10}')
        print(f'  {"-" * 42}')

        per_class = []
        for i, ap in enumerate(metrics.box.ap50):
            name = class_names.get(i, f'class_{i}')
            print(f'  {name:<30} {float(ap):>10.4f}')
            per_class.append({'class_id': i, 'class_name': name, 'ap50': float(ap)})

        results_dict['per_class'] = per_class

    print('=' * 60)

    # 保存结果到 JSON
    if args.save_json:
        result_dir = Path(args.project) / args.name
        result_dir.mkdir(parents=True, exist_ok=True)
        json_path = result_dir / 'eval_results.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, ensure_ascii=False, indent=2)
        print(f'\n  评估结果已保存到: {json_path}')

    # 提示论文使用
    print('\n  ========== 毕业论文使用建议 ==========')
    print('  可在论文中添加以下内容:')
    print('  1. 表格: 模型在验证集/测试集上的整体指标')
    print('  2. 表格: 各类别 AP 对比')
    print('  3. 图片: 混淆矩阵 (confusion_matrix.png)')
    print('  4. 图片: PR 曲线 (PR_curve.png)')
    print('  5. 图片: F1 曲线 (F1_curve.png)')
    result_dir = Path(args.project) / args.name
    print(f'  上述图表位于: {result_dir}/')


if __name__ == '__main__':
    main()
