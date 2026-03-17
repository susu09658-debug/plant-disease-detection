import axios from 'axios';

const service = axios.create({
    baseURL: 'http://127.0.0.1:8000/api', // 指向你的 Django 地址
    timeout: 5000
});

// 响应拦截器
service.interceptors.response.use(
    response => {
        const res = response.data;
        if (res.code !== 200) {
            alert(res.msg || 'Error');
            return Promise.reject(new Error(res.msg || 'Error'));
        }
        return res;
    },
    error => {
        alert('网络请求失败');
        return Promise.reject(error);
    }
);

export default service;