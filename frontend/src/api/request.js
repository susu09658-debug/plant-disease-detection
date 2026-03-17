import axios from 'axios';
import { ElMessage } from 'element-plus';

const service = axios.create({
    baseURL: '/api',
    timeout: 15000,
});

// 请求拦截器：自动注入 Authorization: Bearer <token>
service.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    error => Promise.reject(error)
);

// 响应拦截器
service.interceptors.response.use(
    response => {
        const res = response.data;
        if (res.code !== 200) {
            ElMessage.error(res.msg || '请求失败');
            if (res.code === 401) {
                localStorage.removeItem('token');
                localStorage.removeItem('userInfo');
                window.location.href = '/login'; // redirect to login page
            }
            return Promise.reject(new Error(res.msg || 'Error'));
        }
        return res;
    },
    error => {
        const status = error?.response?.status;
        if (status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('userInfo');
            window.location.href = '/login'; // redirect to login page
            ElMessage.error('登录已过期，请重新登录');
        } else {
            ElMessage.error(error?.response?.data?.msg || '网络请求失败，请稍后再试');
        }
        return Promise.reject(error);
    }
);

export default service;
