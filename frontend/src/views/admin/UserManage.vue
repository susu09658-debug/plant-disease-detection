<template>
  <div class="user-manage-page">
    <h2 class="page-title">🔧 用户管理</h2>

    <el-card shadow="never" class="search-card">
      <el-row :gutter="12" align="middle">
        <el-col :span="8">
          <el-input
            v-model="keyword"
            placeholder="按用户ID或昵称搜索"
            clearable
            prefix-icon="Search"
            @keyup.enter="loadData"
            @clear="loadData"
          />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadData">搜索</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="list" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="用户ID" min-width="120" />
        <el-table-column prop="nickname" label="昵称" min-width="120" />
        <el-table-column prop="phone" label="手机号" min-width="120" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_admin === 1 ? 'danger' : 'info'">
              {{ row.is_admin === 1 ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active === 1 ? 'success' : 'warning'">
              {{ row.is_active === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="注册时间" min-width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              link
              :type="row.is_active === 1 ? 'warning' : 'success'"
              @click="toggleActive(row)"
            >
              {{ row.is_active === 1 ? '禁用' : '启用' }}
            </el-button>
            <el-button
              link
              type="primary"
              @click="toggleAdmin(row)"
            >
              {{ row.is_admin === 1 ? '取消管理员' : '设为管理员' }}
            </el-button>
            <el-button link type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        class="pagination"
        @change="loadData"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getUserList, updateUser, deleteUser } from '../../api/admin';

const loading = ref(false);
const list = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const keyword = ref('');

const loadData = async () => {
    loading.value = true;
    try {
        const res = await getUserList({ page: page.value, page_size: pageSize.value, keyword: keyword.value });
        list.value = res.data.list;
        total.value = res.data.total;
    } finally {
        loading.value = false;
    }
};

const toggleActive = async (row) => {
    await updateUser(row.id, { is_active: row.is_active === 1 ? 0 : 1 });
    ElMessage.success('操作成功');
    loadData();
};

const toggleAdmin = async (row) => {
    await updateUser(row.id, { is_admin: row.is_admin === 1 ? 0 : 1 });
    ElMessage.success('操作成功');
    loadData();
};

const handleDelete = async (id) => {
    await ElMessageBox.confirm('确认删除该用户？此操作不可恢复', '警告', { type: 'warning' });
    await deleteUser(id);
    ElMessage.success('删除成功');
    loadData();
};

onMounted(loadData);
</script>

<style scoped>
.user-manage-page {
    max-width: 1100px;
}

.page-title {
    margin: 0 0 20px;
    font-size: 20px;
    color: #303133;
}

.search-card {
    margin-bottom: 16px;
}

.pagination {
    margin-top: 16px;
    justify-content: flex-end;
}
</style>
