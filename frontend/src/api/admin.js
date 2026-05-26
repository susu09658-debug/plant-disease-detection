import request from './request'; // 导入封装好的 axios 实例或请求工具

/**
 * 获取用户列表（管理员权限）
 * @param {Object} params - 筛选和分页参数，例如 { page: 1, size: 10, username: '张三' }
 * @returns {Promise} 返回包含用户列表数据的 Promise 对象
 */
export const getUserList = (params) => request.get('/user/admin/users/', { params });

/**
 * 更新用户信息
 * @param {String|Number} id - 目标用户的唯一标识 ID
 * @param {Object} data - 需要修改的用户数据对象
 * @returns {Promise} 返回操作结果的 Promise 对象
 */
export const updateUser = (id, data) => request.put(`/user/admin/users/${id}/`, data);

/**
 * 删除用户
 * @param {String|Number} id - 目标用户的唯一标识 ID
 * @returns {Promise} 返回操作结果的 Promise 对象
 */
export const deleteUser = (id) => request.delete(`/user/admin/users/${id}/`);