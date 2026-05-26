<template>
  <div class="training-page">
    <h2 class="page-title">🎯 模型训练管理</h2>

    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-header-flex">
          <span class="card-title">⚙️ 训练配置参考</span>
          <el-select 
            v-model="selectedStrategy" 
            @change="handleStrategyChange" 
            placeholder="切换配置方案" 
            size="small" 
            style="width: 220px;"
          >
            <el-option
              v-for="item in strategies"
              :key="item.filename"
              :label="item.label"
              :value="item.filename"
            />
          </el-select>
        </div>
      </template>

      <el-tabs v-model="activeConfigTab" class="config-tabs">
        <el-tab-pane label="📚 基础训练参数" name="basic">
          <el-descriptions :column="3" border size="small">
            <el-descriptions-item label="预训练模型">
              <el-tag type="primary" size="small">{{ trainConfig.model || 'yolo11n.pt' }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="训练轮数 (epochs)">{{ trainConfig.epochs || '-' }}</el-descriptions-item>
            <el-descriptions-item label="批次大小 (batch)">{{ trainConfig.batch || '-' }}</el-descriptions-item>
            <el-descriptions-item label="图片尺寸 (imgsz)">{{ trainConfig.imgsz || '-' }}</el-descriptions-item>
            <el-descriptions-item label="早停轮数 (patience)">{{ trainConfig.patience || '-' }}</el-descriptions-item>
            <el-descriptions-item label="梯度累积 (nbs)">{{ trainConfig.nbs || '默认' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <el-tab-pane label="📉 优化器与学习率" name="optimizer">
          <el-descriptions :column="3" border size="small">
            <el-descriptions-item label="优化器 (optimizer)">
              <el-tag type="success" size="small">{{ trainConfig.optimizer || '-' }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="初始学习率 (lr0)">{{ trainConfig.lr0 || '-' }}</el-descriptions-item>
            <el-descriptions-item label="终止学习率 (lrf)">{{ trainConfig.lrf || '-' }}</el-descriptions-item>
            <el-descriptions-item label="动量系数 (momentum)">{{ trainConfig.momentum || '-' }}</el-descriptions-item>
            <el-descriptions-item label="权重衰减 (weight_decay)">{{ trainConfig.weight_decay || '-' }}</el-descriptions-item>
            <el-descriptions-item label="预热轮数 (warmup_epochs)">{{ trainConfig.warmup_epochs || '-' }}</el-descriptions-item>
            <el-descriptions-item label="余弦退火 (cos_lr)">
              <el-tag :type="trainConfig.cos_lr ? 'success' : 'info'" size="small">
                {{ trainConfig.cos_lr ? '已启用' : '未启用' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <el-tab-pane label="🖼️ 数据增强策略" name="augment">
          <el-descriptions :column="3" border size="small">
            <el-descriptions-item label="Mosaic 拼接">{{ trainConfig.mosaic || '-' }}</el-descriptions-item>
            <el-descriptions-item label="末期关闭 (close_mosaic)">
               <el-text type="danger" v-if="trainConfig.close_mosaic">最后 {{ trainConfig.close_mosaic }} 轮</el-text>
               <span v-else>-</span>
            </el-descriptions-item>
            <el-descriptions-item label="MixUp 混合">{{ trainConfig.mixup || '-' }}</el-descriptions-item>
            <el-descriptions-item label="实例复制 (copy_paste)">{{ trainConfig.copy_paste || '-' }}</el-descriptions-item>
            <el-descriptions-item label="随机擦除 (erasing)">{{ trainConfig.erasing || '-' }}</el-descriptions-item>
            <el-descriptions-item label="色彩增强 (HSV)">
              <span v-if="trainConfig.hsv_h">H:{{trainConfig.hsv_h}}, S:{{trainConfig.hsv_s}}, V:{{trainConfig.hsv_v}}</span>
              <span v-else>-</span>
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <el-tab-pane label="⚖️ 损失函数与正则化" name="loss">
          <el-descriptions :column="3" border size="small">
            <el-descriptions-item label="Box 回归权重 (box)">{{ trainConfig.box || '-' }}</el-descriptions-item>
            <el-descriptions-item label="分类权重 (cls)">{{ trainConfig.cls || '-' }}</el-descriptions-item>
            <el-descriptions-item label="焦点损失权重 (dfl)">{{ trainConfig.dfl || '-' }}</el-descriptions-item>
            <el-descriptions-item label="标签平滑 (label_smoothing)">{{ trainConfig.label_smoothing || '未启用' }}</el-descriptions-item>
            <el-descriptions-item label="混合精度训练 (amp)">
               <el-tag :type="trainConfig.amp ? 'success' : 'info'" size="small">
                {{ trainConfig.amp ? 'FP16 开启' : '关闭' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card shadow="never" class="section-card">
      <template #header><span class="card-title">🤖 YOLOv11 模型选项</span></template>
      <el-table :data="modelOptions" stripe size="small">
        <el-table-column prop="name" label="模型名称" width="150">
          <template #default="{ row }">
            <el-tag type="primary">{{ row.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="params" label="参数量" width="120" />
        <el-table-column prop="desc" label="说明" />
      </el-table>
    </el-card>

    <el-card shadow="never" class="section-card">
      <template #header><span class="card-title">💻 训练命令参考</span></template>
      <div class="command-list">
        <div class="command-item">
          <div class="command-desc">使用当前选择的策略配置文件进行训练（推荐）</div>
          <el-text tag="code" class="command-code">python yolo/train.py --cfg yolo/configs/{{ selectedStrategy || 'strategy_thesis.yaml' }}</el-text>
        </div>
        <div class="command-item">
          <div class="command-desc">指定 GPU 训练 (单卡推荐设备 0)</div>
          <el-text tag="code" class="command-code">python yolo/train.py --cfg yolo/configs/{{ selectedStrategy || 'strategy_thesis.yaml' }} --device 0</el-text>
        </div>
        <div class="command-item">
          <div class="command-desc">从中断处恢复训练</div>
          <el-text tag="code" class="command-code">python yolo/train.py --resume</el-text>
        </div>
      </div>
    </el-card>

    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-header-flex">
          <span class="card-title">📜 历史训练记录</span>
          <el-button size="small" @click="loadData" :icon="RefreshIcon">刷新</el-button>
        </div>
      </template>
      <el-table v-if="trainRuns.length" :data="trainRuns" stripe>
        <el-table-column prop="name" label="实验名称" width="140" />
        <el-table-column prop="model" label="模型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.model || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="训练进度" width="120">
          <template #default="{ row }">
            {{ row.epochs_completed || 0 }} / {{ row.epochs || 0 }} epochs
          </template>
        </el-table-column>
        <el-table-column label="mAP@0.5" width="90">
          <template #default="{ row }">
            <span v-if="row.metrics?.mAP50" class="metric-highlight">
              {{ (row.metrics.mAP50 * 100).toFixed(1) }}%
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Precision" width="90">
          <template #default="{ row }">
            <span v-if="row.metrics?.precision">
              {{ (row.metrics.precision * 100).toFixed(1) }}%
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Recall" width="90">
          <template #default="{ row }">
            <span v-if="row.metrics?.recall">
              {{ (row.metrics.recall * 100).toFixed(1) }}%
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="最优权重" width="90">
          <template #default="{ row }">
            <el-tag :type="row.has_best_weight ? 'success' : 'info'" size="small">
              {{ row.has_best_weight ? '✓ 有' : '✗ 无' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="权重大小" width="90">
          <template #default="{ row }">
            {{ row.best_weight_size_mb ? row.best_weight_size_mb + ' MB' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="modified_time" label="修改时间" width="170">
          <template #default="{ row }">
            {{ formatTime(row.modified_time) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="100" fixed="right" align="center">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              :disabled="!row.has_best_weight"
              @click="handleDeploy(row)"
            >
              部署
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无训练记录" :image-size="60">
        <template #description>
          <p>暂无训练记录。请在服务器上运行训练命令后刷新查看。</p>
        </template>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, markRaw } from 'vue';
import { getTrainHistory, getTrainConfig, deployModel, getStrategyConfigs } from '../api/experiment';
import { Refresh } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';

const RefreshIcon = markRaw(Refresh);

const trainRuns = ref([]);
const trainConfig = ref({});
const modelOptions = ref([]);

// 策略相关的状态变量
const strategies = ref([]);
const selectedStrategy = ref('');
const activeConfigTab = ref('basic'); // 新增：控制配置选项卡的当前视图

const formatTime = (isoStr) => {
  if (!isoStr) return '-';
  const d = new Date(isoStr);
  return d.toLocaleString('zh-CN');
};

const loadData = async () => {
  try {
    // 并发请求：历史记录、基础配置、策略配置
    const [historyRes, configRes, stratRes] = await Promise.all([
      getTrainHistory(),
      getTrainConfig(),
      getStrategyConfigs()
    ]);
    
    trainRuns.value = historyRes.data?.runs || [];
    modelOptions.value = configRes.data?.model_options || [];
    
    // 处理策略列表并默认选中 thesis
    if (stratRes.data?.strategies?.length) {
      strategies.value = stratRes.data.strategies;
      
      // 尝试寻找包含 'thesis' 的配置文件作为默认值
      const defaultStrat = strategies.value.find(s => s.filename.includes('thesis')) || strategies.value[0];
      
      selectedStrategy.value = defaultStrat.filename;
      trainConfig.value = defaultStrat.content; 
    } else {
      // 降级处理：如果没有读到 yaml 文件，则使用旧接口的基础数据
      trainConfig.value = configRes.data?.config || {};
    }
  } catch (e) {
    console.error('加载训练数据失败', e);
  }
};

// 切换策略时的处理函数
const handleStrategyChange = (filename) => {
  const strat = strategies.value.find(s => s.filename === filename);
  if (strat) {
    trainConfig.value = strat.content;
  }
};

// 部署处理逻辑
const handleDeploy = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要将实验 "${row.name}" 的最优模型部署到系统吗？这将会覆盖当前目录下的 model/best.pt 文件。`,
      '部署确认',
      {
        confirmButtonText: '确定部署',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    const res = await deployModel({ run_name: row.name });
    
    if (res.code === 200) {
      ElMessage.success(`🎉 实验 ${row.name} 模型部署成功！系统现在将使用该模型。`);
      loadData(); // 重新加载数据刷新状态
    } else {
      ElMessage.error(res.msg || '部署失败，请检查后端日志。');
    }
  } catch (e) {
    if (e !== 'cancel') {
      console.error('部署请求异常', e);
      ElMessage.error('请求异常，部署未完成');
    }
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

/* 👇 新增选项卡样式优化 */
.config-tabs {
  margin-top: 10px;
}
:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: #ebeef5;
}
:deep(.el-descriptions__label) {
  width: 150px;
  color: #606266;
  font-weight: 500;
}

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
.metric-highlight {
  color: #67c23a;
  font-weight: 600;
}
</style>