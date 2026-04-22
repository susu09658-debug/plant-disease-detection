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
// 响应拦截器
service.interceptors.response.use(
    response => {
        const res = response.data;
        if (res.code !== 200) {
            // 弹出后端给的错误信息
            ElMessage.error(res.msg || '请求失败');
            
            //  核心修复：只有当不在登录页时，遇到 401 才执行强制跳转
            // 避免在登录页输错密码时被无限刷新页面掩盖了错误提示
            const currentPath = window.location.pathname;
            if (res.code === 401 && currentPath !== '/login') {
                localStorage.removeItem('token');
                localStorage.removeItem('userInfo');
                window.location.href = '/login'; 
            }
            
            // 抛出异常，阻断正常的 await 流程，让它跳进组件的 catch 里
            return Promise.reject(new Error(res.msg || 'Error'));
        }
        return res;
    },
    error => {
        const status = error?.response?.status;
        if (status === 401) {
            // 这里同样做一下路径保护
            const currentPath = window.location.pathname;
            if (currentPath !== '/login') {
                localStorage.removeItem('token');
                localStorage.removeItem('userInfo');
                window.location.href = '/login'; 
                ElMessage.error('登录已过期，请重新登录');
            } else {
                ElMessage.error(error?.response?.data?.msg || '验证失败');
            }
        } else {
            ElMessage.error(error?.response?.data?.msg || '网络请求失败，请稍后再试');
        }
        return Promise.reject(error);
    }
);

export default service;
