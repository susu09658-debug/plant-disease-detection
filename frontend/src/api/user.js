import request from './request';

/**
 * 获取验证码
 * @returns {Promise} 返回包含验证码数据（如图片流或 base64）的 Promise
 */
export const getCaptcha = () => request.get('/user/captcha/');

/**
 * 用户登录
 * @param {Object} data - 登录表单数据 (通常包含 username, password, 可能还有验证码)
 * @returns {Promise} 
 */
export const login = (data) => request.post('/user/login/', data);

/**
 * 用户注册
 * @param {Object} data - 注册表单数据
 * @returns {Promise}
 */
export const register = (data) => request.post('/user/register/', data);

/**
 * 用户登出
 * @returns {Promise}
 */
export const logout = () => request.post('/user/logout/');

/**
 * 获取用户个人信息
 * @returns {Promise} 返回包含当前登录用户详细信息的 Promise
 */
export const getProfile = () => request.get('/user/profile/');

/**
 * 更新用户个人信息
 * @param {Object} data - 需要修改的用户信息字段
 * @returns {Promise}
 */
export const updateProfile = (data) => request.put('/user/profile/', data);

/**
 * 上传用户头像
 * @param {FormData} formData - 包含头像图片文件的 FormData 对象
 * @returns {Promise} 返回包含新头像 URL 或相关状态的 Promise
 */
export const uploadAvatar = (formData) => request.post('/user/avatar/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
});

/**
 * 修改密码 (通常用于用户已登录状态下，通过旧密码修改新密码)
 * @param {Object} data - 密码数据 (通常包含 old_password, new_password 等)
 * @returns {Promise}
 */
export const updatePassword = (data) => request.put('/user/password/', data);

/**
 * 重置密码 (通常用于用户忘记密码时，通过邮箱/手机验证码重置)
 * @param {Object} data - 重置密码所需数据 (通常包含 token/code 以及新密码)
 * @returns {Promise}
 */
export const resetPassword = (data) => request.post('/user/reset-password/', data);