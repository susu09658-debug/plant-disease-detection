import request from './request';

// 获取数据集概览
export const getDatasetOverview = () => request.get('/dataset/overview/');

// 获取类别列表及各类别样本数
export const getDatasetClasses = () => request.get('/dataset/classes/');

// 获取指定类别/划分的样本图片
export const getDatasetSamples = (params) => request.get('/dataset/samples/', { params });

// 获取数据集划分信息
export const getDatasetSplitInfo = () => request.get('/dataset/split-info/');

// 验证数据集完整性（管理员）
export const validateDataset = () => request.post('/dataset/validate/');
