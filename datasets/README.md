# PlantDoc 植物病害检测数据集

## 数据集来源

本项目使用 Kaggle 上的 **PlantDoc** 数据集进行模型训练和评估。

- 下载地址：https://www.kaggle.com/datasets/mrigaankbhatt/plantdoc-dataset
- 包含 13 种植物的 28 个类别（病害+健康）

## 目录结构

```
datasets/
└── plant_disease/
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
7 0.321 0.450 0.150 0.200
```

## PlantDoc 类别定义 (28 类)

| ID | 英文名 | 中文名 |
|----|--------|--------|
| 0  | Apple_Scab_Leaf | 苹果黑星病叶 |
| 1  | Apple_leaf | 苹果健康叶 |
| 2  | Apple_rust_leaf | 苹果锈病叶 |
| 3  | Bell_pepper_leaf_spot | 甜椒叶斑病 |
| 4  | Bell_pepper_leaf | 甜椒健康叶 |
| 5  | Blueberry_leaf | 蓝莓健康叶 |
| 6  | Cherry_leaf | 樱桃健康叶 |
| 7  | Corn_Gray_leaf_spot | 玉米灰斑病 |
| 8  | Corn_leaf_blight | 玉米叶枯病 |
| 9  | Corn_rust_leaf | 玉米锈病叶 |
| 10 | Grape_leaf_black_rot | 葡萄黑腐病叶 |
| 11 | Grape_leaf | 葡萄健康叶 |
| 12 | Grape_leaf_blight | 葡萄叶枯病 |
| 13 | Peach_leaf | 桃树健康叶 |
| 14 | Potato_leaf_early_blight | 马铃薯早疫病叶 |
| 15 | Potato_leaf_late_blight | 马铃薯晚疫病叶 |
| 16 | Raspberry_leaf | 覆盆子健康叶 |
| 17 | Soybean_leaf | 大豆健康叶 |
| 18 | Squash_Powdery_mildew_leaf | 南瓜白粉病叶 |
| 19 | Strawberry_leaf | 草莓健康叶 |
| 20 | Tomato_Early_blight_leaf | 番茄早疫病叶 |
| 21 | Tomato_Septoria_leaf_spot | 番茄叶斑病 |
| 22 | Tomato_leaf | 番茄健康叶 |
| 23 | Tomato_leaf_bacterial_spot | 番茄细菌性斑点病叶 |
| 24 | Tomato_leaf_late_blight | 番茄晚疫病叶 |
| 25 | Tomato_leaf_mosaic_virus | 番茄花叶病毒叶 |
| 26 | Tomato_leaf_yellow_virus | 番茄黄化曲叶病毒叶 |
| 27 | Tomato_mold_leaf | 番茄霉病叶 |

## 数据集准备

### 方式一：手动下载并转换

1. 从 Kaggle 下载 PlantDoc 数据集：https://www.kaggle.com/datasets/mrigaankbhatt/plantdoc-dataset
2. 解压到本地目录
3. 运行转换脚本：
   ```bash
   python yolo/prepare_plantdoc.py --source /path/to/plantdoc_raw
   ```

### 方式二：使用 Kaggle CLI 自动下载

1. 安装 kaggle CLI：`pip install kaggle`
2. 配置 API Key（参考 https://www.kaggle.com/docs/api）
3. 运行：
   ```bash
   python yolo/prepare_plantdoc.py --download
   ```

### 验证数据集

```bash
python yolo/prepare_plantdoc.py --validate
```

## 数据集划分建议

| 用途 | 比例 | 说明 |
|------|------|------|
| 训练集 (train) | 80% | 用于模型训练 |
| 验证集 (val) | 10% | 训练时监控过拟合 |
| 测试集 (test) | 10% | 最终评估模型性能 |

## 注意事项

1. 图片格式支持: JPG, PNG, BMP
2. 建议分辨率: 640×640 或更高
3. 标注文件必须与图片同名 (如 `img001.jpg` → `img001.txt`)
4. 没有目标的图片可以不创建标注文件，或创建空文件
5. `datasets/` 目录下的图片和标注文件已在 `.gitignore` 中排除，不会提交到 Git
6. PlantDoc 原始数据使用 Pascal VOC XML 格式标注，转换脚本会自动转为 YOLO TXT 格式
