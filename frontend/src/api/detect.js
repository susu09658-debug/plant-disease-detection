import request from './request';

export const uploadDetect = (formData) => request.post('/detect/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
});

export const getModelList = () => request.get('/detect/models/');

export const getHistory = (params) => request.get('/detect/history/', { params });

export const getDetail = (id) => request.get(`/detect/history/${id}/`);

export const deleteRecord = (id) => request.delete(`/detect/history/${id}/`);

export const batchDelete = (ids) => request.delete('/detect/history/', { data: { ids } });

export const getStats = () => request.get('/detect/stats/');
