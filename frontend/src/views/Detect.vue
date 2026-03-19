<template>
  <div class="detect-page">
    <h2 class="page-title">🔍 病害检测</h2>

    <el-card shadow="never" class="upload-card">
      <template #header><span class="card-title">上传植物图片</span></template>

      <!-- 模型选择 -->
      <div class="model-select-row">
        <span class="model-label">检测模型：</span>
        <el-select
          v-model="selectedModel"
          placeholder="默认模型"
          size="default"
          style="width: 220px;"
          :disabled="detecting"
        >
          <el-option
            v-for="m in modelList"
            :key="m.key"
            :label="m.name + (m.size_mb ? ` (${m.size_mb} MB)` : '')"
            :value="m.key"
          />
        </el-select>
        <el-button :icon="Refresh" circle size="small" @click="loadModels" title="刷新模型列表" />
      </div>

      <el-upload
        ref="uploadRef"
        class="upload-area"
        drag
        action="#"
        :http-request="handleUpload"
        :before-upload="beforeUpload"
        :show-file-list="false"
        accept="image/jpeg,image/png,image/jpg"
        :disabled="detecting"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽图片至此处，或 <em>点击选择文件</em>
        </div>
        <template #tip>
          <div class="upload-tip">支持 JPG / PNG 格式，单文件最大 10MB</div>
        </template>
      </el-upload>
    </el-card>

    <!-- 检测中 loading -->
    <el-card v-if="detecting" shadow="never" class="result-card">
      <div class="detecting-box">
        <el-icon class="is-loading spin-icon"><Loading /></el-icon>
        <p>正在进行 AI 病害检测，请稍候...</p>
      </div>
    </el-card>

    <!-- 检测结果 -->
    <el-card v-if="result" shadow="never" class="result-card">
      <template #header><span class="card-title">检测结果</span></template>

      <el-row :gutter="24">
        <el-col :span="12">
          <div class="img-label">原始图片</div>
          <img :src="result.original_img_url" class="result-img" alt="原始图片" />
        </el-col>
        <el-col :span="12">
          <div class="img-label">检测标注图</div>
          <img :src="result.result_img_url" class="result-img" alt="标注图" />
        </el-col>
      </el-row>

      <el-divider />

      <el-descriptions :column="2" border>
        <el-descriptions-item label="病害名称">
          <el-tag type="danger" size="large">{{ result.disease_name }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="植物名称">
          {{ result.plant_name || '未识别' }}
        </el-descriptions-item>
        <el-descriptions-item label="置信度">
          <el-progress
            :percentage="Math.round((result.confidence || 0) * 100)"
            :color="getConfColor(result.confidence)"
            style="width: 200px;"
          />
        </el-descriptions-item>
        <el-descriptions-item label="检测时间">
          {{ result.detect_time }}
        </el-descriptions-item>
        <el-descriptions-item v-if="result.model_used" label="使用模型">
          <el-tag size="small" type="info">{{ result.model_used }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 检测框详情 -->
      <div v-if="result.bbox_data && result.bbox_data.length > 1" class="bbox-section">
        <el-divider content-position="left">检测目标列表</el-divider>
        <el-table :data="result.bbox_data" size="small" border stripe>
          <el-table-column prop="label" label="病害类型" width="160" />
          <el-table-column label="置信度" width="200">
            <template #default="{ row }">
              <el-progress
                :percentage="Math.round((row.confidence || 0) * 100)"
                :stroke-width="10"
                :color="getConfColor(row.confidence)"
              />
            </template>
          </el-table-column>
          <el-table-column label="位置坐标">
            <template #default="{ row }">
              [{{ Math.round(row.x1) }}, {{ Math.round(row.y1) }}] →
              [{{ Math.round(row.x2) }}, {{ Math.round(row.y2) }}]
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="action-btns">
        <el-button type="primary" @click="$router.push('/app/history')">
          查看历史记录
        </el-button>
        <el-button type="success" @click="$router.push('/app/knowledge')">
          查看防治知识
        </el-button>
        <el-button @click="resetResult">重新检测</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Refresh } from '@element-plus/icons-vue';
import { uploadDetect, getDetectModels } from '../api/detect';

const DEFAULT_MODEL = { key: 'best', name: 'best.pt', size_mb: 0 };

const detecting = ref(false);
const result = ref(null);
const uploadRef = ref(null);
const modelList = ref([]);
const selectedModel = ref('');

const loadModels = async () => {
    try {
        const res = await getDetectModels();
        modelList.value = res.data || [];
        if (modelList.value.length > 0 && !selectedModel.value) {
            selectedModel.value = modelList.value[0].key;
        }
    } catch (e) {
        modelList.value = [DEFAULT_MODEL];
        selectedModel.value = DEFAULT_MODEL.key;
    }
};

onMounted(() => {
    loadModels();
});

const beforeUpload = (file) => {
    const isImage = ['image/jpeg', 'image/png', 'image/jpg'].includes(file.type);
    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isImage) {
        ElMessage.error('只能上传 JPG/PNG 格式的图片');
        return false;
    }
    if (!isLt10M) {
        ElMessage.error('图片大小不能超过 10MB');
        return false;
    }
    return true;
};

const handleUpload = async ({ file }) => {
    detecting.value = true;
    result.value = null;
    try {
        const formData = new FormData();
        formData.append('image', file);
        if (selectedModel.value) {
            formData.append('model_key', selectedModel.value);
        }
        const res = await uploadDetect(formData);
        result.value = res.data;
        ElMessage.success('检测完成！');
    } catch (e) {
        ElMessage.error('检测失败，请重试');
    } finally {
        detecting.value = false;
    }
};

const resetResult = () => {
    result.value = null;
};

const getConfColor = (conf) => {
    if (!conf) return '#f56c6c';
    if (conf >= 0.9) return '#67c23a';
    if (conf >= 0.7) return '#e6a23c';
    return '#f56c6c';
};
</script>

<style scoped>
.detect-page {
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

.model-select-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}

.model-label {
    font-size: 14px;
    color: #606266;
    white-space: nowrap;
}

.upload-area {
    width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
    width: 100%;
    height: 180px;
}

.upload-tip {
    color: #909399;
    font-size: 12px;
    margin-top: 6px;
}

.result-card {
    margin-top: 20px;
}

.detecting-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px;
    color: #409eff;
    font-size: 15px;
    gap: 14px;
}

.spin-icon {
    font-size: 40px;
}

.img-label {
    font-size: 13px;
    color: #606266;
    margin-bottom: 8px;
    font-weight: 600;
}

.result-img {
    width: 100%;
    max-height: 300px;
    object-fit: contain;
    border-radius: 8px;
    border: 1px solid #ebeef5;
}

.action-btns {
    margin-top: 20px;
    display: flex;
    gap: 12px;
}

.bbox-section {
    margin-top: 10px;
}
</style>
