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
    ├── strategy_lightweight.yaml  # 轻量化部署策略
    └── strategy_thesis.yaml       # 论文深度优化策略 (推荐)
```

## 快速开始

### 1. 环境准备

```bash
pip install ultralytics torch torchvision
```

推荐环境：PyTorch 2.3+, Python 3.12+, CUDA 12.1+, RTX 4090 或同等 GPU

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

# 使用论文深度优化策略 (推荐, 预期 mAP50 ≥ 0.70)
python yolo/train.py --strategy thesis

# 使用指定 GPU
python yolo/train.py --strategy thesis --device 0

# 自定义参数覆盖策略
python yolo/train.py --strategy thesis --epochs 200 --batch 32

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
python yolo/evaluate.py --model runs/train/thesis_optimized/weights/best.pt
```

### 5. 部署模型

```bash
# 将最优权重复制到系统使用的路径
cp runs/train/thesis_optimized/weights/best.pt model/best.pt
```

## 训练策略详解

### 策略总览

| 策略 | 模型 | 参数量 | Epochs | 图像尺寸 | 优化器 | 适用场景 |
|------|------|--------|--------|---------|--------|---------|
| baseline | YOLOv11n | 2.6M | 150 | 640 | SGD | 对照基准 |
| augment | YOLOv11n | 2.6M | 200 | 640 | SGD | 增强实验 |
| finetune | YOLOv11s | 9.4M | 250 | 640 | AdamW | 高精度 |
| lightweight | YOLOv11n | 2.6M | 150 | 416 | Adam | 边缘部署 |
| **thesis** | **YOLOv11m** | **20.1M** | **300** | **800** | **AdamW** | **论文最优** |

### 论文深度优化策略 (strategy_thesis) — 10 项核心优化

本策略针对 PlantDoc 小数据集 (~2500 张, 29 类) 的特点，综合 10 项优化技术：

#### 1. 模型容量提升

```
YOLOv11n (2.6M) → YOLOv11m (20.1M)
```

- 29 类细粒度病害分类需要更强的特征提取能力
- RTX 4090 24GB 显存完全足够支撑 medium 模型
- 相比 small 模型，mAP 可提升 3-5 个百分点

#### 2. 学习率精细调控

```yaml
optimizer: AdamW      # 解耦权重衰减
lr0: 0.0008           # 比常规值更低，训练更稳定
lrf: 0.005            # 极低终止比例 (lr_final = 4e-6)
cos_lr: true          # 余弦退火调度
```

- AdamW 的自适应学习率 + 解耦权重衰减是目标检测任务的最佳选择
- 极低终止学习率确保训练末期的精细收敛

#### 3. 高分辨率训练

```yaml
imgsz: 800            # 640 → 800
```

- 植物病斑、锈斑等细微特征需要更高分辨率捕捉
- 4090 显存充足，800px 配合 batch=16 不会 OOM

#### 4. 充分训练时长

```yaml
epochs: 300           # 100 → 300
patience: 50          # 20 → 50
```

- PlantDoc 数据量小 (~2500 张)，需要更多迭代才能充分拟合
- 配合 patience=50 的早停保护，避免无效训练

#### 5. 关闭末期 Mosaic (最关键优化)

```yaml
mosaic: 1.0           # 训练期间全程 Mosaic
close_mosaic: 20      # 最后 20 轮关闭
```

- **这通常是提升 mAP 最有效的单项优化之一**
- Mosaic 拼接虽然增加了多样性，但也改变了图像分布
- 最后阶段关闭 Mosaic，让模型在干净的单图上精细调整
- 根据目标检测领域经验，通常可提升 mAP50 约 2-5 个百分点

#### 6. 长预热策略

```yaml
warmup_epochs: 10     # 3 → 10
warmup_momentum: 0.5  # 从 0.5 过渡到 0.937
warmup_bias_lr: 0.005
```

- 消除早期训练的剧烈震荡（从训练曲线可观察到前 5-10 epoch 的不稳定）
- 平稳过渡使后续训练更快收敛

#### 7. 渐进式数据增强

```yaml
mosaic: 1.0           # 四图拼接
mixup: 0.2            # 图像混合
copy_paste: 0.15      # 实例复制粘贴
erasing: 0.3          # 随机擦除
degrees: 15.0         # ±15° 旋转
shear: 2.0            # 轻微剪切
```

- `erasing=0.3` 是亮点优化：随机擦除迫使模型学习多个局部特征
- `copy_paste=0.15` 增加目标多样性，缓解类别不平衡
- `mixup=0.2` 提供额外正则化效果

#### 8. 梯度累积

```yaml
batch: 16             # 实际批次大小
nbs: 64               # 名义批次大小 (累积 4 步)
```

- 等效 batch=64 的训练效果，BN 统计更稳定
- 同时保持实际 batch=16 以适配显存

#### 9. 混合精度训练

```yaml
amp: true             # FP16 混合精度
```

- 充分利用 4090 的 Tensor Core
- 训练速度提升约 40%，显存节省约 30%

#### 10. 正则化与损失权重

```yaml
label_smoothing: 0.05 # 轻度标签平滑
weight_decay: 0.02    # 较强权重衰减
box: 8.0              # 提升定位精度
cls: 1.0              # 分类损失
dfl: 1.5              # 分布式焦点损失
```

- 提高 box 损失权重可改善检测框精度，提升 mAP@0.5:0.95
- 轻度标签平滑避免过度自信，同时不影响分类边界

### 预期性能提升（待实验验证）

以下为基于优化原理的预期目标值，实际结果需通过训练实验验证：

