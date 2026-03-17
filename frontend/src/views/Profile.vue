<template>
  <div class="profile-page">
    <h2 class="page-title">👤 个人中心</h2>

    <el-row :gutter="20">
      <!-- 基本信息 -->
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span class="card-title">基本信息</span></template>

          <div class="avatar-area">
            <el-avatar :size="72" class="big-avatar">
              {{ userInfo?.username?.charAt(0)?.toUpperCase() || 'U' }}
            </el-avatar>
            <div>
              <div class="username-text">{{ userInfo?.username }}</div>
              <el-tag :type="userInfo?.is_admin === 1 ? 'danger' : 'success'">
                {{ userInfo?.is_admin === 1 ? '管理员' : '普通用户' }}
              </el-tag>
            </div>
          </div>

          <el-form ref="infoFormRef" :model="infoForm" :rules="infoRules" label-width="80px">
            <el-form-item label="用户名">
              <el-input :model-value="userInfo?.username" disabled />
            </el-form-item>
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="infoForm.phone" placeholder="请输入手机号" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="infoForm.email" placeholder="请输入邮箱（选填）" />
            </el-form-item>
            <el-form-item label="注册时间">
              <el-input :model-value="userInfo?.create_time" disabled />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="savingInfo" @click="saveInfo">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 修改密码 -->
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span class="card-title">修改密码</span></template>

          <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="100px">
            <el-form-item label="旧密码" prop="old_password">
              <el-input
                v-model="pwdForm.old_password"
                type="password"
                show-password
                placeholder="请输入当前密码"
              />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input
                v-model="pwdForm.new_password"
                type="password"
                show-password
                placeholder="至少8位，含大小写和数字"
              />
            </el-form-item>
            <el-form-item label="确认新密码" prop="confirm_password">
              <el-input
                v-model="pwdForm.confirm_password"
                type="password"
                show-password
                placeholder="再次输入新密码"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="warning" :loading="savingPwd" @click="savePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useUserStore } from '../store/user';
import { updateProfile, updatePassword } from '../api/user';

const userStore = useUserStore();
const userInfo = computed(() => userStore.userInfo);

const infoFormRef = ref(null);
const pwdFormRef = ref(null);
const savingInfo = ref(false);
const savingPwd = ref(false);

const infoForm = reactive({
    phone: '',
    email: '',
});

const pwdForm = reactive({
    old_password: '',
    new_password: '',
    confirm_password: '',
});

const infoRules = {
    phone: [
        { required: true, message: '手机号不能为空', trigger: 'blur' },
        { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' },
    ],
    email: [
        { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
    ],
};

const pwdRules = {
    old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
    new_password: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 8, message: '密码至少8位', trigger: 'blur' },
    ],
    confirm_password: [
        { required: true, message: '请确认新密码', trigger: 'blur' },
        {
            validator: (rule, value, callback) => {
                if (value !== pwdForm.new_password) callback(new Error('两次密码不一致'));
                else callback();
            },
            trigger: 'blur',
        },
    ],
};

const saveInfo = async () => {
    const valid = await infoFormRef.value?.validate().catch(() => false);
    if (!valid) return;
    savingInfo.value = true;
    try {
        await updateProfile({ phone: infoForm.phone, email: infoForm.email });
        await userStore.fetchProfile();
        ElMessage.success('信息更新成功');
    } finally {
        savingInfo.value = false;
    }
};

const savePassword = async () => {
    const valid = await pwdFormRef.value?.validate().catch(() => false);
    if (!valid) return;
    savingPwd.value = true;
    try {
        await updatePassword({
            old_password: pwdForm.old_password,
            new_password: pwdForm.new_password,
        });
        ElMessage.success('密码修改成功，请重新登录');
        pwdFormRef.value?.resetFields();
    } finally {
        savingPwd.value = false;
    }
};

onMounted(() => {
    if (userInfo.value) {
        infoForm.phone = userInfo.value.phone || '';
        infoForm.email = userInfo.value.email || '';
    }
});
</script>

<style scoped>
.profile-page {
    max-width: 900px;
}

.page-title {
    margin: 0 0 20px;
    font-size: 20px;
    color: #303133;
}

.card-title {
    font-weight: 600;
}

.avatar-area {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 10px;
}

.big-avatar {
    background: #409eff;
    color: #fff;
    font-size: 24px;
    font-weight: 700;
}

.username-text {
    font-size: 18px;
    font-weight: 700;
    color: #303133;
    margin-bottom: 6px;
}
</style>
