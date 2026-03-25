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
  "nickname": "测试用户",
  "phone": "13800138000",
  "password": "Password123"
}
```

> `username` 为用户ID（唯一，用于登录），`nickname` 为昵称（用于展示，选填，默认同用户ID）。

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
      "nickname": "测试用户",
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
{"nickname": "新昵称", "phone": "13900139000", "email": "user@example.com"}
```

> 支持修改昵称、手机号、邮箱。用户ID（username）注册后不可修改。

### 1.7 上传头像

- **POST** `/api/user/avatar/`
- 认证：Bearer Token
- Content-Type: multipart/form-data

| 参数   | 类型 | 必填 | 说明                       |
|--------|------|------|----------------------------|
| avatar | File | 是   | JPG/PNG/GIF，最大 2MB      |

响应：
```json
{
  "code": 200,
  "msg": "头像上传成功",
  "data": {
    "avatar": "/media/avatars/1_avatar.jpg"
  }
}
```

### 1.8 修改密码

- **PUT** `/api/user/password/`
- 认证：Bearer Token

```json
{"old_password": "OldPass123", "new_password": "NewPass456"}
```

### 1.9 忘记密码（重置密码）

- **POST** `/api/user/reset-password/`
- 认证：无

请求体：
```json
{
  "username": "testuser",
  "phone": "13800138000",
  "new_password": "NewPassword123",
  "captcha": "A1B2",
  "captcha_token": "abc123..."
}
```

响应：
```json
{
  "code": 200,
  "msg": "密码重置成功，请使用新密码登录",
  "data": null
}
```

错误响应：
| code | msg |
|------|-----|
| 400 | 用户名、手机号和新密码不能为空 |
| 400 | 图形验证码错误或已过期 |
| 400 | 新密码长度至少为8位 |
| 403 | 账号已被禁用，请联系管理员 |
| 404 | 用户信息验证失败 |

---

## 二、检测模块 `/api/detect/`

### 2.1 上传图片检测

- **POST** `/api/detect/upload/`
- 认证：Bearer Token
- Content-Type: multipart/form-data

| 参数      | 类型   | 必填 | 说明                               |
|-----------|--------|------|------------------------------------|
| image     | File   | 是   | JPG/PNG，最大 10MB                 |
| model_key | String | 否   | 模型标识（如 best、yolo11n、yolo11s），默认使用 best |

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
    "detect_time": "2026-03-17T20:00:00",
    "model_used": "best.pt"
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

### 2.7 可用模型列表

- **GET** `/api/detect/models/`
- 认证：Bearer Token

响应：
```json
{
  "code": 200,
  "data": [
    {"key": "best", "name": "best.pt", "path": "/path/to/best.pt", "size_mb": 5.21},
    {"key": "yolo11n", "name": "yolo11n.pt", "path": "/path/to/yolo11n.pt", "size_mb": 5.35}
  ]
}
```

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
      "model": "yolo11n.pt",
      "epochs": 100,
      "batch": 16,
      "imgsz": 640,
      "optimizer": "SGD",
      "lr0": 0.01
    },
    "class_names": { "0": "Apple_Scab_Leaf", "1": "Apple_leaf" },
    "class_names_cn": { "0": "苹果黑星病叶", "1": "苹果健康叶" },
    "num_classes": 29,
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
    "model_version": "yolo11n.pt",
    "num_classes": 29,
    "class_names": { "0": "Apple_Scab_Leaf" },
    "class_names_cn": { "0": "苹果黑星病叶" },
    "input_size": 640,
    "file_size_mb": 6.23,
    "has_train_records": true,
    "latest_run": "plant_disease"
  }
}
```

### 5.4 获取历史训练记录

- **GET** `/api/experiment/train-history/`
- 认证：Bearer Token

响应示例：

```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "runs": [
      {
        "name": "plant_disease",
        "model": "yolo11n.pt",
        "epochs": 100,
        "epochs_completed": 100,
        "batch": 16,
        "imgsz": 640,
        "optimizer": "SGD",
        "lr0": 0.01,
        "has_best_weight": true,
        "has_last_weight": true,
        "best_weight_size_mb": 6.23,
        "metrics": {
          "mAP50": 0.8742,
          "mAP50_95": 0.6518,
          "precision": 0.8923,
          "recall": 0.8456
        },
        "modified_time": "2026-03-18T10:00:00"
      }
    ]
  }
}
```

### 5.5 获取训练配置参数

- **GET** `/api/experiment/train-config/`
- 认证：Bearer Token

响应示例：

```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "config": { "model": "yolo11n.pt", "epochs": 100, "batch": 16 },
    "model_options": [
      { "name": "yolo11n.pt", "params": "2.6M", "desc": "超轻量 - 适合快速实验" },
      { "name": "yolo11s.pt", "params": "9.4M", "desc": "轻量 - 平衡精度与速度" }
    ],
    "num_classes": 29,
    "optimizer_options": ["SGD", "Adam", "AdamW"],
    "strategy_options": [
      { "key": "baseline", "name": "基线策略", "desc": "标准训练参数，适合作为对照基准" },
      { "key": "augment", "name": "数据增强策略", "desc": "强化数据增强，提升小样本类别效果" },
      { "key": "finetune", "name": "微调策略", "desc": "大模型 + AdamW + 余弦退火学习率" },
      { "key": "lightweight", "name": "轻量化策略", "desc": "轻量化部署，适合边缘设备" }
    ]
  }
}
```

---

## 六、数据集管理模块 `/api/dataset/`

### 6.1 获取数据集概览

- **GET** `/api/dataset/overview/`
- 认证：Bearer Token

响应示例：

```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "dataset_exists": true,
    "dataset_name": "FieldPlant",
    "dataset_source": "Roboflow (universe.roboflow.com/plant-disease-detection/fieldplant)",
    "num_classes": 27,
    "total_images": 2598,
    "total_labels": 2598,
    "splits": {
      "train": { "images": 2078, "labels": 2078 },
      "val": { "images": 260, "labels": 260 },
      "test": { "images": 260, "labels": 260 }
    },
    "class_details": [
      { "id": 0, "name": "Apple_Scab_Leaf", "name_cn": "苹果黑星病叶", "count": 95 }
    ]
  }
}
```

### 6.2 获取类别列表

- **GET** `/api/dataset/classes/`
- 认证：Bearer Token

### 6.3 获取样本列表

- **GET** `/api/dataset/samples/?split=train&class_id=0&limit=20`
- 认证：Bearer Token

### 6.4 获取划分信息

- **GET** `/api/dataset/split-info/`
- 认证：Bearer Token

### 6.5 验证数据集（管理员）

- **POST** `/api/dataset/validate/`
- 认证：Bearer Token（管理员）
