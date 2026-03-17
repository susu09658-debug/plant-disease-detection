import request from './request';

export const getUserList = (params) => request.get('/user/admin/users/', { params });

export const updateUser = (id, data) => request.put(`/user/admin/users/${id}/`, data);

export const deleteUser = (id) => request.delete(`/user/admin/users/${id}/`);
