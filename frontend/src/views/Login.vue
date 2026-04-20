<template>
  <div class="auth-page">
    <div class="auth-card-wrapper">
      <el-card class="auth-card" shadow="hover">
        <div class="brand-area">
          <div class="brand-logo">🌿</div>
          <div>
            <h1>植物病害智能检测系统</h1>
            <p>AI 驱动 | 精准检测 | 实时预警</p>
          </div>
        </div>

        <el-tabs v-model="activeTab" class="auth-tabs" type="border-card">
          <el-tab-pane label="登录" name="login">
            <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-width="0" size="large">
              <el-form-item prop="username">
                <el-input
                  v-model="loginForm.username"
                  placeholder="请输入用户ID"
                  prefix-icon="User"
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

              <div class="quick-row">
                <el-checkbox v-model="loginForm.remember">7天内自动登录</el-checkbox>
                <el-button type="text" class="forgot-link" @click="showForgotDialog = true">忘记密码？</el-button>
              </div>

              <el-button :loading="loadingLogin" type="primary" class="submit-btn" @click="handleLogin">
                登 录
              </el-button>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="注册" name="register">
            <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" label-width="0" size="large">
              <el-form-item prop="username">
                <el-input
                  v-model="registerForm.username"
                  placeholder="请设置用户ID（2-20位字母或数字，用于登录）"
                  prefix-icon="User"
                />
              </el-form-item>

              <el-form-item prop="nickname">
                <el-input
                  v-model="registerForm.nickname"
                  placeholder="请设置昵称（最多20个字符，用于系统展示）"
                  prefix-icon="UserFilled"
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
                  placeholder="请设置密码（至少8位，含大小写数字）"
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
                  我已阅读并同意服务条款和隐私政策
                </el-checkbox>
              </el-form-item>

              <el-button :loading="loadingRegister" type="success" class="submit-btn" @click="handleRegister">
                注 册
              </el-button>

              <div class="hint">注册成功后可直接使用用户ID和密码登录。</div>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>

    <!-- 忘记密码弹窗 -->
    <el-dialog v-model="showForgotDialog" title="忘记密码" width="420px" :close-on-click-modal="false">
      <el-form ref="forgotFormRef" :model="forgotForm" :rules="forgotRules" label-width="0" size="large">
        <el-form-item prop="username">
          <el-input v-model="forgotForm.username" placeholder="请输入用户ID" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="phone">
          <el-input v-model="forgotForm.phone" placeholder="请输入注册时的手机号" prefix-icon="Iphone" />
        </el-form-item>
        <el-form-item prop="newPassword">
          <el-input v-model="forgotForm.newPassword" type="password" placeholder="请设置新密码（至少8位）" show-password prefix-icon="Lock" />
        </el-form-item>
        <el-form-item prop="confirmNewPassword">
          <el-input v-model="forgotForm.confirmNewPassword" type="password" placeholder="确认新密码" show-password prefix-icon="Lock" />
        </el-form-item>
        <el-form-item prop="captcha" class="captcha-item">
          <el-input v-model="forgotForm.captcha" placeholder="请输入图形验证码" prefix-icon="Picture" />
          <img class="captcha-img" :src="forgotCaptchaImage" @click="refreshForgotCaptcha" alt="验证码" title="点击刷新" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showForgotDialog = false">取消</el-button>
        <el-button type="primary" :loading="loadingReset" @click="handleResetPassword">重置密码</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
import { getCaptcha, register as apiRegister, resetPassword } from '../api/user';

const router = useRouter();
const userStore = useUserStore();

const activeTab = ref('login');
const loadingLogin = ref(false);
const loadingRegister = ref(false);

const loginFormRef = ref(null);
const registerFormRef = ref(null);

const loginForm = reactive({ username: '', password: '', remember: true, captcha: '' });
const registerForm = reactive({ username: '', nickname: '', phone: '', password: '', confirmPassword: '', agreed: false });

const captchaImage = ref('');
const captchaToken = ref('');
const loginFailCount = ref(0);
const isLocked = ref(false);
const lockEndTime = ref(0);

const showForgotDialog = ref(false);
const loadingReset = ref(false);
const forgotFormRef = ref(null);
const forgotForm = reactive({ username: '', phone: '', newPassword: '', confirmNewPassword: '', captcha: '' });
const forgotCaptchaImage = ref('');
const forgotCaptchaToken = ref('');

const encrypt = (text) => {
    try { return btoa(unescape(encodeURIComponent(text))); } catch { return text; }
};
const decrypt = (text) => {
    try { return decodeURIComponent(escape(atob(text))); } catch { return text; }
};
const setCookie = (name, value, days = 7) => {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; path=/; expires=${expires}; samesite=strict`;
};
const getCookie = (name) => document.cookie.split('; ').reduce((r, v) => {
    const parts = v.split('=');
    return parts[0] === name ? decodeURIComponent(parts[1]) : r;
}, '');
const removeCookie = (name) => {
    document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT;`;
};

const refreshCaptcha = async () => {
    try {
        const res = await getCaptcha();
        captchaImage.value = res?.data?.image || '';
        captchaToken.value = res?.data?.token || '';
        loginForm.captcha = '';
    } catch {
        ElMessage.error('验证码加载失败，请稍后再试');
    }
};

