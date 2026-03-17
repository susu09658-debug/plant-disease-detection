<template>
  <div class="auth-page">
    <div class="auth-card-wrapper">
      <el-card class="white-card" shadow="hover">
        <div class="auth-header">
          <h2>植物病害智能检测系统</h2>
          <p>基于 YOLOv11 的高效识别平台</p>
        </div>

        <el-tabs v-model="activeTab" class="auth-tabs">
          <el-tab-pane label="用户登录" name="login">
            <el-form 
              ref="loginFormRef" 
              :model="loginForm" 
              :rules="loginRules" 
              label-width="0"
              size="large"
            >
              <el-form-item prop="username">
                <el-input v-model="loginForm.username" placeholder="请输入用户名" prefix-icon="User" />
              </el-form-item>
              <el-form-item prop="password">
                <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password prefix-icon="Lock" />
              </el-form-item>
              <el-button type="primary" class="submit-btn" :loading="loading" @click="handleLogin">
                登 录
              </el-button>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="账号注册" name="register">
            <el-form 
              ref="registerFormRef" 
              :model="registerForm" 
              :rules="registerRules" 
              label-width="0"
              size="large"
            >
              <el-form-item prop="username">
                <el-input v-model="registerForm.username" placeholder="请设置用户名" prefix-icon="User" />
              </el-form-item>
              <el-form-item prop="phone">
                <el-input v-model="registerForm.phone" placeholder="请输入11位手机号" prefix-icon="Iphone" />
              </el-form-item>
              <el-form-item prop="password">
                <el-input v-model="registerForm.password" type="password" placeholder="请设置密码" show-password prefix-icon="Lock" />
              </el-form-item>
              <el-button type="success" class="submit-btn" :loading="loading" @click="handleRegister">
                立 即 注 册
              </el-button>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { User, Lock, Iphone } from '@element-plus/icons-vue';
import request from '../api/request';
import { useRouter } from 'vue-router';

const router = useRouter();

const activeTab = ref('login');
const loading = ref(false);

const loginFormRef = ref(null);
const registerFormRef = ref(null);

const loginForm = reactive({ username: '', password: '' });
const registerForm = reactive({ username: '', phone: '', password: '' });

const validatePhone = (rule, value, callback) => {
  const phoneRegex = /^1[3-9]\d{9}$/;
  if (!value) {
    callback(new Error('手机号不能为空'));
  } else if (!phoneRegex.test(value)) {
    callback(new Error('请输入正确的11位手机号码'));
  } else {
    callback();
  }
};

const loginRules = reactive({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
});

const registerRules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  phone: [{ required: true, validator: validatePhone, trigger: 'blur' }],
  password: [
    { required: true, message: '请设置密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
});

const handleLogin = async () => {
  const formEl = loginFormRef.value;
  if (!formEl) return;
  const valid = await formEl.validate().catch(() => false);
  if (!valid) return;

  loading.value = true;
  try {
    const res = await request.post('/user/login/', loginForm);
    localStorage.setItem('token', res.data.token || '');
    localStorage.setItem('userInfo', JSON.stringify(res.data.user_info || {}));
    ElMessage.success('登录成功，欢迎回来！');
    router.push('/index');
  } catch (error) {
    console.error('登录失败', error);
  } finally {
    loading.value = false;
  }
};

const handleRegister = async () => {
  const formEl = registerFormRef.value;
  if (!formEl) return;
  const valid = await formEl.validate().catch(() => false);
  if (!valid) return;

  loading.value = true;
  try {
    await request.post('/user/register/', registerForm);
    ElMessage.success('注册成功！请登录');
    formEl.resetFields();
    activeTab.value = 'login';
  } catch (error) {
    console.error('注册失败', error);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* 页面容器 —— 极简白色背景 */
.auth-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ffffff;
}

/* 卡片容器 */
.auth-card-wrapper {
  width: 100%;
  max-width: 400px;
  padding: 0 20px;
}

/* 纯白卡片 */
.white-card {
  border-radius: 12px;
  border: 1px solid #f1f1f1;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

/* 标题区域 */
.auth-header {
  text-align: center;
  padding: 10px 0 20px;
}

.auth-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #333;
}

.auth-header p {
  margin: 6px 0 0;
  font-size: 14px;
  color: #999;
}

/* 按钮样式 */
.submit-btn {
  width: 100%;
  height: 44px;
  margin-top: 10px;
  font-size: 16px;
  letter-spacing: 1px;
  border-radius: 6px;
}

/* 标签页样式 —— 简洁无彩色 */
:deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
  color: #666;
}

:deep(.el-tabs__item.is-active) {
  color: #409eff;
  font-weight: 600;
}

:deep(.el-tabs__nav) {
  width: 100%;
  display: flex;
}

:deep(.el-tabs__item.is-top) {
  flex: 1;
  text-align: center;
  padding: 0;
}

/* 输入框样式 */
:deep(.el-input__wrapper) {
  border-radius: 6px;
  box-shadow: none;
  border: 1px solid #e5e6eb;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}
</style>