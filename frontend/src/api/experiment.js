import request from './request';

// 获取实验评估指标
export const getExperimentMetrics = () => request.get('/experiment/metrics/');

// 获取训练曲线数据
export const getTrainCurves = () => request.get('/experiment/curves/');

// 获取模型基本信息
export const getModelInfo = () => request.get('/experiment/model-info/');
