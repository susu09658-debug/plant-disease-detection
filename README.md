# 基于 YOLOv11 的植物病害智能检测系统

## 一、项目简介

本项目为本科毕业设计，采用前后端分离架构，集成 YOLOv11 目标检测模型，实现植物叶片病害的智能识别与管理。系统使用 Roboflow 上的 FieldPlant 数据集进行模型训练，包含 27 个类别（木薯 5 类 + 玉米 16 类 + 番茄 6 类），具备完整的数据集管理、模型训练、评估、部署和可视化流程，可作为毕业论文的实验验证平台。

## 二、技术栈

| 层次      | 技术选型                                         |
|-----------|-------------------------------------------------|
| 前端      | Vue 3 + Vite + Element Plus + Pinia + Chart.js   |
| 后端      | Django 6.0.3 + Django REST Framework 3.16.1      |
| 认证      | JWT（PyJWT 2.12.1）                               |
| AI 模型   | YOLOv11（ultralytics）                            |
| 数据集    | FieldPlant（Roboflow, 27 类植物病害）               |
| 数据库    | MySQL 8.0                                       |
| 跨域      | django-cors-headers 4.9.0                        |

## 三、功能模块

- **登录注册**：用户ID+密码+图形验证码登录，用户可自定义昵称，PBKDF2 加密存储密码
- **忘记密码**：通过用户ID+手机号+验证码重置密码
- **JWT 认证**：安全的 Token 认证，7天有效期，自动续期
- **系统首页**：检测统计卡片 + 近7天趋势图 + 病害分布图 + 模型状态
- **病害检测**：拖拽上传图片，调用 YOLOv11 推理，展示标注结果及检测框详情，支持选择不同模型进行检测
- **历史记录**：分页列表，支持搜索、单条/批量删除，查看详情
- **知识库**：病害知识卡片展示，支持按植物/病害名搜索，点击查看详情
- **数据集管理**（新增）：FieldPlant 数据集概览、类别分布、划分统计、数据集准备指南
- **模型训练管理**（新增）：训练配置参考、YOLOv11 模型选项、多种训练策略（基线/增强/微调/轻量化/论文优化）、历史训练记录、论文实验设计建议
- **实验结果**：展示模型训练曲线（损失/mAP/Precision/Recall）、评估指标、各类别 AP、实验设计说明
- **个人中心**：查看/修改个人信息、自定义头像上传、修改昵称、修改密码
- **管理后台**（管理员专属）：用户管理、知识库管理、数据集管理、模型训练管理（基于权限类控制）
- **管理员创建**：通过 `python manage.py create_admin` 命令行创建管理员用户

## 四、项目结构

```
plant-disease-detection/
├── frontend/                # 前端项目（Vue3 + Vite）
│   └── src/
│       ├── api/             # API 封装（request, user, detect, knowledge, experiment, dataset, admin）
│       ├── layouts/         # 布局组件（MainLayout.vue）
│       ├── store/           # Pinia 状态管理（user.js）
│       ├── router/          # 路由配置（含守卫）
│       └── views/           # 页面组件
│           ├── Dashboard.vue        # 系统首页
│           ├── Detect.vue           # 病害检测
│           ├── History.vue          # 历史记录
│           ├── Knowledge.vue        # 知识库
│           ├── DatasetManage.vue    # 数据集管理（新增）
│           ├── TrainingManage.vue   # 模型训练管理（新增）
│           ├── Experiment.vue       # 实验结果
│           ├── Profile.vue          # 个人中心
│           └── admin/               # 管理员页面
├── backend/                 # 后端项目（Django 6.0.3）
│   ├── apps/
│   │   ├── user/            # 用户模块
│   │   ├── detect/          # 检测模块
│   │   ├── knowledge/       # 知识库模块
│   │   ├── experiment/      # 实验结果与训练管理模块
│   │   └── dataset/         # 数据集管理模块（新增）
│   ├── utils/
│   │   ├── jwt_utils.py     # JWT 工具
│   │   ├── authentication.py # DRF 认证类
│   │   ├── permissions.py   # 权限类
│   │   └── yolo_model.py    # YOLOv11 推理封装
│   └── backend/             # Django 配置
├── yolo/                    # YOLO 模型训练与评估
│   ├── train.py             # YOLOv11 训练脚本
│   ├── evaluate.py          # 模型评估脚本（生成论文指标）
│   ├── predict.py           # 推理脚本
│   ├── export_model.py      # 模型导出
│   ├── prepare_plantdoc.py  # PlantDoc 数据集准备脚本（兼容保留）
│   ├── prepare_dataset.py   # 统一数据集准备脚本（支持 FieldPlant / PlantDoc）
│   └── configs/             # 数据集与训练配置
│       ├── data.yaml              # FieldPlant 27 类数据集配置
│       ├── train_config.yaml     # YOLOv11 训练超参数
│       ├── strategy_baseline.yaml    # 基线训练策略
│       ├── strategy_augment.yaml     # 数据增强策略
│       ├── strategy_finetune.yaml    # 微调训练策略
│       ├── strategy_lightweight.yaml # 轻量化部署策略
│       └── strategy_thesis.yaml      # 论文优化策略
├── datasets/                # 数据集存放目录
│   └── plant_disease/       # YOLO 格式数据集
├── model/                   # 部署用权重文件（best.pt）
├── docs/                    # 设计文档
│   ├── system-design.md
│   ├── api-docs.md
│   ├── database-design.md
│   └── user-guide.md
└── requirements.txt         # Python 依赖
```

