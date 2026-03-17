# 系统设计文档

## 一、系统架构

### 1.1 总体架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端 (Vue3 + Vite)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ 登录注册  │ │ 系统首页  │ │ 病害检测  │ │ 历史记录  │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                 │
│  │ 知识库   │ │ 个人中心  │ │ 管理后台  │                 │
│  └──────────┘ └──────────┘ └──────────┘                 │
│         ↕ Axios (JWT Bearer Token)                       │
├─────────────────────────────────────────────────────────┤
│                 后端 (Django 6.0.3 + DRF)                 │
│  ┌───────────────────────────────────────────────┐      │
│  │ API Gateway (urls.py + JWT 认证中间件)          │      │
│  ├──────────┬──────────┬───────────┬─────────────┤      │
│  │ user app │detect app│knowledge  │  admin API  │      │
│  └──────────┴──────────┴───────────┴─────────────┘      │
│         ↕                    ↕                           │
│  ┌──────────┐       ┌──────────────┐                    │
│  │ MySQL 8.0│       │ YOLOv11 Model│                    │
│  └──────────┘       └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

### 1.2 技术栈

| 层次      | 技术选型                                    |
|-----------|---------------------------------------------|
| 前端框架  | Vue 3 + Vite + Element Plus                 |
| 前端状态  | Pinia                                       |
| 前端路由  | Vue Router 4（Hash/History 模式）           |
| HTTP 客户端| Axios（统一封装，JWT 拦截器）              |
| 后端框架  | Django 6.0.3 + Django REST Framework 3.15.2 |
| 认证方式  | JWT（PyJWT 2.10.1）                          |
| 密码加密  | Django PBKDF2（make_password/check_password）|
| AI 模型   | YOLOv11（ultralytics）                       |
| 数据库    | MySQL 8.0                                   |
| 缓存      | Django LocMemCache（验证码存储）             |
| 跨域      | django-cors-headers                         |
| 文件存储  | 本地媒体文件（MEDIA_ROOT）                   |

## 二、模块划分

### 2.1 后端模块

| 模块        | 路由前缀           | 说明                           |
|-------------|--------------------|---------------------------------|
| 用户模块    | /api/user/         | 注册、登录、个人信息、密码管理  |
| 检测模块    | /api/detect/       | 图片上传、YOLO推理、历史记录    |
| 知识库模块  | /api/knowledge/    | 病害知识浏览与管理              |
| 管理员模块  | /api/user/admin/   | 用户列表、用户状态管理          |

### 2.2 前端模块

| 路由              | 组件                    | 说明           |
|-------------------|-------------------------|----------------|
| /login            | Login.vue               | 登录注册页     |
| /app/dashboard    | Dashboard.vue           | 系统首页仪表盘 |
| /app/detect       | Detect.vue              | 病害检测页     |
| /app/history      | History.vue             | 历史记录页     |
| /app/knowledge    | Knowledge.vue           | 知识库浏览页   |
| /app/profile      | Profile.vue             | 个人中心页     |
| /app/admin/users  | admin/UserManage.vue    | 用户管理（管理员）|
| /app/admin/knowledge | admin/KnowledgeManage.vue | 知识库管理（管理员）|

## 三、认证流程

```
前端                                后端
 │                                    │
 │  POST /api/user/login/             │
 │  {username, password, captcha}     │
 │ ─────────────────────────────────► │
 │                                    │  check_password(pwd, user.password)
 │  {token: "eyJ...", user_info: ...} │
 │ ◄───────────────────────────────── │
 │                                    │
 │  localStorage.setItem('token', ...) │
 │                                    │
 │  GET /api/detect/stats/            │
 │  Authorization: Bearer eyJ...      │
 │ ─────────────────────────────────► │
 │                                    │  JWTAuthentication.authenticate()
 │                                    │  jwt.decode(token, SECRET_KEY)
 │  {code: 200, data: {...}}          │
 │ ◄───────────────────────────────── │
```

## 四、安全设计

1. **密码存储**：使用 Django `make_password`（PBKDF2+SHA256），取代不安全的 MD5
2. **JWT Token**：payload 包含 user_id、username、is_admin、exp（7天过期），使用 SECRET_KEY 签名
3. **路由守卫**：前端 `router.beforeEach` 拦截未认证访问，401 响应自动清除 token 并跳转登录页
4. **CORS**：通过 `django-cors-headers` 统一控制跨域
5. **验证码**：登录需输入图形验证码，5分钟有效期，验证后立即删除

## 五、YOLO 推理降级策略

- 正常情况：加载 `model/best.pt`，调用 YOLOv11 推理
- 模型文件不存在时：返回随机模拟数据（便于开发调试，不影响系统其他功能运行）
- 推理出错时：捕获异常并降级返回模拟数据