| 指标 | Baseline (实测) | Thesis Optimized (预期目标) | 预期提升 |
|------|----------|-----------------|------|
| mAP@0.5 | ~0.55 | ~0.70+ | ↑15+ pp |
| mAP@0.5:0.95 | ~0.35 | ~0.48+ | ↑13+ pp |
| Precision | ~0.50 | ~0.65+ | ↑15+ pp |
| Recall | ~0.50 | ~0.60+ | ↑10+ pp |
| 训练稳定性 | 剧烈振荡 | 平滑收敛 | 显著改善 |

## YOLOv11 模型版本

> 以下 mAP 为 PlantDoc 数据集上使用 thesis 策略的预期参考值（非 COCO 通用基准），实际精度取决于数据集和超参数配置。

| 模型 | 参数量 | mAP@0.5 (PlantDoc 预期) | 推理速度 | 适用场景 |
|------|--------|----------------|---------|---------|
| YOLOv11n | 2.6M | ~55% | 最快 | 轻量级部署、快速实验 |
| YOLOv11s | 9.4M | ~60% | 快 | 平衡精度与速度 |
| YOLOv11m | 20.1M | ~70% | 中等 | 较高精度需求 (推荐) |
| YOLOv11l | 25.3M | ~72% | 较慢 | 高精度需求 |
| YOLOv11x | 56.9M | ~73% | 最慢 | 最高精度 |

> 推荐使用 **YOLOv11m** 作为论文主模型，在精度和训练效率之间取得最佳平衡。

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

训练完成后，在 `runs/train/<name>/` 目录下生成：

```
runs/train/<name>/
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

### 实验一：训练策略全面对比（核心实验）

对比所有训练策略在 PlantDoc 上的性能差异：

```bash
python yolo/train.py --strategy baseline     --name exp_baseline
python yolo/train.py --strategy augment      --name exp_augment
python yolo/train.py --strategy finetune     --name exp_finetune
python yolo/train.py --strategy lightweight  --name exp_lightweight
python yolo/train.py --strategy thesis       --name exp_thesis
```

各策略说明：
- **baseline**: 标准基线策略（YOLOv11n, SGD, 150 epochs），作为论文对照基准
- **augment**: 强化数据增强策略（Mosaic + MixUp + CopyPaste + Erasing），验证增强技术效果
- **finetune**: 大模型微调策略（YOLOv11s, AdamW, 余弦退火），追求更高检测精度
- **lightweight**: 轻量化部署策略（YOLOv11n, 低分辨率），适用于边缘设备部署
- **thesis**: 论文深度优化策略（YOLOv11m, 综合优化），获得最佳实验结果

### 实验二：模型规模消融实验

对比不同规模 YOLOv11 模型在 PlantDoc 上的性能-效率权衡：

```bash
python yolo/train.py --strategy thesis --model yolo11n.pt --name exp_model_n --imgsz 640
python yolo/train.py --strategy thesis --model yolo11s.pt --name exp_model_s --imgsz 640
python yolo/train.py --strategy thesis --model yolo11m.pt --name exp_model_m
python yolo/train.py --strategy thesis --model yolo11l.pt --name exp_model_l
```

### 实验三：关键优化技术消融实验

逐项验证每项优化的贡献（论文创新点验证）：

```bash
# 基础 (无优化)
python yolo/train.py --strategy baseline --name ablation_base

# +close_mosaic
python yolo/train.py --strategy baseline --name ablation_closemosaic
# (手动修改 strategy 中 close_mosaic=15)

# +AdamW + 余弦退火
python yolo/train.py --strategy finetune --name ablation_adamw

# +全部增强
python yolo/train.py --strategy augment --name ablation_augment

# +全部优化 (thesis)
python yolo/train.py --strategy thesis --name ablation_full
```

### 实验四：输入分辨率对比实验

```bash
python yolo/train.py --strategy thesis --imgsz 416  --name exp_imgsz_416
python yolo/train.py --strategy thesis --imgsz 640  --name exp_imgsz_640
python yolo/train.py --strategy thesis --imgsz 800  --name exp_imgsz_800
python yolo/train.py --strategy thesis --imgsz 1024 --name exp_imgsz_1024
```

### 论文图表建议

1. **表格**: 不同训练策略在测试集上的 mAP、Precision、Recall、F1 对比
2. **表格**: 不同 YOLOv11 模型的性能-效率权衡（mAP vs 参数量 vs FPS）
3. **表格**: 消融实验结果（每项优化的独立贡献）
4. **图片**: 训练损失曲线对比图（baseline vs thesis 的 loss 和 mAP 变化）
5. **图片**: 混淆矩阵 (`confusion_matrix.png`)
6. **图片**: PR 曲线 (`PR_curve.png`)
7. **图片**: 各类别 AP 条形图（展示小样本类别的改善）
8. **图片**: 检测效果示例 (`val_batch*_pred.jpg`)
9. **表格**: PlantDoc 各类别 AP 值

### RTX 4090 训练时间估计

| 策略 | 模型 | Epochs | imgsz | 预估时间 |
|------|------|--------|-------|---------|
| baseline | YOLOv11n | 150 | 640 | ~30 分钟 |
| augment | YOLOv11n | 200 | 640 | ~45 分钟 |
| finetune | YOLOv11s | 250 | 640 | ~1.5 小时 |
| lightweight | YOLOv11n | 150 | 416 | ~20 分钟 |
| **thesis** | **YOLOv11m** | **300** | **800** | **~3 小时** |

> 以上为估计值，实际时间取决于数据集大小和系统负载。thesis 策略虽然训练时间较长，但有 patience=50 的早停保护，通常不会训满 300 轮。
