import request from './request';

export const getList = (params) => request.get('/knowledge/list/', { params });

export const getDetail = (id) => request.get(`/knowledge/${id}/`);

export const createKnowledge = (data) => request.post('/knowledge/manage/', data);

export const updateKnowledge = (id, data) => request.put(`/knowledge/manage/${id}/`, data);

export const deleteKnowledge = (id) => request.delete(`/knowledge/manage/${id}/`);
