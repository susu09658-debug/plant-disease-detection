# 植物病害检测系统设计文档（更新版）

## 1. 文档目的
本文件用于同步当前代码实现状态，重点说明认证模块的实际落地策略，避免与旧版需求描述不一致。

## 2. 认证与注册设计（已更新）
- 注册功能：不使用短信验证码
- 注册字段：username、phone、password
- 登录功能：使用图片验证码
- 登录字段：username、password、captcha、captcha_token

## 3. 图片验证码设计
- 接口：GET /api/user/captcha/
- 返回：token + base64验证码图片
- 验证策略：
  - 验证码值存储于服务端缓存
  - 默认有效期300秒
  - 登录校验通过后删除验证码，防止重复使用

## 4. 用户模块接口
- POST /api/user/register/
- POST /api/user/login/
- GET /api/user/captcha/

## 5. 前后端协同约束
- 前端注册页不得展示或校验短信验证码
- 前端注册请求体禁止提交sms_code、email等后端未定义字段
- 前端登录页必须先拉取图片验证码，再提交登录
- 后端统一返回格式：code、msg、data

## 6. 变更记录（2026-03-18）
- 移除短信验证码接口与前端流程
- 修复注册表单与后端字段不一致问题
- 统一登录验证码路径为 /api/user/captcha/
- 更新README接口说明与认证流程说明
