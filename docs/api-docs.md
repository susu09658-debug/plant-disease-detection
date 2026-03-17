# API 接口文档

## 统一响应格式

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {}
}
```

| 状态码 | 含义           |
|--------|----------------|
| 200    | 成功           |
| 400    | 请求参数错误   |
| 401    | 未认证/Token无效 |
| 403    | 无权限         |
| 404    | 资源不存在     |
| 500    | 服务器内部错误 |

---

## 一、用户模块 `/api/user/`

### 1.1 获取图形验证码

- **GET** `/api/user/captcha/`
- 认证：无

响应：
```json
{
  "code": 200,
  "data": {
    "token": "abc123...",
    "image": "data:image/png;base64,..."
  }
}
```

### 1.2 用户注册

- **POST** `/api/user/register/`
- 认证：无

请求体：
```json
{
  "username": "testuser",
  "phone": "13800138000",
  "password": "Password123"
}
```

### 1.3 用户登录

- **POST** `/api/user/login/`
- 认证：无

请求体：
```json
{
  "username": "testuser",
  "password": "Password123",
  "captcha": "A1B2",
  "captcha_token": "abc123..."
}
```

响应：
```json
{
  "code": 200,
  "data": {
    "token": "eyJ0eXAiOiJKV1Q...",
    "user_info": {
      "id": 1,
      "username": "testuser",
      "phone": "138...",
      "is_admin": 0
    }
  }
}
```

### 1.4 用户登出

- **POST** `/api/user/logout/`
- 认证：Bearer Token

### 1.5 获取个人信息

- **GET** `/api/user/profile/`
- 认证：Bearer Token

### 1.6 修改个人信息

- **PUT** `/api/user/profile/`
- 认证：Bearer Token

请求体：
```json
{"phone": "13900139000", "email": "user@example.com"}
```

### 1.7 修改密码

- **PUT** `/api/user/password/`
- 认证：Bearer Token

```json
{"old_password": "OldPass123", "new_password": "NewPass456"}
```

---

## 二、检测模块 `/api/detect/`

### 2.1 上传图片检测

- **POST** `/api/detect/upload/`
- 认证：Bearer Token
- Content-Type: multipart/form-data

| 参数  | 类型 | 必填 | 说明               |
|-------|------|------|--------------------|
| image | File | 是   | JPG/PNG，最大 10MB |

响应：
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "disease_name": "番茄叶枯病",
    "plant_name": "番茄",
    "confidence": 0.932,
    "original_img_url": "http://127.0.0.1:8000/media/uploads/xxx.jpg",
    "result_img_url": "http://127.0.0.1:8000/media/results/xxx.jpg",
    "detect_time": "2026-03-17T20:00:00"
  }
}
```

### 2.2 历史记录列表

- **GET** `/api/detect/history/?page=1&page_size=10&keyword=番茄`
- 认证：Bearer Token

### 2.3 删除历史记录（批量）

- **DELETE** `/api/detect/history/`
- 认证：Bearer Token

```json
{"ids": [1, 2, 3]}
```

### 2.4 单条记录详情

- **GET** `/api/detect/history/<id>/`
- 认证：Bearer Token

### 2.5 删除单条记录

- **DELETE** `/api/detect/history/<id>/`
- 认证：Bearer Token

### 2.6 检测统计

- **GET** `/api/detect/stats/`
- 认证：Bearer Token

---

## 三、知识库模块 `/api/knowledge/`

### 3.1 知识库列表

- **GET** `/api/knowledge/list/?page=1&page_size=9&plant_name=番茄&disease_name=叶枯`
- 认证：Bearer Token

### 3.2 知识详情

- **GET** `/api/knowledge/<id>/`
- 认证：Bearer Token

### 3.3 新增知识（管理员）

- **POST** `/api/knowledge/manage/`
- 认证：Bearer Token（管理员）

```json
{
  "plant_name": "番茄",
  "disease_name": "叶枯病",
  "symptom": "叶片出现...",
  "treatment": "及时喷洒...",
  "severity": 3
}
```

### 3.4 编辑知识（管理员）

- **PUT** `/api/knowledge/manage/<id>/`
- 认证：Bearer Token（管理员）

### 3.5 删除知识（管理员）

- **DELETE** `/api/knowledge/manage/<id>/`
- 认证：Bearer Token（管理员）

---

## 四、管理员模块 `/api/user/admin/`

### 4.1 用户列表

- **GET** `/api/user/admin/users/?page=1&page_size=10&keyword=test`
- 认证：Bearer Token（管理员）

### 4.2 编辑用户

- **PUT** `/api/user/admin/users/<id>/`
- 认证：Bearer Token（管理员）

```json
{"is_active": 0, "is_admin": 1}
```

### 4.3 删除用户

- **DELETE** `/api/user/admin/users/<id>/`
- 认证：Bearer Token（管理员）
