<template>
  <div class="auth-page">
    <div class="auth-card-wrapper">
      <el-card class="auth-card" shadow="hover">
        <div class="brand-area">
          <div class="brand-logo">🌿</div>
          <div>
            <h1>植物病害智能检测系统</h1>
            <p>企业级AI检测 | 实时监控 | 精准预警</p>
          </div>
        </div>

        <el-tabs v-model="activeTab" class="auth-tabs" type="border-card">
          <el-tab-pane label="登录" name="login">
            <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-width="0" size="large">
              <el-form-item prop="username">
                <el-input
                  v-model="loginForm.username"
                  placeholder="请输入用户名 / 邮箱"
                  prefix-icon="User"
                />
              </el-form-item>

              <el-form-item prop="captcha" class="captcha-item">
                <el-input
                  v-model="loginForm.captcha"
                  placeholder="请输入图形验证码"
                  prefix-icon="Picture"
                />
                <img
                  class="captcha-img"
                  :src="captchaImage"
                  @click="refreshCaptcha"
                  alt="验证码"
                  title="点击刷新"
                />
              </el-form-item>

              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  show-password
                  prefix-icon="Lock"
                />
              </el-form-item>

              <div class="quick-row">
                <el-checkbox v-model="loginForm.remember">7天内自动登录</el-checkbox>
                <a class="link-text" @click.prevent="onForgotPassword">忘记密码?</a>
              </div>

              <el-button :loading="loadingLogin" type="primary" class="submit-btn" @click="handleLogin">
                登录
              </el-button>

              <div class="hint">推荐使用企业邮箱登录，安全可审计。</div>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="注册" name="register">
            <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" label-width="0" size="large">
              <el-form-item prop="username">
                <el-input
                  v-model="registerForm.username"
                  placeholder="请设置用户名"
                  prefix-icon="User"
                />
              </el-form-item>

              <el-form-item prop="phone">
                <el-input
                  v-model="registerForm.phone"
                  placeholder="请输入11位手机号"
                  prefix-icon="Iphone"
                />
              </el-form-item>

              <el-form-item prop="password">
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="请设置密码 (至少8位，含大小写数字)"
                  show-password
                  prefix-icon="Lock"
                />
              </el-form-item>

              <el-form-item prop="confirmPassword">
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="确认密码"
                  show-password
                  prefix-icon="Lock"
                />
              </el-form-item>

              <el-form-item prop="agreed">
                <el-checkbox v-model="registerForm.agreed">
                  我已阅读并同意
                  <a class="link-text" href="#" @click.prevent="openPolicy('terms')">服务条款</a>
                  和
                  <a class="link-text" href="#" @click.prevent="openPolicy('privacy')">隐私政策</a>
                </el-checkbox>
              </el-form-item>

              <el-button :loading="loadingRegister" type="success" class="submit-btn" @click="handleRegister">
                注册
              </el-button>

              <div class="hint">注册成功后可直接使用用户名和密码登录。</div>
            </el-form>
          </el-tab-pane>
        </el-tabs>

        <div class="oauth-row">
          <span>企业单点登录</span>
          <el-button type="info" size="mini" @click="handleSSO">SAML/SSO 登录</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { User, Lock, Iphone } from '@element-plus/icons-vue';
import request from '../api/request';
import { useRouter } from 'vue-router';

const router = useRouter();

const activeTab = ref('login');
const loadingLogin = ref(false);
const loadingRegister = ref(false);

const loginFormRef = ref(null);
const registerFormRef = ref(null);

const loginForm = reactive({ username: '', password: '', remember: true, captcha: '' });
const registerForm = reactive({ username: '', phone: '', password: '', confirmPassword: '', agreed: false });

const captchaImage = ref('');
const captchaToken = ref('');
const loginFailCount = ref(0);
const isLocked = ref(false);
const lockEndTime = ref(0);

const encrypt = (text) => {
  try {
    return btoa(unescape(encodeURIComponent(text)));
  } catch {
    return text;
  }
};

const decrypt = (text) => {
  try {
    return decodeURIComponent(escape(atob(text)));
  } catch {
    return text;
  }
};

const setCookie = (name, value, days = 7) => {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; expires=${expires}; secure; samesite=strict`;
};

const getCookie = (name) => {
  return document.cookie.split('; ').reduce((r, v) => {
    const parts = v.split('=');
    return parts[0] === name ? decodeURIComponent(parts[1]) : r;
  }, '');
};

const removeCookie = (name) => {
  document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT;`;
};

const refreshCaptcha = async () => {
  try {
    const res = await request.get('/user/captcha/');
    captchaImage.value = res.data?.image || '';
    captchaToken.value = res.data?.token || '';
    loginForm.captcha = '';
  } catch (error) {
    ElMessage.error('验证码加载失败，请稍后再试');
  }
};

const validPhone = (phone) => /^1[3-9]\d{9}$/.test(phone);

const openPolicy = (type) => {
  const url = type === 'terms' ? '/terms' : '/privacy';
  window.open(url, '_blank');
};

const validatePhone = (rule, value, callback) => {
  if (!value) return callback(new Error('手机号不能为空'));
  if (!validPhone(value)) return callback(new Error('请输入正确的11位手机号'));
  callback();
};

const validatePassword = (rule, value, callback) => {
  if (!value) return callback(new Error('密码不能为空'));
  if (value.length < 8) return callback(new Error('密码至少8位'));
  const strong = /(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value);
  if (!strong) return callback(new Error('密码需包含大小写字母和数字'));
  callback();
};

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) return callback(new Error('两次输入密码不一致'));
  callback();
};

