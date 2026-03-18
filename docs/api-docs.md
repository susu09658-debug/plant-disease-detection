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

---

## 五、实验结果模块 `/api/experiment/`

### 5.1 获取评估指标

- **GET** `/api/experiment/metrics/`
- 认证：Bearer Token

响应示例：

```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "metrics": {
      "mAP50": 0.8742,
      "mAP50_95": 0.6518,
      "precision": 0.8923,
      "recall": 0.8456,
      "f1_score": 0.8683,
      "train_box_loss": 0.0312,
      "train_cls_loss": 0.0245,
      "val_box_loss": 0.0489,
      "val_cls_loss": 0.0367,
      "epochs_completed": 100
    },
    "train_config": {
      "model": "yolov8n.pt",
      "epochs": 100,
      "batch": 16,
      "imgsz": 640,
      "optimizer": "SGD",
      "lr0": 0.01
    },
    "class_names": { "0": "Tomato_Early_Blight", "1": "Tomato_Late_Blight" },
    "class_names_cn": { "0": "番茄早疫病", "1": "番茄晚疫病" },
    "num_classes": 10,
    "charts": { "results": "results.png", "confusion_matrix": "confusion_matrix.png" },
    "run_name": "plant_disease"
  }
}
```

### 5.2 获取训练曲线

- **GET** `/api/experiment/curves/`
- 认证：Bearer Token

响应示例：

```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "epochs": [1, 2, 3],
    "train_box_loss": [0.08, 0.06, 0.04],
    "train_cls_loss": [0.06, 0.04, 0.03],
    "val_box_loss": [0.10, 0.08, 0.06],
    "val_cls_loss": [0.08, 0.06, 0.05],
    "mAP50": [0.30, 0.55, 0.70],
    "mAP50_95": [0.15, 0.35, 0.50],
    "precision": [0.40, 0.60, 0.75],
    "recall": [0.35, 0.55, 0.70]
  }
}
```

### 5.3 获取模型信息

- **GET** `/api/experiment/model-info/`
- 认证：Bearer Token

响应示例：

```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "model_loaded": true,
    "model_path": "/path/to/model/best.pt",
    "model_version": "yolov8n.pt",
    "num_classes": 10,
    "class_names": { "0": "Tomato_Early_Blight" },
    "class_names_cn": { "0": "番茄早疫病" },
    "input_size": 640,
    "file_size_mb": 6.23,
    "has_train_records": true,
    "latest_run": "plant_disease"
  }
}
```
