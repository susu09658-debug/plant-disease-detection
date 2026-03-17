import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', redirect: '/login' },
        {
            path: '/login',
            name: 'login',
            component: Login,
            meta: { guest: true },
        },
        {
            path: '/app',
            component: () => import('../layouts/MainLayout.vue'),
            meta: { requiresAuth: true },
            redirect: '/app/dashboard',
            children: [
                {
                    path: 'dashboard',
                    name: 'dashboard',
                    component: () => import('../views/Dashboard.vue'),
                    meta: { title: '系统首页' },
                },
                {
                    path: 'detect',
                    name: 'detect',
                    component: () => import('../views/Detect.vue'),
                    meta: { title: '病害检测' },
                },
                {
                    path: 'history',
                    name: 'history',
                    component: () => import('../views/History.vue'),
                    meta: { title: '历史记录' },
                },
                {
                    path: 'knowledge',
                    name: 'knowledge',
                    component: () => import('../views/Knowledge.vue'),
                    meta: { title: '知识库' },
                },
                {
                    path: 'profile',
                    name: 'profile',
                    component: () => import('../views/Profile.vue'),
                    meta: { title: '个人中心' },
                },
                {
                    path: 'admin/users',
                    name: 'adminUsers',
                    component: () => import('../views/admin/UserManage.vue'),
                    meta: { title: '用户管理', admin: true },
                },
                {
                    path: 'admin/knowledge',
                    name: 'adminKnowledge',
                    component: () => import('../views/admin/KnowledgeManage.vue'),
                    meta: { title: '知识库管理', admin: true },
                },
            ],
        },
    ],
});

// 路由守卫
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token');
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || 'null');

    if (to.meta.requiresAuth && !token) {
        return next('/login');
    }
    if (to.meta.admin && userInfo?.is_admin !== 1) {
        return next('/app/dashboard');
    }
    if (to.meta.guest && token) {
        return next('/app/dashboard');
    }
    next();
});

export default router;