const validatePhone = (rule, value, callback) => {
    if (!value) return callback(new Error('手机号不能为空'));
    if (!/^1[3-9]\d{9}$/.test(value)) return callback(new Error('请输入正确的11位手机号'));
    callback();
};
const validatePassword = (rule, value, callback) => {
    if (!value) return callback(new Error('密码不能为空'));
    if (value.length < 8) return callback(new Error('密码至少8位'));
    if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) return callback(new Error('密码需包含大小写字母和数字'));
    callback();
};
const validateConfirmPassword = (rule, value, callback) => {
    if (value !== registerForm.password) return callback(new Error('两次输入密码不一致'));
    callback();
};
const validateForgotConfirmPassword = (rule, value, callback) => {
    if (value !== forgotForm.newPassword) return callback(new Error('两次输入密码不一致'));
    callback();
};
const validateAgreement = (rule, value, callback) => {
    if (!value) return callback(new Error('请同意服务条款与隐私政策'));
    callback();
};

const loginRules = reactive({
    username: [{ required: true, message: '请输入用户ID', trigger: 'blur' }],
    password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
    captcha: [{ required: true, message: '请输入图形验证码', trigger: 'blur' }],
});

const registerRules = reactive({
    username: [
        { required: true, message: '请输入用户ID', trigger: 'blur' },
        { min: 2, max: 20, message: '长度2到20个字符', trigger: 'blur' },
        { pattern: /^[a-zA-Z0-9]+$/, message: '用户ID只能包含字母和数字', trigger: 'blur' }
    ],
    nickname: [
        // 新增这行必填校验
        { required: true, message: '请输入昵称', trigger: 'blur' },
        { max: 20, message: '昵称最多20个字符', trigger: 'blur' },
    ],
    phone: [{ required: true, validator: validatePhone, trigger: 'blur' }],
    password: [{ required: true, validator: validatePassword, trigger: 'blur' }],
    confirmPassword: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }],
    agreed: [{ required: true, validator: validateAgreement, trigger: 'change' }],
});

const forgotRules = reactive({
    username: [{ required: true, message: '请输入用户ID', trigger: 'blur' }],
    phone: [{ required: true, validator: validatePhone, trigger: 'blur' }],
    newPassword: [{ required: true, validator: validatePassword, trigger: 'blur' }],
    confirmNewPassword: [{ required: true, validator: validateForgotConfirmPassword, trigger: 'blur' }],
    captcha: [{ required: true, message: '请输入图形验证码', trigger: 'blur' }],
});

const refreshForgotCaptcha = async () => {
    try {
        const res = await getCaptcha();
        forgotCaptchaImage.value = res?.data?.image || '';
        forgotCaptchaToken.value = res?.data?.token || '';
        forgotForm.captcha = '';
    } catch {
        ElMessage.error('验证码加载失败');
    }
};

const handleResetPassword = async () => {
    const valid = await forgotFormRef.value?.validate().catch(() => false);
    if (!valid) return;

    loadingReset.value = true;
    try {
        await resetPassword({
            username: forgotForm.username,
            phone: forgotForm.phone,
            new_password: forgotForm.newPassword,
            captcha: forgotForm.captcha,
            captcha_token: forgotCaptchaToken.value,
        });
        ElMessage.success('密码重置成功，请使用新密码登录');
        showForgotDialog.value = false;
        forgotFormRef.value?.resetFields();
    } catch (error) {
        const msg = error?.response?.data?.msg || error.message || '密码重置失败，请检查输入信息或稍后重试';
        ElMessage.error(msg);
        refreshForgotCaptcha();
    } finally {
        loadingReset.value = false;
    }
};

watch(showForgotDialog, (val) => {
    if (val) refreshForgotCaptcha();
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

    const valid = await loginFormRef.value?.validate().catch(() => false);
    if (!valid) return;

    loadingLogin.value = true;
    try {
        await userStore.login({
            username: loginForm.username,
            password: loginForm.password,
            captcha: loginForm.captcha,
            captcha_token: captchaToken.value,
        });

        if (loginForm.remember) {
            setCookie('rememberedUser', encrypt(loginForm.username), 7);
        } else {
            removeCookie('rememberedUser');
        }

        loginFailCount.value = 0;
        ElMessage.success('登录成功，正在跳转...');
        router.push({ name: 'dashboard' });
    } catch (error) {
        loginFailCount.value += 1;
        if (loginFailCount.value >= 5) startLock();
        const msg = error?.response?.data?.msg || error.message || '登录失败，请检查用户ID和密码';
        ElMessage.error(msg);
        refreshCaptcha();
    } finally {
        loadingLogin.value = false;
    }
};

const handleRegister = async () => {
    const valid = await registerFormRef.value?.validate().catch(() => false);
    if (!valid) return;

    loadingRegister.value = true;
    try {
        await apiRegister({
            username: registerForm.username,
            nickname: registerForm.nickname,
            phone: registerForm.phone,
            password: registerForm.password,
        });
        ElMessage.success('注册成功，请登录系统');
        registerFormRef.value?.resetFields();
        activeTab.value = 'login';
    } catch (error) {
        const msg = error?.response?.data?.msg || error.message || '注册失败，请重试';
        ElMessage.error(msg);
    } finally {
        loadingRegister.value = false;
    }
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
    background: #b7bdbe;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
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
    margin: 4px 0 12px;
}

.forgot-link {
    margin-left: auto;
    font-size: 13px;
    padding: 0;
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

:deep(.el-form-item) {
    margin-bottom: 24px; /* 这里从 12px 修改为了 24px，给表单错误提示文字留出足够空间 */
}

:deep(.el-input__wrapper) {
    border-radius: 8px;
    border: 1px solid #dce5f2;
}

:deep(.el-tabs__nav) {
    background: #f7fafd;
    border-bottom: 1px solid #d8e6f7;
    border-radius: 8px 8px 0 0;
}

:deep(.el-tabs__item.is-active) {
    color: #f6fafb;
    font-weight: 700;
}

:deep(.el-tabs__item) {
    flex: 1;
    text-align: center;
}
</style>