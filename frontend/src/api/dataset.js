import request from './request';



// 获取可用数据集列表 (新增)
export const getDatasetList = () => request.get('/dataset/list/');
// 获取数据集概览 (新增 datasetPath 参数)
export const getDatasetOverview = (datasetPath) => request.get('/dataset/overview/', { 
  params: { dataset_path: datasetPath } 
});

// 获取类别列表及各类别样本数 (新增 datasetPath 参数)
export const getDatasetClasses = (datasetPath) => request.get('/dataset/classes/', { 
  params: { dataset_path: datasetPath } 
});

// 获取指定类别/划分的样本图片
// 注意：这里将 datasetPath 作为一个独立参数，并与原有的 params（比如 split, class_id）合并
export const getDatasetSamples = (datasetPath, params = {}) => request.get('/dataset/samples/', { 
  params: { dataset_path: datasetPath, ...params } 
});

// 获取数据集划分信息 (新增 datasetPath 参数)
export const getDatasetSplitInfo = (datasetPath) => request.get('/dataset/split-info/', { 
  params: { dataset_path: datasetPath } 
});

// 验证数据集完整性（管理员）
// 注意：这是 POST 请求，所以 dataset_path 放在请求体 (data) 里，而不是 URL params 里
export const validateDataset = (datasetPath) => request.post('/dataset/validate/', { 
  dataset_path: datasetPath 
});