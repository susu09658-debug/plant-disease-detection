# 基于YOLOv11的植物病害检测系统

## 一、项目简介
本项目为本科毕业设计，采用前后端分离架构，集成YOLOv11轻量化目标检测模型，实现植物叶片病害的智能识别。系统包含用户管理、病害检测、历史记录、病害知识库、管理员管理等核心功能，适配VS Code（前端）+ PyCharm（后端）开发。

## 二、技术栈
| 层次   | 技术选型                        |
|--------|---------------------------------|
| 前端   | Vue3 + Vite + Element Plus + Axios |
| 后端   | Django 4.2 + DRF + PyTorch      |
| AI     | YOLOv11（ultralytics官方库）     |
| 数据库 | MySQL 8.0                       |
| 依赖   | django-cors-headers（跨域）      |

## 三、项目结构
```
plant-disease-detectio/
├── frontend/    # 前端项目（Vue3）
├── backend/     # 后端项目（Django）
├── model/       # YOLOv11权重文件
├── docs/        # 设计文档
└── README.md    # 项目说明
```

### 1. 前端目录
- public/：静态资源
- src/api/：接口封装（user.js、detect.js、admin.js等）
- src/views/：页面组件（Login、Register、Index、History、Knowledge等）
- src/components/：公共组件
- src/router/：路由配置
- src/store/：状态管理
- src/utils/：工具函数
- App.vue、main.js：入口

### 2. 后端目录
- apps/user/：用户模块（注册、登录、信息）
- apps/detect/：病害检测模块（历史、上传、推理接口预留）
- apps/knowledge/：病害知识库模块
- backend/settings.py：全局配置（数据库、跨域、模型）
- backend/urls.py：总路由
- utils/yolo_model.py：YOLOv11推理工具（预留）
- requirements.txt：依赖清单

## 四、数据库设计
### 1. 用户表 user_user
| 字段         | 类型         | 说明         |
|--------------|--------------|--------------|
| id           | int          | 用户ID       |
| username     | varchar(20)  | 用户名       |
| password     | varchar(100) | 加密密码     |
| phone        | varchar(11)  | 手机号       |
| create_time  | datetime     | 创建时间     |
| is_admin     | tinyint      | 是否管理员   |

### 2. 检测历史表 detect_record
| 字段         | 类型         | 说明         |
|--------------|--------------|--------------|
| id           | int          | 记录ID       |
| user_id      | int          | 关联用户ID   |
| original_img | varchar(255) | 原始图片路径 |
| result_img   | varchar(255) | 标注图片路径 |
| disease_name | varchar(50)  | 病害名称     |
| confidence   | float        | 置信度       |
| detect_time  | datetime     | 检测时间     |

### 3. 病害知识库表 knowledge_info
| 字段         | 类型         | 说明         |
|--------------|--------------|--------------|
| id           | int          | 病害ID       |
| plant_name   | varchar(30)  | 植物名称     |
| disease_name | varchar(50)  | 病害名称     |
| symptom      | text         | 病害症状     |
| treatment    | text         | 防治方法     |

## 五、接口设计（RESTful）
- 用户注册：POST /api/user/register/
- 用户登录：POST /api/user/login/
- 图片检测：POST /api/detect/upload/（模型推理预留）
- 检测历史：GET /api/detect/history/，DELETE /api/detect/history/
- 知识库列表：GET /api/knowledge/list/
- 知识库管理：POST/PUT/DELETE /api/knowledge/manage/

## 六、开发环境与配置
- 前端：Node.js 16+，VS Code，npm install
- 后端：Python 3.9+，PyCharm，pip install -r requirements.txt
- 数据库：MySQL 8.0，Navicat
- 跨域：已配置django-cors-headers，Vite代理

## 七、部署与运行
- 前端启动：cd frontend && npm run dev
- 后端启动：cd backend && python manage.py runserver
- 数据库：本地MySQL服务，建库plant_disease_db
- 模型：权重文件放入model/目录，后端utils/yolo_model.py集成

## 八、功能亮点
- 标准前后端分离，接口清晰，易于扩展
- 支持用户注册、登录、检测、历史、知识库、管理员管理
- YOLOv11推理接口预留，便于后续AI集成
- 代码结构规范，适合毕设/竞赛/二次开发

## 九、后续可扩展方向
- 集成YOLOv11模型推理与图片上传
- 支持批量检测、移动端适配
- 增加数据统计与可视化
- 优化权限与安全机制

---
如需详细设计文档、接口文档、数据库脚本等，请见docs/目录。
