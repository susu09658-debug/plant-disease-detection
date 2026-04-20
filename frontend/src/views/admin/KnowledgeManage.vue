<template>
  <div class="km-page">
    <h2 class="page-title">📝 知识库管理</h2>

    <el-card shadow="never" class="search-card">
      <el-row :gutter="12" align="middle">
        <el-col :span="7">
          <el-input v-model="keyword" placeholder="搜索病害/植物名称" clearable @keyup.enter="loadData" />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadData">搜索</el-button>
        </el-col>
        <el-col :span="13" style="text-align: right;">
          <el-button type="success" @click="openDialog(null)">+ 新增知识</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="list" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="缩略图" width="90">
          <template #default="{ row }">
            <el-image
              v-if="row.image_url"
              :src="row.image_url"
              :preview-src-list="[row.image_url]"
              fit="cover"
              style="width: 50px; height: 50px; border-radius: 6px;"
              preview-teleported
            />
            <span v-else style="color: #909399; font-size: 12px;">暂无图片</span>
          </template>
        </el-table-column>
        <el-table-column prop="plant_name" label="植物名称" width="110" />
        <el-table-column prop="disease_name" label="病害名称" min-width="130" />
        <el-table-column label="严重等级" width="100">
          <template #default="{ row }">
            <el-rate :model-value="row.severity" disabled />
          </template>
        </el-table-column>
        <el-table-column prop="symptom" label="症状摘要" min-width="180" show-overflow-tooltip />
        <el-table-column prop="create_time" label="创建时间" width="160" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
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

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑知识' : '新增知识'"
      width="600px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="植物名称" prop="plant_name">
          <el-input v-model="form.plant_name" />
        </el-form-item>
        <el-form-item label="病害名称" prop="disease_name">
          <el-input v-model="form.disease_name" />
        </el-form-item>
        <el-form-item label="严重等级" prop="severity">
          <el-rate v-model="form.severity" />
        </el-form-item>
        <el-form-item label="病害症状" prop="symptom">
          <el-input v-model="form.symptom" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="防治方法" prop="treatment">
          <el-input v-model="form.treatment" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="参考图片" prop="image_url">
          <el-upload
            class="knowledge-uploader"
            action="/api/knowledge/upload/image/"  :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :before-upload="beforeImageUpload"
            accept="image/*"
          >
            <img v-if="form.image_url" :src="form.image_url" class="uploaded-image" />
            <div v-else class="upload-placeholder">
              <el-icon class="upload-icon"><Plus /></el-icon>
              <span>点击上传图片</span>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getList, createKnowledge, updateKnowledge, deleteKnowledge } from '../../api/knowledge';
import { Plus } from '@element-plus/icons-vue';

const loading = ref(false);
const saving = ref(false);
const list = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const keyword = ref('');
const dialogVisible = ref(false);
const editingId = ref(null);
const formRef = ref(null);

const form = reactive({
    plant_name: '',
    disease_name: '',
    severity: 1,
    symptom: '',
    treatment: '',
    image_url: '',
});

const rules = {
    plant_name: [{ required: true, message: '请输入植物名称', trigger: 'blur' }],
    disease_name: [{ required: true, message: '请输入病害名称', trigger: 'blur' }],
    symptom: [{ required: true, message: '请输入病害症状', trigger: 'blur' }],
    treatment: [{ required: true, message: '请输入防治方法', trigger: 'blur' }],
};

const loadData = async () => {
    loading.value = true;
    try {
        const res = await getList({ page: page.value, page_size: pageSize.value, keyword: keyword.value });
        list.value = res.data.list;
        total.value = res.data.total;
    } finally {
        loading.value = false;
    }
};

const openDialog = (row) => {
    if (row) {
        editingId.value = row.id;
        Object.assign(form, {
            plant_name: row.plant_name,
            disease_name: row.disease_name,
            severity: row.severity || 1,
            symptom: row.symptom,
            treatment: row.treatment,
            image_url: row.image_url || '',
        });
    } else {
        editingId.value = null;
        Object.assign(form, { plant_name: '', disease_name: '', severity: 1, symptom: '', treatment: '', image_url: '' });
    }
    dialogVisible.value = true;
};

const save = async () => {
    const valid = await formRef.value?.validate().catch(() => false);
    if (!valid) return;
    saving.value = true;
    try {
        if (editingId.value) {
            await updateKnowledge(editingId.value, { ...form });
        } else {
            await createKnowledge({ ...form });
        }
        ElMessage.success(editingId.value ? '编辑成功' : '新增成功');
        dialogVisible.value = false;
        loadData();
    } finally {
        saving.value = false;
    }
};

const handleDelete = async (id) => {
    await ElMessageBox.confirm('确认删除该知识条目？', '提示', { type: 'warning' });
    await deleteKnowledge(id);
    ElMessage.success('删除成功');
    loadData();
};

onMounted(loadData);

const uploadHeaders = reactive({
    Authorization: `Bearer ${localStorage.getItem('token') || ''}`
});

// 2. 上传前的校验（限制格式和大小，比如 5MB）
const beforeImageUpload = (file) => {
    const isImage = file.type.startsWith('image/');
    const isLt5M = file.size / 1024 / 1024 < 5;

    if (!isImage) {
        ElMessage.error('上传的必须是图片格式!');
        return false;
    }
    if (!isLt5M) {
        ElMessage.error('图片大小不能超过 5MB!');
        return false;
    }
    return true;
};

// 3. 上传成功后的回调
const handleUploadSuccess = (res, file) => {
    // 假设后端返回的格式是 { code: 200, data: { url: '/media/images/xxx.jpg' } }
    if (res.code === 200) {
        form.image_url = res.data.url;
        ElMessage.success('图片上传成功');
    } else {
        ElMessage.error(res.msg || '上传失败');
    }
};
</script>

<style scoped>
.km-page {
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

.knowledge-uploader {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    width: 178px;
    height: 178px;
    transition: border-color 0.3s;
}

.knowledge-uploader:hover {
    border-color: #409eff;
}

.upload-placeholder {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
    color: #8c939d;
}

.upload-icon {
    font-size: 28px;
    margin-bottom: 8px;
}

.uploaded-image {
    width: 178px;
    height: 178px;
    display: block;
    object-fit: cover;
}
</style>
