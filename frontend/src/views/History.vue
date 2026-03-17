<template>
  <div class="history-page">
    <h2 class="page-title">📋 历史记录</h2>

    <!-- 搜索栏 -->
    <el-card shadow="never" class="search-card">
      <el-row :gutter="12" align="middle">
        <el-col :span="8">
          <el-input
            v-model="keyword"
            placeholder="按病害名称搜索"
            clearable
            prefix-icon="Search"
            @keyup.enter="loadData"
            @clear="loadData"
          />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadData">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-col>
        <el-col :span="12" style="text-align: right;">
          <el-button
            type="danger"
            :disabled="!selectedIds.length"
            @click="handleBatchDelete"
          >
            批量删除 ({{ selectedIds.length }})
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 表格 -->
    <el-card shadow="never" class="table-card">
      <el-table
        v-loading="loading"
        :data="list"
        stripe
        @selection-change="handleSelectionChange"
        style="width: 100%"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column label="缩略图" width="90">
          <template #default="{ row }">
            <el-image
              :src="row.original_img_url"
              :preview-src-list="[row.original_img_url]"
              fit="cover"
              style="width: 60px; height: 60px; border-radius: 6px;"
              preview-teleported
            />
          </template>
        </el-table-column>
        <el-table-column prop="disease_name" label="病害名称" min-width="120">
          <template #default="{ row }">
            <el-tag type="danger">{{ row.disease_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="plant_name" label="植物名称" width="100" />
        <el-table-column prop="confidence" label="置信度" width="120">
          <template #default="{ row }">
            {{ row.confidence ? (row.confidence * 100).toFixed(1) + '%' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="detect_time" label="检测时间" min-width="160" />
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row.id)">详情</el-button>
            <el-button link type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        class="pagination"
        @change="loadData"
      />
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="检测详情" width="700px" destroy-on-close>
      <div v-if="detailData" class="detail-content">
        <el-row :gutter="16">
          <el-col :span="12">
            <div class="img-label">原始图片</div>
            <img :src="detailData.original_img_url" class="detail-img" />
          </el-col>
          <el-col :span="12">
            <div class="img-label">标注图片</div>
            <img :src="detailData.result_img_url" class="detail-img" />
          </el-col>
        </el-row>
        <el-descriptions :column="2" border style="margin-top: 16px;">
          <el-descriptions-item label="病害名称">{{ detailData.disease_name }}</el-descriptions-item>
          <el-descriptions-item label="植物名称">{{ detailData.plant_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="置信度">
            {{ detailData.confidence ? (detailData.confidence * 100).toFixed(2) + '%' : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="检测时间">{{ detailData.detect_time }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getHistory, getDetail, deleteRecord, batchDelete } from '../api/detect';

const loading = ref(false);
const list = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const keyword = ref('');
const selectedIds = ref([]);
const detailVisible = ref(false);
const detailData = ref(null);

const loadData = async () => {
    loading.value = true;
    try {
        const res = await getHistory({ page: page.value, page_size: pageSize.value, keyword: keyword.value });
        list.value = res.data.list;
        total.value = res.data.total;
    } finally {
        loading.value = false;
    }
};

const resetSearch = () => {
    keyword.value = '';
    page.value = 1;
    loadData();
};

const handleSelectionChange = (rows) => {
    selectedIds.value = rows.map(r => r.id);
};

const handleDelete = async (id) => {
    await ElMessageBox.confirm('确认删除该记录？', '提示', { type: 'warning' });
    await deleteRecord(id);
    ElMessage.success('删除成功');
    loadData();
};

const handleBatchDelete = async () => {
    await ElMessageBox.confirm(`确认删除选中的 ${selectedIds.value.length} 条记录？`, '提示', { type: 'warning' });
    await batchDelete(selectedIds.value);
    ElMessage.success('批量删除成功');
    selectedIds.value = [];
    loadData();
};

const viewDetail = async (id) => {
    const res = await getDetail(id);
    detailData.value = res.data;
    detailVisible.value = true;
};

onMounted(loadData);
</script>

<style scoped>
.history-page {
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

.table-card {
    padding-bottom: 8px;
}

.pagination {
    margin-top: 16px;
    justify-content: flex-end;
}

.img-label {
    font-size: 13px;
    color: #606266;
    margin-bottom: 8px;
    font-weight: 600;
}

.detail-img {
    width: 100%;
    max-height: 220px;
    object-fit: contain;
    border-radius: 6px;
    border: 1px solid #ebeef5;
}
</style>
