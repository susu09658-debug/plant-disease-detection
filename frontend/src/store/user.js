import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { login as apiLogin, logout as apiLogout, getProfile } from '../api/user';

export const useUserStore = defineStore('user', () => {
    const token = ref(localStorage.getItem('token') || '');
    const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'));

    const isLoggedIn = computed(() => !!token.value);
    const isAdmin = computed(() => userInfo.value?.is_admin === 1);

    async function login(credentials) {
        const res = await apiLogin(credentials);
        token.value = res.data.token;
        userInfo.value = res.data.user_info;
        localStorage.setItem('token', res.data.token);
        localStorage.setItem('userInfo', JSON.stringify(res.data.user_info));
        return res;
    }

    async function logout() {
        try {
            await apiLogout();
        } catch {}
        token.value = '';
        userInfo.value = null;
        localStorage.removeItem('token');
        localStorage.removeItem('userInfo');
    }

    async function fetchProfile() {
        const res = await getProfile();
        userInfo.value = res.data;
        localStorage.setItem('userInfo', JSON.stringify(res.data));
        return res.data;
    }

    return { token, userInfo, isLoggedIn, isAdmin, login, logout, fetchProfile };
});
