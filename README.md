# 基于 YOLOv11 的植物病害智能检测系统

## 一、项目简介

本项目为本科毕业设计，采用前后端分离架构，集成 YOLOv11 目标检测模型，实现植物叶片病害的智能识别与管理。系统使用 DatasetNinja 上的 PlantDoc 数据集进行模型训练，包含完整的数据集管理、模型训练、评估、部署和可视化流程，可作为毕业论文的实验验证平台。

## 二、技术栈

| 层次      | 技术选型                                         |
|-----------|-------------------------------------------------|
| 前端      | Vue 3 + Vite + Element Plus + Pinia + Chart.js   |
| 后端      | Django 6.0.3 + Django REST Framework 3.16.1      |
| 认证      | JWT（PyJWT 2.12.1）                               |
| AI 模型   | YOLOv11（ultralytics）                            |
| 数据集    | PlantDoc（DatasetNinja, 30 类植物病害）             |
| 数据库    | MySQL 8.0                                       |
| 跨域      | django-cors-headers 4.9.0                        |

## 三、功能模块

- **登录注册**：用户名+密码+图形验证码登录，PBKDF2 加密存储密码
- **忘记密码**：通过用户名+手机号+验证码重置密码
- **JWT 认证**：安全的 Token 认证，7天有效期，自动续期
- **系统首页**：检测统计卡片 + 近7天趋势图 + 病害分布图 + 模型状态
- **病害检测**：拖拽上传图片，调用 YOLOv11 推理，展示标注结果及检测框详情，支持选择不同模型进行检测
- **历史记录**：分页列表，支持搜索、单条/批量删除，查看详情
- **知识库**：病害知识卡片展示，支持按植物/病害名搜索，点击查看详情
- **数据集管理**（新增）：PlantDoc 数据集概览、类别分布、划分统计、数据集准备指南
- **模型训练管理**（新增）：训练配置参考、YOLOv11 模型选项、历史训练记录、论文实验设计建议
- **实验结果**：展示模型训练曲线（损失/mAP/Precision/Recall）、评估指标、各类别 AP、实验设计说明
- **个人中心**：查看/修改个人信息、修改密码
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
│   ├── prepare_plantdoc.py  # PlantDoc 数据集准备脚本（新增）
│   └── configs/             # 数据集与训练配置
│       ├── data.yaml        # PlantDoc 30 类数据集配置
│       └── train_config.yaml # YOLOv11 训练超参数
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

### 数据集准备（PlantDoc）

```bash
# 从 DatasetNinja 网站下载 PlantDoc 数据集（Supervisely 格式）:
#   https://datasetninja.com/plantdoc
# 解压后目录结构为:
#   plantdoc-DatasetNinja/
#   ├── train/
#   │   ├── img/   # 训练图片 (2251张)
#   │   └── ann/   # JSON 标注文件
#   └── test/
#       ├── img/   # 测试图片 (231张)
#       └── ann/   # JSON 标注文件

# 将数据集转换为 YOLO 格式（自动检测预划分目录，从 train 拆分 val）
python yolo/prepare_plantdoc.py --source /path/to/plantdoc-DatasetNinja

# 也可以尝试从 GitHub Releases 自动下载
python yolo/prepare_plantdoc.py --download

# 验证数据集
python yolo/prepare_plantdoc.py --validate
```

> **注意**: `dataset-ninja` 包不在公共 PyPI 上，请从 https://datasetninja.com/plantdoc 手动下载数据集后使用 `--source` 参数指定路径。

### 模型训练

```bash
# 使用 YOLOv11 训练（默认 yolo11n.pt, 100 epochs）
python yolo/train.py

# 使用更大模型
python yolo/train.py --model yolo11s.pt --epochs 150

# 评估模型
python yolo/evaluate.py --split test --save-json

# 部署到系统
cp runs/train/plant_disease/weights/best.pt model/best.pt
```

详细训练指南请参考 [yolo/README.md](yolo/README.md)

## 六、PlantDoc 数据集

本项目使用 DatasetNinja 上的 **PlantDoc** 数据集，包含 30 个类别：

| 植物 | 病害类别 |
|------|---------|
| 苹果 | 黑星病叶、健康叶、锈病叶 |
| 甜椒 | 叶斑病、健康叶 |
| 蓝莓 | 健康叶 |
| 樱桃 | 健康叶 |
| 玉米 | 灰斑病、叶枯病、锈病叶 |
| 葡萄 | 黑腐病叶、健康叶、叶枯病 |
| 桃树 | 健康叶 |
| 马铃薯 | 健康叶、早疫病叶、晚疫病叶 |
| 覆盆子 | 健康叶 |
| 大豆 | 健康叶 |
| 南瓜 | 白粉病叶 |
| 草莓 | 健康叶 |
| 番茄 | 早疫病叶、叶斑病、健康叶、细菌性斑点病叶、晚疫病叶、花叶病毒叶、黄化曲叶病毒叶、霉病叶、二斑叶螨叶 |

数据集来源：https://datasetninja.com/plantdoc

## 七、API 接口

详见 [docs/api-docs.md](docs/api-docs.md)

## 八、数据库设计

详见 [docs/database-design.md](docs/database-design.md)

## 九、系统架构

详见 [docs/system-design.md](docs/system-design.md)

## 十、系统使用指南

详见 [docs/user-guide.md](docs/user-guide.md)
