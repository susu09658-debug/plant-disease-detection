<template>
  <div class="dataset-page">
    <h2 class="page-title">📁 数据集管理</h2>

    <!-- 数据集概览 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-header-flex">
          <span class="card-title">📊 数据集概览</span>
          <el-tag type="primary" size="small">FieldPlant</el-tag>
        </div>
      </template>
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="stat-card stat-blue">
            <div class="stat-value">{{ overview.num_classes || 0 }}</div>
            <div class="stat-label">类别总数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card stat-green">
            <div class="stat-value">{{ overview.total_images || 0 }}</div>
            <div class="stat-label">图片总数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card stat-orange">
            <div class="stat-value">{{ overview.total_labels || 0 }}</div>
            <div class="stat-label">标注总数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card" :class="overview.dataset_exists ? 'stat-green' : 'stat-red'">
            <div class="stat-value">{{ overview.dataset_exists ? '✓' : '✗' }}</div>
            <div class="stat-label">数据集状态</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 数据集信息 -->
    <el-card shadow="never" class="section-card">
      <template #header><span class="card-title">ℹ️ 数据集信息</span></template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="数据集名称">
          <el-tag type="primary">{{ overview.dataset_name || 'FieldPlant' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="数据来源">{{ overview.dataset_source || 'Roboflow' }}</el-descriptions-item>
        <el-descriptions-item label="类别数量">{{ overview.num_classes || 27 }} 类</el-descriptions-item>
        <el-descriptions-item label="数据集路径">
          <el-text size="small" type="info">{{ overview.dataset_path || '-' }}</el-text>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 数据集划分 -->
    <el-card shadow="never" class="section-card">
      <template #header><span class="card-title">📂 数据集划分</span></template>
      <el-row :gutter="16">
        <el-col :span="8" v-for="(info, split) in splits" :key="split">
          <div class="split-card">
            <div class="split-name">{{ splitLabels[split] || split }}</div>
            <div class="split-stats">
              <div class="split-stat">
                <span class="split-stat-value">{{ info.images || 0 }}</span>
                <span class="split-stat-label">图片</span>
              </div>
              <div class="split-stat">
                <span class="split-stat-value">{{ info.labels || 0 }}</span>
                <span class="split-stat-label">标注</span>
              </div>
              <div class="split-stat" v-if="info.size_mb !== undefined">
                <span class="split-stat-value">{{ info.size_mb }}</span>
                <span class="split-stat-label">MB</span>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
      <el-empty v-if="!Object.keys(splits).length" description="暂无划分信息" :image-size="60" />
    </el-card>

    <!-- 类别分布 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-header-flex">
          <span class="card-title">🏷️ 类别分布 ({{ classDetails.length }} 类)</span>
        </div>
      </template>
      <div v-if="classDetails.length" class="class-list">
        <div v-for="cls in classDetails" :key="cls.id" class="class-row">
          <span class="class-id">{{ cls.id }}</span>
          <span class="class-name-cn">{{ cls.name_cn || cls.name }}</span>
          <span class="class-name-en">({{ cls.name }})</span>
          <el-progress
            :percentage="getClassPercent(cls.count)"
            :stroke-width="14"
            :color="getBarColor(cls.count)"
            style="flex: 1; margin: 0 12px;"
          />
          <span class="class-count">{{ cls.count }} 样本</span>
        </div>
      </div>
      <el-empty v-else description="暂无类别数据（数据集尚未准备）" :image-size="80">
        <template #description>
          <div>
            <p>数据集尚未准备，请按照以下步骤操作：</p>
            <ol style="text-align: left; padding-left: 20px; line-height: 2;">
              <li>从 Roboflow 下载 FieldPlant 数据集 (YOLO 格式)</li>
              <li>运行 <code>python yolo/prepare_dataset.py --source /path/to/FieldPlant.v11</code></li>
              <li>或运行 <code>python yolo/prepare_dataset.py --validate</code> 验证已有数据集</li>
            </ol>
          </div>
        </template>
      </el-empty>
    </el-card>

    <!-- 数据集准备指南 -->
    <el-card shadow="never" class="section-card">
      <template #header><span class="card-title">📋 数据集准备指南</span></template>
      <div class="guide-content">
        <h4>方式一：下载 FieldPlant 数据集</h4>
        <ol>
          <li>访问 <a href="https://universe.roboflow.com/plant-disease-detection/fieldplant/dataset/11" target="_blank">Roboflow FieldPlant v11 Dataset</a></li>
          <li>选择 YOLO 格式导出并下载到本地</li>
          <li>运行准备脚本：<el-text tag="code">python yolo/prepare_dataset.py --source /path/to/FieldPlant.v11</el-text></li>
        </ol>

        <h4>方式二：兼容 PlantDoc 数据集</h4>
        <ol>
          <li>从 <a href="https://datasetninja.com/plantdoc" target="_blank">DatasetNinja</a> 下载 PlantDoc 数据集</li>
          <li>运行：<el-text tag="code">python yolo/prepare_dataset.py --source /path/to/plantdoc_raw --dataset plantdoc</el-text></li>
        </ol>

        <h4>验证数据集</h4>
        <p>准备完成后运行验证：<el-text tag="code">python yolo/prepare_dataset.py --validate</el-text></p>

        <h4>FieldPlant 数据集说明</h4>
        <p>FieldPlant 是一个包含 27 类植物病害的目标检测数据集，涵盖木薯（5 类）、玉米（16 类）、番茄（6 类）三种作物的健康与病害样本。数据集采用 Roboflow YOLO 格式，标注质量高，适合用于植物病害目标检测模型的训练与评估。如果仅解压了 train/ 目录，工具会自动按 80/10/10 比例划分为 train/val/test 集。许可证：CC BY 4.0。</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { getDatasetOverview, getDatasetSplitInfo } from '../api/dataset';

const overview = ref({});
const classDetails = ref([]);
const splits = ref({});

const splitLabels = {
  train: '🟢 训练集 (Train)',
  val: '🟡 验证集 (Val)',
  test: '🔴 测试集 (Test)',
};

const maxCount = computed(() => {
  if (!classDetails.value.length) return 1;
  return Math.max(...classDetails.value.map(c => c.count), 1);
});

const getClassPercent = (count) => {
  return Math.round((count / maxCount.value) * 100);
};

const getBarColor = (count) => {
  const pct = count / maxCount.value;
  if (pct >= 0.7) return '#67c23a';
  if (pct >= 0.3) return '#409eff';
  if (pct > 0) return '#e6a23c';
  return '#c0c4cc';
};

const loadData = async () => {
  try {
    const [overviewRes, splitRes] = await Promise.all([
      getDatasetOverview(),
      getDatasetSplitInfo(),
    ]);
    overview.value = overviewRes.data || {};
    classDetails.value = overviewRes.data?.class_details || [];
    splits.value = splitRes.data?.splits || {};
  } catch (e) {
    console.error('加载数据集信息失败', e);
  }
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.dataset-page {
  max-width: 1200px;
}

.page-title {
  margin: 0 0 20px;
  font-size: 20px;
  color: #303133;
}

.section-card {
  margin-bottom: 16px;
}

.card-title {
  font-weight: 600;
  font-size: 15px;
}

.card-header-flex {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 统计卡片 */
.stat-card {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  border-left: 4px solid #409eff;
  transition: box-shadow 0.2s;
}

.stat-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.stat-blue { border-left-color: #409eff; }
.stat-green { border-left-color: #67c23a; }
.stat-orange { border-left-color: #e6a23c; }
.stat-red { border-left-color: #f56c6c; }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 6px;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

/* 划分卡片 */
.split-card {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.split-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.split-stats {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.split-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.split-stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}

.split-stat-label {
  font-size: 12px;
  color: #909399;
}

/* 类别列表 */
.class-list {
  max-height: 600px;
  overflow-y: auto;
}

.class-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  padding: 4px 0;
}

.class-id {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #ecf5ff;
  color: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
  margin-right: 10px;
}

.class-name-cn {
  width: 120px;
  font-size: 13px;
  color: #303133;
  font-weight: 500;
  flex-shrink: 0;
}

.class-name-en {
  width: 200px;
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
}

.class-count {
  width: 70px;
  text-align: right;
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  flex-shrink: 0;
}

/* 指南 */
.guide-content h4 {
  margin: 16px 0 8px;
  color: #303133;
  font-size: 15px;
}

.guide-content h4:first-child {
  margin-top: 0;
}

.guide-content ol {
  padding-left: 20px;
  color: #606266;
  line-height: 2;
}

.guide-content p {
  color: #606266;
  line-height: 1.8;
  margin: 8px 0;
}

.guide-content code {
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}
</style>
