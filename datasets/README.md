# FieldPlant 植物病害检测数据集

## 数据集来源

本项目使用 Roboflow 上的 **FieldPlant** 数据集 (v11) 进行模型训练和评估。

- 下载地址：https://universe.roboflow.com/plant-disease-detection/fieldplant/dataset/11
- 包含 3 种作物的 27 个类别（木薯 5 类 + 玉米 16 类 + 番茄 6 类）
- 许可证：CC BY 4.0

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

## FieldPlant 类别定义 (27 类)

| ID | 英文名 | 中文名 |
|----|--------|--------|
| 0  | Cassava Bacterial Blight | 木薯细菌性枯萎病 |
| 1  | Cassava Brown Leaf Spot | 木薯褐斑病 |
| 2  | Cassava Healthy | 木薯健康 |
| 3  | Cassava Mosaic | 木薯花叶病 |
| 4  | Cassava Root Rot | 木薯根腐病 |
| 5  | Corn Brown Spots | 玉米褐斑病 |
| 6  | Corn Charcoal | 玉米炭疽病 |
| 7  | Corn Chlorotic Leaf Spot | 玉米褪绿叶斑病 |
| 8  | Corn Gray leaf spot | 玉米灰斑病 |
| 9  | Corn Healthy | 玉米健康 |
| 10 | Corn Insects Damages | 玉米虫害 |
| 11 | Corn Mildew | 玉米霉病 |
| 12 | Corn Purple Discoloration | 玉米紫色变色 |
| 13 | Corn Smut | 玉米黑穗病 |
| 14 | Corn Streak | 玉米条纹病 |
| 15 | Corn Stripe | 玉米条斑病 |
| 16 | Corn Violet Decoloration | 玉米紫罗兰变色 |
| 17 | Corn Yellow Spots | 玉米黄斑病 |
| 18 | Corn Yellowing | 玉米黄化病 |
| 19 | Corn leaf blight | 玉米叶枯病 |
| 20 | Corn rust leaf | 玉米锈病叶 |
| 21 | Tomato Brown Spots | 番茄褐斑病 |
| 22 | Tomato bacterial wilt | 番茄细菌性萎蔫病 |
| 23 | Tomato blight leaf | 番茄疫病叶 |
| 24 | Tomato healthy | 番茄健康 |
| 25 | Tomato leaf mosaic virus | 番茄花叶病毒 |
| 26 | Tomato leaf yellow virus | 番茄黄化曲叶病毒 |

## 数据集准备

### 方式一：下载 FieldPlant 数据集

1. 从 Roboflow 下载 FieldPlant v11 数据集：https://universe.roboflow.com/plant-disease-detection/fieldplant/dataset/11
2. 选择 YOLO 格式导出并解压到本地
3. 运行准备脚本：
   ```bash
   python yolo/prepare_dataset.py --source /path/to/FieldPlant.v11
   ```

### 方式二：兼容 PlantDoc 数据集

1. 从 DatasetNinja 下载 PlantDoc 数据集
2. 运行：
   ```bash
   python yolo/prepare_dataset.py --source /path/to/plantdoc_raw --dataset plantdoc
   ```

### 验证数据集

```bash
python yolo/prepare_dataset.py --validate
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
6. FieldPlant 数据集采用 Roboflow YOLO 格式导出，已包含 YOLO TXT 标注，无需格式转换
