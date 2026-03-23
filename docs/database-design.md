# 数据库设计文档

## 一、数据库信息

- 数据库类型：MySQL 8.0
- 数据库名：`plant_disease_db`
- 字符集：utf8mb4
- 排序规则：utf8mb4_unicode_ci

## 二、数据表设计

### 2.1 用户表 `user_user`

| 字段        | 类型          | 约束                    | 说明             |
|-------------|---------------|-------------------------|------------------|
| id          | bigint        | PK, AUTO_INCREMENT      | 用户ID           |
| username    | varchar(20)   | NOT NULL, UNIQUE        | 用户ID（唯一，用于登录） |
| nickname    | varchar(20)   | NOT NULL, DEFAULT ''    | 用户昵称（用于展示）     |
| password    | varchar(128)  | NOT NULL                | PBKDF2加密密码   |
| phone       | varchar(11)   | NOT NULL                | 手机号           |
| email       | varchar(50)   | NULL                    | 邮箱（可选）     |
| avatar      | varchar(255)  | NULL                    | 头像路径（可选） |
| is_admin    | int           | DEFAULT 0               | 0=普通, 1=管理员 |
| is_active   | int           | DEFAULT 1               | 0=禁用, 1=启用   |
| last_login  | datetime      | NULL                    | 最后登录时间     |
| create_time | datetime      | DEFAULT NOW             | 注册时间         |
| update_time | datetime      | AUTO UPDATE             | 更新时间         |

**索引：**
- PRIMARY KEY: `id`
- UNIQUE INDEX: `username`

---

### 2.2 检测历史表 `detect_record`

| 字段         | 类型         | 约束                  | 说明             |
|--------------|--------------|-----------------------|------------------|
| id           | bigint       | PK, AUTO_INCREMENT    | 记录ID           |
| user_id      | bigint       | FK → user_user.id     | 关联用户ID       |
| original_img | varchar(255) | NOT NULL              | 原始图片相对路径 |
| result_img   | varchar(255) | NULL                  | 标注图片相对路径 |
| disease_name | varchar(50)  | NOT NULL              | 检测病害名称     |
| plant_name   | varchar(30)  | NULL                  | 植物名称         |
| confidence   | float        | NOT NULL              | 置信度（0~1）    |
| bbox_data    | json         | NULL                  | 检测框坐标JSON   |
| detect_time  | datetime     | DEFAULT NOW           | 检测时间         |

**索引：**
- PRIMARY KEY: `id`
- INDEX: `user_id`（外键索引）
- INDEX: `detect_time`（时间查询优化）

**外键约束：**
- `user_id` → `user_user.id` ON DELETE CASCADE

---

### 2.3 病害知识库表 `knowledge_info`

| 字段         | 类型         | 约束               | 说明             |
|--------------|--------------|--------------------|------------------|
| id           | bigint       | PK, AUTO_INCREMENT | 知识ID           |
| plant_name   | varchar(30)  | NOT NULL, INDEX    | 植物名称         |
| disease_name | varchar(50)  | NOT NULL, INDEX    | 病害名称         |
| symptom      | text         | NOT NULL           | 病害症状描述     |
| treatment    | text         | NOT NULL           | 防治方法         |
| image_url    | varchar(255) | NULL               | 参考图片URL      |
| severity     | int          | DEFAULT 1          | 严重等级（1-5）  |
| create_time  | datetime     | DEFAULT NOW        | 创建时间         |
| update_time  | datetime     | AUTO UPDATE        | 更新时间         |

**索引：**
- PRIMARY KEY: `id`
- INDEX: `plant_name`（按植物名搜索优化）
- INDEX: `disease_name`（按病害名搜索优化）

## 三、ER 关系图

```
user_user (1) ──── (N) detect_record
```

知识库表 `knowledge_info` 是独立的，不与用户或检测记录存在外键关系，由管理员维护。

## 四、数据库初始化 SQL

```sql
CREATE DATABASE IF NOT EXISTS plant_disease_db
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE plant_disease_db;

-- 通过 Django migrate 命令自动创建所有表
```