## 五、快速启动

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0

### 后端启动

```bash
cd backend
pip install -r ../requirements.txt
# 创建数据库
mysql -u root -p -e "CREATE DATABASE plant_disease_db DEFAULT CHARACTER SET utf8mb4;"
# 执行迁移
python manage.py migrate
# 创建管理员用户
python manage.py create_admin --username admin --password admin123
# 启动开发服务器
python manage.py runserver
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

### YOLO 模型

将训练好的 `best.pt` 权重文件放置到 `model/` 目录下。如果模型文件不存在，系统会自动返回模拟数据，不影响其他功能使用。

可以在 `model/` 目录下放置多个 `.pt` 模型文件（如 `best.pt`、`yolo11n.pt`、`yolo11s.pt`），在病害检测页面可以选择不同的模型进行检测。

### 数据集准备（FieldPlant）

```bash
# FieldPlant 数据集 (Roboflow YOLO 格式, 已包含 train/valid/test 划分):
#   从 Roboflow 下载 FieldPlant v11 数据集（YOLO 格式导出）:
#   https://universe.roboflow.com/plant-disease-detection/fieldplant/dataset/11
#
# 解压后目录结构为:
#   FieldPlant.v11-fieldplant_dataset.yolov11/
#   ├── data.yaml
#   ├── train/
#   │   ├── images/
#   │   └── labels/
#   ├── valid/
#   │   ├── images/
#   │   └── labels/
#   └── test/
#       ├── images/
#       └── labels/

# 准备 FieldPlant 数据集（自动检测格式）
python yolo/prepare_dataset.py --source /path/to/FieldPlant.v11

# 或显式指定数据集类型
python yolo/prepare_dataset.py --source /path/to/FieldPlant.v11 --dataset fieldplant

# 验证数据集
python yolo/prepare_dataset.py --validate

# 查看类别信息
python yolo/prepare_dataset.py --info
```

> **兼容 PlantDoc**: 如需使用旧版 PlantDoc 数据集，可运行 `python yolo/prepare_dataset.py --source /path/to/plantdoc_raw --dataset plantdoc`。

### 模型训练

```bash
# 使用论文深度优化策略 (推荐, RTX 4090 约 3 小时)
python yolo/train.py --strategy thesis

# 使用预定义训练策略（适合毕业论文对比实验）
python yolo/train.py --strategy baseline      # 基线策略 (对照组)
python yolo/train.py --strategy augment       # 增强数据增强策略
python yolo/train.py --strategy finetune      # 大模型微调策略
python yolo/train.py --strategy lightweight   # 轻量化部署策略
python yolo/train.py --strategy thesis        # 论文深度优化策略（综合最佳实践）

# 自定义训练参数
python yolo/train.py --model yolo11s.pt --epochs 200
python yolo/train.py --strategy thesis --device 0  # 指定 GPU

# 评估模型
python yolo/evaluate.py --split test --save-json

# 部署到系统
cp runs/train/thesis_optimized/weights/best.pt model/best.pt
```

#### 训练策略对比

| 策略 | 模型 | Epochs | 图像尺寸 | 优化器 | 适用场景 | 预期 mAP50 |
|------|------|--------|---------|--------|---------|-----------|
| baseline | YOLOv11n | 150 | 640 | SGD | 对照基准 | ~0.60 |
| augment | YOLOv11n | 200 | 640 | SGD | 增强实验 | ~0.65 |
| finetune | YOLOv11s | 250 | 640 | AdamW | 高精度 | ~0.70 |
| lightweight | YOLOv11n | 150 | 416 | Adam | 边缘部署 | ~0.52 |
| **thesis** | **YOLOv11m** | **300** | **640** | **AdamW** | **论文最优** | **0.75+** |

详细训练指南请参考 [yolo/README.md](yolo/README.md)

## 六、FieldPlant 数据集

本项目使用 Roboflow 上的 **FieldPlant** 数据集 (v11)，包含 27 个类别，涵盖 3 种作物：

| 植物 | 病害类别 |
|------|---------|
| 木薯 | 细菌性枯萎病、褐斑病、健康、花叶病、根腐病 |
| 玉米 | 褐斑病、炭疽病、褪绿叶斑病、灰斑病、健康、虫害、霉病、紫色变色、黑穗病、条纹病、条斑病、紫罗兰变色、黄斑病、黄化病、叶枯病、锈病叶 |
| 番茄 | 褐斑病、细菌性萎蔫病、疫病叶、健康、花叶病毒、黄化曲叶病毒 |

数据集来源：https://universe.roboflow.com/plant-disease-detection/fieldplant/dataset/11
许可证：CC BY 4.0

## 七、API 接口

详见 [docs/api-docs.md](docs/api-docs.md)

## 八、数据库设计

详见 [docs/database-design.md](docs/database-design.md)

## 九、系统架构

详见 [docs/system-design.md](docs/system-design.md)

## 十、系统使用指南

详见 [docs/user-guide.md](docs/user-guide.md)
