# 基于 YOLOv11 的植物病害智能检测系统

## 一、项目简介

本项目为本科毕业设计，采用前后端分离架构，集成 YOLOv11 轻量化目标检测模型，实现植物叶片病害的智能识别与管理。

## 二、技术栈

| 层次      | 技术选型                                         |
|-----------|-------------------------------------------------|
| 前端      | Vue 3 + Vite + Element Plus + Pinia + Axios      |
| 后端      | Django 6.0.3 + Django REST Framework 3.15.2      |
| 认证      | JWT（PyJWT 2.10.1）                               |
| AI 模型   | YOLOv11（ultralytics）                            |
| 数据库    | MySQL 8.0                                       |
| 跨域      | django-cors-headers 4.6.0                        |

## 三、功能模块

- **登录注册**：用户名+密码+图形验证码登录，PBKDF2 加密存储密码
- **JWT 认证**：安全的 Token 认证，7天有效期，自动续期
- **系统首页**：检测统计卡片 + 近7天趋势图 + 病害分布图
- **病害检测**：拖拽上传图片，调用 YOLOv11 推理，展示标注结果
- **历史记录**：分页列表，支持搜索、单条/批量删除，查看详情
- **知识库**：病害知识卡片展示，支持按植物/病害名搜索，点击查看详情
- **个人中心**：查看/修改个人信息、修改密码
- **管理后台**（管理员专属）：用户管理（启用/禁用/设管理员/删除）、知识库管理（增删改查）

## 四、项目结构

```
plant-disease-detection/
├── frontend/                # 前端项目（Vue3 + Vite）
│   └── src/
│       ├── api/             # API 封装（request.js, user.js, detect.js, knowledge.js, admin.js）
│       ├── layouts/         # 布局组件（MainLayout.vue）
│       ├── store/           # Pinia 状态管理（user.js）
│       ├── router/          # 路由配置（含守卫）
│       └── views/           # 页面组件
├── backend/                 # 后端项目（Django 6.0.3）
│   ├── apps/
│   │   ├── user/            # 用户模块
│   │   ├── detect/          # 检测模块
│   │   └── knowledge/       # 知识库模块
│   ├── utils/
│   │   ├── jwt_utils.py     # JWT 工具
│   │   ├── authentication.py # DRF 认证类
│   │   ├── permissions.py   # 权限类
│   │   └── yolo_model.py    # YOLOv11 推理封装
│   └── requirements.txt
├── model/                   # YOLOv11 权重文件目录（best.pt）
└── docs/                    # 设计文档
    ├── system-design.md
    ├── api-docs.md
    └── database-design.md
```

## 五、快速启动

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0

### 后端启动

```bash
cd backend
pip install -r requirements.txt
# 创建数据库
mysql -u root -p -e "CREATE DATABASE plant_disease_db DEFAULT CHARACTER SET utf8mb4;"
# 执行迁移
python manage.py migrate
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

## 六、API 接口

详见 [docs/api-docs.md](docs/api-docs.md)

## 七、数据库设计

详见 [docs/database-design.md](docs/database-design.md)

## 八、系统架构

详见 [docs/system-design.md](docs/system-design.md)
