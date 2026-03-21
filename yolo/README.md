# YOLOv11 植物病害检测 - 训练与评估指南

## 概述

本目录包含 YOLOv11 模型的训练、评估和推理脚本，用于 PlantDoc 植物病害目标检测任务。

## 目录结构

```
yolo/
├── README.md                  # 本文件
├── train.py                   # YOLOv11 模型训练脚本
├── evaluate.py                # 模型评估脚本 (生成论文所需指标)
├── predict.py                 # 单张/批量图片推理脚本
├── export_model.py            # 模型格式导出工具
├── prepare_plantdoc.py        # PlantDoc 数据集准备脚本
└── configs/
    ├── data.yaml              # PlantDoc 数据集配置 (29 类)
    ├── train_config.yaml      # YOLOv11 训练超参数参考
    ├── strategy_baseline.yaml     # 基线训练策略
    ├── strategy_augment.yaml      # 数据增强策略
    ├── strategy_finetune.yaml     # 微调训练策略
    └── strategy_lightweight.yaml  # 轻量化部署策略
```

## 快速开始

### 1. 环境准备

```bash
pip install ultralytics torch torchvision
```

### 2. 准备 PlantDoc 数据集

```bash
# 方式一：手动下载后转换
# 从 DatasetNinja 下载 PlantDoc 数据集，解压后运行：
python yolo/prepare_plantdoc.py --source /path/to/plantdoc_raw

# 方式二：从 DatasetNinja GitHub Releases 自动下载
python yolo/prepare_plantdoc.py --download

# 查看数据集类别信息
python yolo/prepare_plantdoc.py --info

# 验证数据集
python yolo/prepare_plantdoc.py --validate
```

数据集下载地址：https://datasetninja.com/plantdoc

确保转换后目录结构如下：

```
datasets/plant_disease/
├── images/{train,val,test}/
└── labels/{train,val,test}/
```

### 3. 训练模型

```bash
# 使用默认参数训练 (YOLOv11n, 100 epochs)
python yolo/train.py

# 使用更大模型
python yolo/train.py --model yolo11s.pt --epochs 150

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

## YOLOv11 模型版本

| 模型 | 参数量 | mAP@0.5 (参考) | 推理速度 | 适用场景 |
|------|--------|----------------|---------|---------|
| YOLOv11n | 2.6M | ~85% | 最快 | 轻量级部署、快速实验 |
| YOLOv11s | 9.4M | ~88% | 快 | 平衡精度与速度 |
| YOLOv11m | 20.1M | ~90% | 中等 | 较高精度需求 |
| YOLOv11l | 25.3M | ~91% | 较慢 | 高精度需求 |
| YOLOv11x | 56.9M | ~92% | 最慢 | 最高精度 |

> 建议本科毕设使用 **YOLOv11n** 或 **YOLOv11s**，训练速度快且精度足够。

## PlantDoc 数据集 (29 类)

PlantDoc 数据集包含 13 种植物的 29 类病害/健康状态：

| 植物 | 类别 |
|------|------|
| 苹果 | 黑星病叶、健康叶、锈病叶 |
| 甜椒 | 健康叶、叶斑病 |
| 蓝莓 | 健康叶 |
| 樱桃 | 健康叶 |
| 玉米 | 灰斑病、叶枯病、锈病叶 |
| 葡萄 | 健康叶、黑腐病叶 |
| 桃树 | 健康叶 |
| 马铃薯 | 健康叶、早疫病叶、晚疫病叶 |
| 覆盆子 | 健康叶 |
| 大豆 | 健康叶 |
| 南瓜 | 白粉病叶 |
| 草莓 | 健康叶 |
| 番茄 | 早疫病叶、叶斑病、健康叶、细菌性斑点病叶、晚疫病叶、花叶病毒叶、黄化曲叶病毒叶、霉病叶、二斑叶螨叶 |

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

训练不同规模的 YOLOv11 模型，对比在 PlantDoc 数据集上的性能：

```bash
python yolo/train.py --model yolo11n.pt --name exp_yolo11n
python yolo/train.py --model yolo11s.pt --name exp_yolo11s
python yolo/train.py --model yolo11m.pt --name exp_yolo11m
```

### 实验二：数据增强消融实验

对比不同数据增强策略的影响。

```bash
python yolo/train.py --strategy baseline --name exp_no_aug
python yolo/train.py --strategy augment  --name exp_aug
```

### 实验三：学习率对比实验

```bash
python yolo/train.py --lr0 0.001 --name exp_lr_0001
python yolo/train.py --lr0 0.01  --name exp_lr_001
python yolo/train.py --lr0 0.1   --name exp_lr_01
```

### 实验四：训练策略对比实验

使用预定义策略进行系统化对比：

```bash
python yolo/train.py --strategy baseline     --name exp_baseline
python yolo/train.py --strategy augment      --name exp_augment
python yolo/train.py --strategy finetune     --name exp_finetune
python yolo/train.py --strategy lightweight  --name exp_lightweight
```

各策略说明：
- **baseline**：标准基线策略（YOLOv11n, SGD, 100 epochs），作为论文对照基准
- **augment**：强化数据增强策略（Mosaic + MixUp + 旋转 + 色彩抖动），验证数据增强对小样本类别的提升效果
- **finetune**：大模型微调策略（YOLOv11s, AdamW, 余弦退火学习率），追求更高检测精度
- **lightweight**：轻量化部署策略（YOLOv11n, 小 batch, 低分辨率），适用于边缘设备部署场景

### 论文图表建议

1. **表格**: 不同 YOLOv11 模型在测试集上的 mAP、Precision、Recall、F1 对比
2. **图片**: 训练损失曲线 (`results.png`)
3. **图片**: 混淆矩阵 (`confusion_matrix.png`)
4. **图片**: PR 曲线 (`PR_curve.png`)
5. **图片**: 检测效果示例 (`val_batch*_pred.jpg`)
6. **表格**: PlantDoc 各类别 AP 值
