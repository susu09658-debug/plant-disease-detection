<template>
  <div class="knowledge-page">
    <h2 class="page-title">📚 病害知识库</h2>

    <!-- 搜索栏 -->
    <el-card shadow="never" class="search-card">
      <el-row :gutter="12" align="middle">
        <el-col :span="7">
          <el-input
            v-model="plantKeyword"
            placeholder="按植物名称搜索"
            clearable
            prefix-icon="Search"
          />
        </el-col>
        <el-col :span="7">
          <el-input
            v-model="diseaseKeyword"
            placeholder="按病害名称搜索"
            clearable
            prefix-icon="Search"
          />
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="doSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 卡片列表 -->
    <div v-loading="loading">
      <el-row :gutter="16" v-if="list.length">
        <el-col v-for="item in list" :key="item.id" :span="8" class="card-col">
          <el-card
            class="knowledge-card"
            shadow="hover"
            @click="showDetail(item)"
          >
            <div class="k-header">
              <el-tag type="success" class="plant-tag">{{ item.plant_name }}</el-tag>
              <el-tag type="danger">{{ item.disease_name }}</el-tag>
              <el-tag
                v-if="item.severity"
                :type="severityType(item.severity)"
                size="small"
                style="margin-left: auto;"
              >
                {{ severityLabel(item.severity) }}
              </el-tag>
            </div>
            <p class="symptom-preview">{{ item.symptom?.slice(0, 80) }}...</p>
            <div class="k-footer">
              <span class="view-more">点击查看详情 →</span>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <el-empty v-else description="暂无知识库数据" />
    </div>

    <el-pagination
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      class="pagination"
      @change="loadData"
    />

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" :title="`${current?.plant_name} - ${current?.disease_name}`" width="600px">
      <div v-if="current">
        <img v-if="current.image_url" :src="current.image_url" class="detail-img" />
        <el-descriptions :column="1" border>
          <el-descriptions-item label="病害症状">{{ current.symptom }}</el-descriptions-item>
          <el-descriptions-item label="防治方法">{{ current.treatment }}</el-descriptions-item>
          <el-descriptions-item label="严重等级">
            <el-rate :model-value="current.severity" disabled />
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getList } from '../api/knowledge';

const loading = ref(false);
const list = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(9);
const plantKeyword = ref('');
const diseaseKeyword = ref('');
const detailVisible = ref(false);
const current = ref(null);

const severityLabel = (s) => ['', '轻微', '较轻', '中等', '较重', '严重'][s] || '';
const severityType = (s) => s <= 2 ? 'success' : s === 3 ? 'warning' : 'danger';

const loadData = async () => {
    loading.value = true;
    try {
        const res = await getList({
            page: page.value,
            page_size: pageSize.value,
            plant_name: plantKeyword.value,
            disease_name: diseaseKeyword.value,
        });
        list.value = res.data.list;
        total.value = res.data.total;
    } finally {
        loading.value = false;
    }
};

const doSearch = () => {
    page.value = 1;
    loadData();
};

const resetSearch = () => {
    plantKeyword.value = '';
    diseaseKeyword.value = '';
    page.value = 1;
    loadData();
};

const showDetail = (item) => {
    current.value = item;
    detailVisible.value = true;
};

onMounted(loadData);
</script>

<style scoped>
.knowledge-page {
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

.card-col {
    margin-bottom: 16px;
}

.knowledge-card {
    cursor: pointer;
    transition: transform 0.2s;
    height: 180px;
    display: flex;
    flex-direction: column;
}

.knowledge-card:hover {
    transform: translateY(-3px);
}

.k-header {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 10px;
}

.symptom-preview {
    font-size: 13px;
    color: #606266;
    line-height: 1.6;
    flex: 1;
    overflow: hidden;
}

.k-footer {
    margin-top: auto;
    text-align: right;
}

.view-more {
    font-size: 12px;
    color: #409eff;
}

.pagination {
    margin-top: 20px;
    justify-content: center;
}

.detail-img {
    width: 100%;
    max-height: 200px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 16px;
}
</style>
