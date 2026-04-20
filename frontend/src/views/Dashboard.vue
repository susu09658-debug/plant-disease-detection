<template>
  <div class="dashboard">
    <h2 class="page-title">🏠 系统首页</h2>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background:#ecf5ff;">🔍</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">累计检测次数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background:#f0f9eb;">📅</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.today_count }}</div>
            <div class="stat-label">今日检测次数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background:#fdf6ec;">📚</div>
          <div class="stat-info">
            <div class="stat-value">{{ knowledgeTotal }}</div>
            <div class="stat-label">知识库条数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background:#fef0f0;">🌿</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.disease_distribution?.length || 0 }}</div>
            <div class="stat-label">已检测病害种类</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 模型状态 -->
    <el-card shadow="never" class="model-info-card">
      <template #header><span class="card-title">🤖 模型状态</span></template>
      <el-row :gutter="16" align="middle">
        <el-col :span="6">
          <div class="model-stat">
            <span class="model-stat-label">模型版本</span>
            <el-tag type="primary" size="large">{{ modelInfo.model_version || 'YOLOv8' }}</el-tag>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="model-stat">
            <span class="model-stat-label">模型状态</span>
            <el-tag :type="modelInfo.model_loaded ? 'success' : 'warning'" size="large">
              {{ modelInfo.model_loaded ? '已加载' : '使用演示模式' }}
            </el-tag>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="model-stat">
            <span class="model-stat-label">检测类别数</span>
            <span class="model-stat-value">{{ modelInfo.num_classes || 10 }}</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="model-stat">
            <el-button type="primary" plain @click="$router.push('/app/experiment')">
              <el-icon><DataAnalysis /></el-icon>&nbsp;查看实验结果
            </el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="16" class="chart-row">
      <!-- 近7天趋势 -->
      <el-col :span="14">
        <el-card shadow="never">
          <template #header><span class="card-title">📈 近7天检测趋势</span></template>
          <div class="trend-chart">
            <div
              v-for="item in stats.weekly_trend"
              :key="item.date"
              class="trend-bar-wrapper"
            >
              <div class="trend-bar-label">{{ item.count }}</div>
              <div
                class="trend-bar"
                :style="{ height: `${Math.max(item.count * 8, 4)}px` }"
              ></div>
              <div class="trend-date">{{ item.date.slice(5) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 病害分布 -->
      <el-col :span="10">
        <el-card shadow="never">
          <template #header><span class="card-title">🦠 病害检测分布 Top10</span></template>
          <div v-if="stats.disease_distribution?.length">
            <div
              v-for="item in stats.disease_distribution"
              :key="item.disease_name"
              class="disease-row"
            >
              <span class="disease-name">{{ item.disease_name }}</span>
              <el-progress
                :percentage="Math.round((item.count / stats.total) * 100)"
                :stroke-width="10"
                style="flex: 1; margin: 0 10px;"
              />
              <span class="disease-count">{{ item.count }}次</span>
            </div>
          </div>
          <el-empty v-else description="暂无检测数据" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-card shadow="never" class="quick-card">
      <template #header><span class="card-title">⚡ 快捷操作</span></template>
      <div class="quick-btns">
        <el-button type="primary" size="large" @click="$router.push('/app/detect')">
          <el-icon><Search /></el-icon>&nbsp;开始病害检测
        </el-button>
        <el-button type="success" size="large" @click="$router.push('/app/history')">
          <el-icon><List /></el-icon>&nbsp;查看历史记录
        </el-button>
        <el-button type="info" size="large" @click="$router.push('/app/knowledge')">
          <el-icon><Reading /></el-icon>&nbsp;浏览知识库
        </el-button>
      </div>
    </el-card>
  </div>
</template>


<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { getStats } from '../api/detect';
import { getList } from '../api/knowledge';
import { getModelInfo } from '../api/experiment';
// import { ElMessage } from 'element-plus'; // 需要提示可开启

const stats = ref({
    total: 0,
    today_count: 0,
    disease_distribution: [],
    weekly_trend: [],
});
const knowledgeTotal = ref(0);
const modelInfo = ref({});
let refreshTimer = null;

// 独立加载统计数据
const loadStats = async () => {
    try {
        const res = await getStats();
        if (res && res.data) stats.value = res.data;
    } catch (err) {
        console.error('获取统计数据失败:', err);
    }
};

// 独立加载知识库数量
const loadKnowledge = async () => {
    try {
        const res = await getList({ page: 1, page_size: 1 });
        if (res && res.data) knowledgeTotal.value = res.data.total || 0;
    } catch (err) {
        console.error('获取知识库数据失败:', err);
    }
};

// 独立加载模型状态
const loadModel = async () => {
    try {
        const res = await getModelInfo();
        if (res && res.data) modelInfo.value = res.data;
    } catch (err) {
        console.error('获取模型信息失败:', err);
    }
};

// 汇总执行
const loadAllData = () => {
    loadStats();
    loadKnowledge();
    loadModel();
};

onMounted(() => {
    loadAllData(); // 首次加载
    
    // 开启轮询：每10秒刷新一次数据，实现实时趋势与今日检测数量的更新
    refreshTimer = setInterval(() => {
        loadStats(); 
        loadModel();
        // 知识库数量如果不常变，可以不放进轮询里
    }, 10000); 
});

onUnmounted(() => {
    if (refreshTimer) clearInterval(refreshTimer);
});
</script>


<style scoped>
.dashboard {
    max-width: 1200px;
}

.page-title {
    margin: 0 0 20px;
    font-size: 20px;
    color: #303133;
}

.stats-row {
    margin-bottom: 16px;
}

.stat-card :deep(.el-card__body) {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
}

.stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    flex-shrink: 0;
}

.stat-value {
    font-size: 28px;
    font-weight: 700;
    color: #303133;
}

.stat-label {
    font-size: 13px;
    color: #909399;
    margin-top: 4px;
}

.card-title {
    font-weight: 600;
    font-size: 15px;
}

.chart-row {
    margin-bottom: 16px;
}

.trend-chart {
    display: flex;
    align-items: flex-end;
    justify-content: space-around;
    height: 140px;
    padding: 10px 0;
}

.trend-bar-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    flex: 1;
}

.trend-bar {
    width: 24px;
    background: linear-gradient(180deg, #409eff, #67c23a);
    border-radius: 4px 4px 0 0;
    min-height: 4px;
    transition: height 0.3s;
}

.trend-bar-label {
    font-size: 12px;
    color: #606266;
}

.trend-date {
    font-size: 11px;
    color: #909399;
    white-space: nowrap;
}

.disease-row {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

.disease-name {
    width: 100px;
    font-size: 13px;
    color: #606266;
    flex-shrink: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.disease-count {
    font-size: 13px;
    color: #909399;
    width: 40px;
    text-align: right;
    flex-shrink: 0;
}

.quick-card {
    margin-top: 8px;
}

.quick-btns {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}

/* 模型信息卡片 */
.model-info-card {
    margin-bottom: 16px;
}

.model-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
}

.model-stat-label {
    font-size: 13px;
    color: #909399;
}

.model-stat-value {
    font-size: 24px;
    font-weight: 700;
    color: #303133;
}
</style>
