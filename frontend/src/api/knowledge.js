import request from './request'; 

/**
 * 获取知识列表
 * @param {Object} params - 查询参数，例如 { page: 1, pageSize: 10, keyword: '关键字' }
 * @returns {Promise} 
 */
export const getList = (params) => request.get('/knowledge/list/', { params });

/**
 * 获取指定知识详情
 * @param {String|Number} id - 知识条目的唯一标识 ID
 * @returns {Promise}
 */
export const getDetail = (id) => request.get(`/knowledge/${id}/`);

/**
 * 新增知识条目
 * @param {Object} data - 表单数据对象
 * @returns {Promise}
 */
export const createKnowledge = (data) => request.post('/knowledge/manage/', data);

/**
 * 更新/编辑已有知识条目
 * @param {String|Number} id - 需要修改的知识 ID
 * @param {Object} data - 更新后的数据对象
 * @returns {Promise}
 */
export const updateKnowledge = (id, data) => request.put(`/knowledge/manage/${id}/`, data);

/**
 * 删除指定知识条目
 * @param {String|Number} id - 需要删除的知识 ID
 * @returns {Promise}
 */
export const deleteKnowledge = (id) => request.delete(`/knowledge/manage/${id}/`);