const validateAgreement = (rule, value, callback) => {
  if (!value) return callback(new Error('请同意服务条款与隐私政策'));
  callback();
};

const loginRules = reactive({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captcha: [{ required: true, message: '请输入图形验证码', trigger: 'blur' }]
});

const registerRules = reactive({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }, { min: 2, max: 20, message: '长度2到20个字符', trigger: 'blur' }],
  phone: [{ required: true, validator: validatePhone, trigger: 'blur' }],
  password: [{ required: true, validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }],
  agreed: [{ required: true, validator: validateAgreement, trigger: 'change' }]
});

const startLock = () => {
  isLocked.value = true;
  lockEndTime.value = Date.now() + 60_000;
  ElMessage.error('错误次数过多，已锁定 60 秒');
  const timer = setInterval(() => {
    if (Date.now() >= lockEndTime.value) {
      isLocked.value = false;
      loginFailCount.value = 0;
      clearInterval(timer);
      ElMessage.info('登录已解锁，请重试');
    }
  }, 1000);
};

const handleLogin = async () => {
  if (isLocked.value) {
    const left = Math.max(0, Math.ceil((lockEndTime.value - Date.now()) / 1000));
    ElMessage.warning(`登录被暂时锁定，还剩 ${left} 秒`);
    return;
  }

  if (!loginFormRef.value) return;
  const valid = await loginFormRef.value.validate().catch(() => false);
  if (!valid) return;

  loadingLogin.value = true;
  try {
    const res = await request.post('/user/login/', {
      username: loginForm.username,
      password: loginForm.password,
      captcha: loginForm.captcha,
      captcha_token: captchaToken.value
    });

    const token = res.data?.token;
    if (!token) throw new Error('服务端未返回令牌');

    const userInfo = res.data?.user_info || {};
    localStorage.setItem('token', token);
    localStorage.setItem('userInfo', JSON.stringify(userInfo));

    if (loginForm.remember) {
      setCookie('rememberedUser', encrypt(loginForm.username), 7);
    } else {
      removeCookie('rememberedUser');
    }

    loginFailCount.value = 0;
    ElMessage.success('登录成功，进入系统...');
    await router.push('/index');
  } catch (error) {
    loginFailCount.value += 1;
    if (loginFailCount.value >= 5) startLock();
    const msg = error?.response?.data?.msg || error.message || '登录失败，请检查用户名密码';
    ElMessage.error(msg);
    refreshCaptcha();
  } finally {
    loadingLogin.value = false;
  }
};

const handleRegister = async () => {
  if (!registerFormRef.value) return;
  const valid = await registerFormRef.value.validate().catch(() => false);
  if (!valid) return;

  loadingRegister.value = true;
  try {
    await request.post('/user/register/', {
      username: registerForm.username,
      phone: registerForm.phone,
      password: registerForm.password
    });

    ElMessage.success('注册成功，请登录系统');
    registerFormRef.value.resetFields();
    activeTab.value = 'login';
  } catch (error) {
    const msg = error?.response?.data?.msg || error.message || '注册失败，请重试';
    ElMessage.error(msg);
  } finally {
    loadingRegister.value = false;
  }
};

const onForgotPassword = () => {
  ElMessage.info('请联系管理员重置密码或通过企业邮箱找回。');
};

const handleSSO = () => {
  router.push('/sso-login');
};

onMounted(() => {
  const remembered = getCookie('rememberedUser');
  if (remembered) {
    loginForm.username = decrypt(remembered);
    loginForm.remember = true;
  }
  refreshCaptcha();
});
</script>

<style scoped>
.auth-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f6f8fb;
}

.auth-card-wrapper {
  width: 100%;
  max-width: 480px;
  padding: 14px;
}

.auth-card {
  border-radius: 14px;
  border: 1px solid #e6eaf0;
  background: #ffffff;
  box-shadow: 0 8px 20px rgba(31, 45, 71, 0.08);
  overflow: hidden;
}

.brand-area {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
  padding: 12px 10px;
}

.brand-logo {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #1b7cff;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.brand-area h1 {
  margin: 0;
  font-size: 20px;
  color: #1b3f72;
}

.brand-area p {
  margin: 4px 0 0;
  color: #54607a;
  font-size: 13px;
}

.auth-tabs {
  margin-top: 8px;
}

.quick-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 4px 0 12px;
}

.link-text {
  color: #409eff;
  cursor: pointer;
  font-size: 13px;
}

.captcha-item {
  display: grid;
  align-items: center;
  grid-template-columns: 1fr auto;
  column-gap: 10px;
}

.captcha-img {
  max-width: 120px;
  height: 34px;
  cursor: pointer;
  border: 1px solid #d8e5f0;
  border-radius: 8px;
}

.submit-btn {
  width: 100%;
  height: 48px;
  margin-top: 6px;
  border-radius: 8px;
  font-size: 16px;
  letter-spacing: 0.8px;
}

.hint {
  margin-top: 10px;
  font-size: 12px;
  color: #7a8299;
}

.oauth-row {
  margin-top: 20px;
  padding: 12px 0 8px;
  border-top: 1px solid #e7ecf4;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #8f9caf;
  font-size: 12px;
}

:deep(.el-form-item) {
  margin-bottom: 12px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  border: 1px solid #dce5f2;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.12);
}

:deep(.el-tabs__nav) {
  background: #f7fafd;
  border-bottom: 1px solid #d8e6f7;
  border-radius: 8px 8px 0 0;
}

:deep(.el-tabs__item.is-active) {
  color: #0058d9;
  font-weight: 700;
}

:deep(.el-tabs__item) {
  flex: 1;
  text-align: center;
}
</style>