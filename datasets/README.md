# 植物病害检测数据集

## 目录结构

```
datasets/
└── plant_disease/
    ├── data.yaml              # → yolo/configs/data.yaml (数据集配置)
    ├── images/
    │   ├── train/             # 训练集图片 (~80%)
    │   ├── val/               # 验证集图片 (~10%)
    │   └── test/              # 测试集图片 (~10%)
    └── labels/
        ├── train/             # 训练集标注 (YOLO TXT 格式)
        ├── val/               # 验证集标注
        └── test/              # 测试集标注
```

## 标注格式 (YOLO TXT)

每张图片对应一个同名 `.txt` 文件，每行一个目标：

```
<class_id> <center_x> <center_y> <width> <height>
```

- `class_id`: 类别编号 (从 0 开始)
- `center_x`, `center_y`: 目标中心坐标 (归一化到 0~1)
- `width`, `height`: 目标宽高 (归一化到 0~1)

示例：
```
0 0.512 0.631 0.284 0.195
3 0.321 0.450 0.150 0.200
```

## 类别定义

| ID | 英文名 | 中文名 |
|----|--------|--------|
| 0  | Tomato_Early_Blight | 番茄早疫病 |
| 1  | Tomato_Late_Blight | 番茄晚疫病 |
| 2  | Tomato_Healthy | 番茄健康 |
| 3  | Apple_Scab | 苹果黑星病 |
| 4  | Apple_Black_Rot | 苹果黑腐病 |
| 5  | Corn_Common_Rust | 玉米锈病 |
| 6  | Grape_Black_Rot | 葡萄黑腐病 |
| 7  | Potato_Early_Blight | 马铃薯早疫病 |
| 8  | Potato_Late_Blight | 马铃薯晚疫病 |
| 9  | Strawberry_Leaf_Scorch | 草莓叶枯病 |

## 数据集获取

### 方案一：使用 PlantVillage 公开数据集

1. 下载 PlantVillage 数据集：https://github.com/spMohanty/PlantVillage-Dataset
2. 选取需要的类别子集
3. 使用标注工具 (如 LabelImg, Roboflow) 进行目标检测标注
4. 导出为 YOLO TXT 格式
5. 按 8:1:1 比例划分为 train/val/test

### 方案二：使用 Roboflow 在线平台

1. 访问 https://roboflow.com/
2. 搜索 "plant disease detection" 数据集
3. 选择合适的数据集并导出为 YOLOv8 格式
4. 将导出的文件按上述目录结构放置

### 方案三：自定义标注

1. 收集植物病害图片 (每类建议至少 200 张)
2. 安装标注工具: `pip install labelImg`
3. 使用 LabelImg 进行标注，选择 YOLO 格式输出
4. 划分数据集

## 数据集划分建议

| 用途 | 比例 | 建议数量 (每类) | 说明 |
|------|------|-----------------|------|
| 训练集 (train) | 80% | ≥160 张 | 用于模型训练 |
| 验证集 (val) | 10% | ≥20 张 | 训练时监控过拟合 |
| 测试集 (test) | 10% | ≥20 张 | 最终评估模型性能 |

## 注意事项

1. 图片格式支持: JPG, PNG, BMP
2. 建议分辨率: 640×640 或更高
3. 标注文件必须与图片同名 (如 `img001.jpg` → `img001.txt`)
4. 没有目标的图片可以不创建标注文件，或创建空文件
5. `datasets/` 目录下的图片和标注文件已在 `.gitignore` 中排除，不会提交到 Git
