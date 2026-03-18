# YOLOv8 植物病害检测 - 训练与评估指南

## 概述

本目录包含 YOLOv8 模型的训练、评估和推理脚本，用于植物病害目标检测任务。

## 目录结构

```
yolo/
├── README.md                  # 本文件
├── train.py                   # 模型训练脚本
├── evaluate.py                # 模型评估脚本 (生成论文所需指标)
├── predict.py                 # 单张/批量图片推理脚本
├── export_model.py            # 模型格式导出工具
└── configs/
    ├── data.yaml              # 数据集配置 (类别、路径)
    └── train_config.yaml      # 训练超参数参考
```

## 快速开始

### 1. 环境准备

```bash
pip install ultralytics torch torchvision
```

### 2. 准备数据集

参考 `datasets/README.md` 准备数据集，确保目录结构如下：

```
datasets/plant_disease/
├── images/{train,val,test}/
└── labels/{train,val,test}/
```

### 3. 训练模型

```bash
# 使用默认参数训练 (YOLOv8n, 100 epochs)
python yolo/train.py

# 使用更大模型
python yolo/train.py --model yolov8s.pt --epochs 150

# 指定 GPU
python yolo/train.py --device 0

# 从中断处继续训练
python yolo/train.py --resume
```

### 4. 评估模型

```bash
# 在验证集上评估
python yolo/evaluate.py

# 在测试集上评估 (用于论文最终结果)
python yolo/evaluate.py --split test --save-json

# 评估训练目录中的权重
python yolo/evaluate.py --model runs/train/plant_disease/weights/best.pt
```

### 5. 部署模型

```bash
# 将最优权重复制到系统使用的路径
cp runs/train/plant_disease/weights/best.pt model/best.pt
```

## 可选的 YOLO 模型版本

| 模型 | 参数量 | mAP@0.5 (参考) | 推理速度 | 适用场景 |
|------|--------|----------------|---------|---------|
| YOLOv8n | 3.2M | ~85% | 最快 | 轻量级部署 |
| YOLOv8s | 11.2M | ~88% | 快 | 平衡精度与速度 |
| YOLOv8m | 25.9M | ~90% | 中等 | 较高精度需求 |
| YOLOv8l | 43.7M | ~91% | 较慢 | 高精度需求 |
| YOLOv8x | 68.2M | ~92% | 最慢 | 最高精度 |

> 建议本科毕设使用 **YOLOv8n** 或 **YOLOv8s**，训练速度快且精度足够。

## 训练输出

训练完成后，在 `runs/train/plant_disease/` 目录下生成：

```
runs/train/plant_disease/
├── weights/
│   ├── best.pt                # 验证集表现最好的权重
│   └── last.pt                # 最后一轮的权重
├── results.csv                # 每轮训练指标数据
├── results.png                # 训练曲线图
├── confusion_matrix.png       # 混淆矩阵
├── confusion_matrix_normalized.png  # 归一化混淆矩阵
├── PR_curve.png               # Precision-Recall 曲线
├── P_curve.png                # Precision 曲线
├── R_curve.png                # Recall 曲线
├── F1_curve.png               # F1 曲线
├── labels.jpg                 # 标注分布统计图
├── labels_correlogram.jpg     # 标注相关性图
├── train_batch*.jpg           # 训练批次可视化
├── val_batch*_pred.jpg        # 验证集预测结果
└── args.yaml                  # 训练参数记录
```

## 毕业论文实验设计建议

### 实验一：模型对比实验

训练不同规模的模型，对比性能：

```bash
python yolo/train.py --model yolov8n.pt --name exp_yolov8n
python yolo/train.py --model yolov8s.pt --name exp_yolov8s
python yolo/train.py --model yolov8m.pt --name exp_yolov8m
```

### 实验二：数据增强消融实验

对比不同数据增强策略的影响。

### 实验三：学习率对比实验

```bash
python yolo/train.py --lr0 0.001 --name exp_lr_0001
python yolo/train.py --lr0 0.01  --name exp_lr_001
python yolo/train.py --lr0 0.1   --name exp_lr_01
```

### 论文图表建议

1. **表格**: 不同模型在测试集上的 mAP、Precision、Recall、F1 对比
2. **图片**: 训练损失曲线 (`results.png`)
3. **图片**: 混淆矩阵 (`confusion_matrix.png`)
4. **图片**: PR 曲线 (`PR_curve.png`)
5. **图片**: 检测效果示例 (`val_batch*_pred.jpg`)
6. **表格**: 各类别 AP 值
