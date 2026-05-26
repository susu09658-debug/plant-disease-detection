import request from './request'; // 导入封装好的请求工具（通常是 axios 实例）

/**
 * 上传并进行检测
 * @param {FormData} formData - 包含待检测文件（如图片/视频）的表单数据
 * @returns {Promise}
 */
export const uploadDetect = (formData) => request.post('/detect/upload/', formData, {
    // 关键：上传文件必须指定 Content-Type 为 multipart/form-data
    headers: { 'Content-Type': 'multipart/form-data' },
});

/**
 * 获取检测历史记录列表
 * @param {Object} params - 过滤或分页参数，例如 { page: 1, limit: 20, status: 'completed' }
 * @returns {Promise}
 */
export const getHistory = (params) => request.get('/detect/history/', { params });

/**
 * 获取单条检测记录的详细信息
 * @param {String|Number} id - 检测记录的唯一 ID
 * @returns {Promise}
 */
export const getDetail = (id) => request.get(`/detect/history/${id}/`);

/**
 * 删除单条检测记录
 * @param {String|Number} id - 要删除的记录 ID
 * @returns {Promise}
 */
export const deleteRecord = (id) => request.delete(`/detect/history/${id}/`);

/**
 * 批量删除检测记录
 * @param {Array} ids - 包含多个记录 ID 的数组，例如 [1, 2, 3]
 * @returns {Promise}
 */
export const batchDelete = (ids) => request.delete('/detect/history/', { 
    // 注意：axios 的 delete 方法传递 body 数据需要放在 data 字段中
    data: { ids } 
});

/**
 * 获取检测相关的统计数据
 * @returns {Promise} - 通常返回检测总数、成功率等看板数据
 */
export const getStats = () => request.get('/detect/stats/');

/**
 * 获取可用的检测模型列表
 * @returns {Promise} - 返回当前系统支持的 AI 模型选项
 */
export const getDetectModels = () => request.get('/detect/models/');