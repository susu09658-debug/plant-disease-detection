<template>
  <div class="training-page">
    <h2 class="page-title">🎯 模型训练管理</h2>

    <!-- 训练配置 -->
    <el-card shadow="never" class="section-card">
      <template #header><span class="card-title">⚙️ 训练配置参考</span></template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="预训练模型">
          <el-tag type="primary">{{ trainConfig.model || 'yolo11n.pt' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="训练轮数">{{ trainConfig.epochs || 100 }}</el-descriptions-item>
        <el-descriptions-item label="批次大小">{{ trainConfig.batch || 16 }}</el-descriptions-item>
        <el-descriptions-item label="优化器">{{ trainConfig.optimizer || 'SGD' }}</el-descriptions-item>
        <el-descriptions-item label="初始学习率">{{ trainConfig.lr0 || 0.01 }}</el-descriptions-item>
        <el-descriptions-item label="图片尺寸">{{ trainConfig.imgsz || 640 }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 可用模型 -->
    <el-card shadow="never" class="section-card">
      <template #header><span class="card-title">🤖 YOLOv11 模型选项</span></template>
      <el-table :data="modelOptions" stripe>
        <el-table-column prop="name" label="模型名称" width="150">
          <template #default="{ row }">
            <el-tag type="primary">{{ row.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="params" label="参数量" width="120" />
        <el-table-column prop="desc" label="说明" />
      </el-table>
    </el-card>

    <!-- 训练命令参考 -->
    <el-card shadow="never" class="section-card">
      <template #header><span class="card-title">💻 训练命令参考</span></template>
      <div class="command-list">
        <div class="command-item">
          <div class="command-desc">使用默认参数训练（YOLOv11n, 100 epochs）</div>
          <el-text tag="code" class="command-code">python yolo/train.py</el-text>
        </div>
        <div class="command-item">
          <div class="command-desc">使用更大模型（YOLOv11s）</div>
          <el-text tag="code" class="command-code">python yolo/train.py --model yolo11s.pt --epochs 150</el-text>
        </div>
        <div class="command-item">
          <div class="command-desc">指定 GPU 训练</div>
          <el-text tag="code" class="command-code">python yolo/train.py --device 0</el-text>
        </div>
        <div class="command-item">
          <div class="command-desc">从中断处恢复训练</div>
          <el-text tag="code" class="command-code">python yolo/train.py --resume</el-text>
        </div>
        <div class="command-item">
          <div class="command-desc">在测试集上评估模型</div>
          <el-text tag="code" class="command-code">python yolo/evaluate.py --split test --save-json</el-text>
        </div>
        <div class="command-item">
          <div class="command-desc">部署模型到系统</div>
          <el-text tag="code" class="command-code">cp runs/train/thesis_optimized/weights/best.pt model/best.pt</el-text>
        </div>
      </div>
    </el-card>

    <!-- 历史训练记录 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-header-flex">
          <span class="card-title">📜 历史训练记录</span>
          <el-button size="small" @click="loadData" :icon="RefreshIcon">刷新</el-button>
        </div>
      </template>
      <el-table v-if="trainRuns.length" :data="trainRuns" stripe>
        <el-table-column prop="name" label="实验名称" width="160" />
        <el-table-column prop="model" label="模型" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.model || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="训练进度" width="140">
          <template #default="{ row }">
            {{ row.epochs_completed || 0 }} / {{ row.epochs || 0 }} epochs
          </template>
        </el-table-column>
        <el-table-column label="mAP@0.5" width="100">
          <template #default="{ row }">
            <span v-if="row.metrics?.mAP50" class="metric-highlight">
              {{ (row.metrics.mAP50 * 100).toFixed(1) }}%
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Precision" width="100">
          <template #default="{ row }">
            <span v-if="row.metrics?.precision">
              {{ (row.metrics.precision * 100).toFixed(1) }}%
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Recall" width="100">
          <template #default="{ row }">
            <span v-if="row.metrics?.recall">
              {{ (row.metrics.recall * 100).toFixed(1) }}%
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="最优权重" width="100">
          <template #default="{ row }">
            <el-tag :type="row.has_best_weight ? 'success' : 'info'" size="small">
              {{ row.has_best_weight ? '✓ 有' : '✗ 无' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="权重大小" width="100">
          <template #default="{ row }">
            {{ row.best_weight_size_mb ? row.best_weight_size_mb + ' MB' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="modified_time" label="修改时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.modified_time) }}
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无训练记录" :image-size="60">
        <template #description>
          <p>暂无训练记录。请在服务器上运行训练命令后刷新查看。</p>
        </template>
      </el-empty>
    </el-card>

    <!-- 毕业论文实验设计建议 -->
    <el-card shadow="never" class="section-card">
      <template #header><span class="card-title">📝 毕业论文实验设计建议</span></template>
      <div class="guide-content">
        <h4>实验一：模型对比实验</h4>
        <p>训练不同规模的 YOLOv11 模型（n/s/m），对比在 FieldPlant 数据集上的 mAP、Precision、Recall、F1 指标。</p>
        <el-text tag="code">python yolo/train.py --model yolo11n.pt --name exp_v11n</el-text>
        <br /><el-text tag="code">python yolo/train.py --model yolo11s.pt --name exp_v11s</el-text>
        <br /><el-text tag="code">python yolo/train.py --model yolo11m.pt --name exp_v11m</el-text>

        <h4>实验二：数据增强消融实验</h4>
        <p>对比不同数据增强策略（mosaic、mixup、翻转等）的影响，验证增强策略对模型性能的贡献。</p>

        <h4>实验三：学习率对比实验</h4>
        <p>对比不同初始学习率的训练效果。</p>
        <el-text tag="code">python yolo/train.py --lr0 0.001 --name exp_lr_0001</el-text>
        <br /><el-text tag="code">python yolo/train.py --lr0 0.01  --name exp_lr_001</el-text>
        <br /><el-text tag="code">python yolo/train.py --lr0 0.1   --name exp_lr_01</el-text>

        <h4>论文图表建议</h4>
        <ul>
          <li><strong>表格</strong>: 不同模型在测试集上的 mAP、Precision、Recall、F1 对比</li>
          <li><strong>图片</strong>: 训练损失曲线 (results.png)</li>
          <li><strong>图片</strong>: 混淆矩阵 (confusion_matrix.png)</li>
          <li><strong>图片</strong>: PR 曲线 (PR_curve.png)</li>
          <li><strong>图片</strong>: 检测效果示例 (val_batch*_pred.jpg)</li>
          <li><strong>表格</strong>: FieldPlant 各类别 AP 值对比</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, markRaw } from 'vue';
import { getTrainHistory, getTrainConfig } from '../api/experiment';
import { Refresh } from '@element-plus/icons-vue';

const RefreshIcon = markRaw(Refresh);

const trainRuns = ref([]);
const trainConfig = ref({});
const modelOptions = ref([]);

const formatTime = (isoStr) => {
  if (!isoStr) return '-';
  const d = new Date(isoStr);
  return d.toLocaleString('zh-CN');
};

const loadData = async () => {
  try {
    const [historyRes, configRes] = await Promise.all([
      getTrainHistory(),
      getTrainConfig(),
    ]);
    trainRuns.value = historyRes.data?.runs || [];
    trainConfig.value = configRes.data?.config || {};
    modelOptions.value = configRes.data?.model_options || [];
  } catch (e) {
    console.error('加载训练数据失败', e);
  }
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.training-page {
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

/* 命令列表 */
.command-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.command-item {
  background: #fafafa;
  border-radius: 6px;
  padding: 12px 16px;
}

.command-desc {
  font-size: 13px;
  color: #606266;
  margin-bottom: 6px;
}

.command-code {
  background: #f0f0f0;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
  color: #303133;
}

/* 指标高亮 */
.metric-highlight {
  color: #67c23a;
  font-weight: 600;
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

.guide-content p {
  color: #606266;
  line-height: 1.8;
  margin: 8px 0;
}

.guide-content ul {
  padding-left: 20px;
  color: #606266;
  line-height: 2;
}

.guide-content code {
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}
</style>
