<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '210px'" class="sidebar">
      <div class="logo-area" @click="toggleCollapse">
        <span class="logo-icon">🌿</span>
        <span v-if="!isCollapse" class="logo-text">植物病害检测</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        router
        :collapse="isCollapse"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        class="sidebar-menu"
      >
        <el-menu-item index="/app/dashboard">
          <el-icon><House /></el-icon>
          <template #title>系统首页</template>
        </el-menu-item>

        <el-menu-item index="/app/detect">
          <el-icon><Search /></el-icon>
          <template #title>病害检测</template>
        </el-menu-item>

        <el-menu-item index="/app/history">
          <el-icon><List /></el-icon>
          <template #title>历史记录</template>
        </el-menu-item>

        <el-menu-item index="/app/knowledge">
          <el-icon><Reading /></el-icon>
          <template #title>知识库</template>
        </el-menu-item>

        <el-sub-menu index="model">
          <template #title>
            <el-icon><Cpu /></el-icon>
            <span>模型与数据</span>
          </template>
          <el-menu-item v-if="userStore.isAdmin" index="/app/dataset">
            <el-icon><FolderOpened /></el-icon>
            数据集管理
          </el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/app/training">
            <el-icon><Aim /></el-icon>
            模型训练
          </el-menu-item>
          <el-menu-item index="/app/experiment">
            <el-icon><DataAnalysis /></el-icon>
            实验结果
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/app/profile">
          <el-icon><User /></el-icon>
          <template #title>个人中心</template>
        </el-menu-item>

        <!-- 管理员菜单 -->
        <el-sub-menu v-if="userStore.isAdmin" index="admin">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>管理后台</span>
          </template>
          <el-menu-item index="/app/admin/users">
            <el-icon><UserFilled /></el-icon>
            用户管理
          </el-menu-item>
          <el-menu-item index="/app/admin/knowledge">
            <el-icon><EditPen /></el-icon>
            知识库管理
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container class="right-container">
      <!-- 顶部导航栏 -->
      <el-header class="navbar">
        <div class="navbar-left">
          <el-icon class="collapse-btn" @click="toggleCollapse">
            <Fold v-if="!isCollapse" /><Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item :to="{ path: '/app/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="navbar-right">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" :src="avatarUrl" class="user-avatar">
                {{ userInfo?.username?.charAt(0)?.toUpperCase() || 'U' }}
              </el-avatar>>
              <span class="username">{{ userInfo?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessageBox } from 'element-plus';
import { useUserStore } from '../store/user';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const isCollapse = ref(false);

const userInfo = computed(() => userStore.userInfo);
const avatarUrl = computed(() => {
  const avatar = userInfo.value?.avatar;
  if (!avatar) return ''; 

  // 如果已经是完整路径 (以 http 开头)，直接返回
  if (avatar.startsWith('http')) return avatar;

  // 从环境变量读取 API 地址
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  // 规范拼接：确保 baseUrl 和 avatar 之间只有一个斜杠
  // 即使 avatar 开头有斜杠也能正确处理
  return `${baseUrl}/${avatar}`.replace(/([^:])\/\/+/g, '$1/');
});
const activeMenu = computed(() => route.path);
const currentTitle = computed(() => route.meta?.title || '');

const toggleCollapse = () => {
    isCollapse.value = !isCollapse.value;
};

const handleCommand = async (cmd) => {
    if (cmd === 'profile') {
        router.push('/app/profile');
    } else if (cmd === 'logout') {
        await ElMessageBox.confirm('确认退出登录？', '提示', {
            confirmButtonText: '确认',
            cancelButtonText: '取消',
            type: 'warning',
        }).catch(() => null);
        await userStore.logout();
        router.push('/login');
    }
};
import { onMounted, watch } from 'vue';

// 页面加载完看一眼
onMounted(() => {
  console.log('--- 调试头像信息 ---');
  console.log('原始 userInfo:', userStore.userInfo);
  console.log('拼接后的 avatarUrl:', avatarUrl.value);
});

// 如果数据是异步获取的，监听它
watch(() => userStore.userInfo, (newVal) => {
  console.log('UserInfo 变动了:', newVal?.avatar);
}, { deep: true });
</script>

<style scoped>
.main-layout {
    height: 100vh;
    overflow: hidden;
}

.sidebar {
    background-color: #304156;
    transition: width 0.3s;
    overflow: hidden;
}

.logo-area {
    height: 60px;
    display: flex;
    align-items: center;
    padding: 0 16px;
    cursor: pointer;
    border-bottom: 1px solid #3a4d65;
    overflow: hidden;
    white-space: nowrap;
}

.logo-icon {
    font-size: 24px;
    flex-shrink: 0;
}

.logo-text {
    margin-left: 10px;
    color: #fff;
    font-size: 15px;
    font-weight: 600;
}

.sidebar-menu {
    border-right: none;
}

.right-container {
    flex: 1;
    overflow: hidden;
    flex-direction: column;
}

.navbar {
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    border-bottom: 1px solid #e6e6e6;
    height: 60px;
    box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.navbar-left {
    display: flex;
    align-items: center;
    gap: 14px;
}

.collapse-btn {
    font-size: 20px;
    cursor: pointer;
    color: #5a6678;
}

.navbar-right {
    display: flex;
    align-items: center;
}

.user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    color: #333;
    font-size: 14px;
}

.user-avatar {
    background-color: #409eff;
    color: #fff;
    font-size: 14px;
}

.username {
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.main-content {
    background: #f5f7fa;
    overflow-y: auto;
    padding: 20px;
}
</style>
