import request from './request';

// 获取实验评估指标 (支持传入 { run: 'xxx' })
export const getExperimentMetrics = (params) => request.get('/experiment/metrics/', { params });

// 获取训练曲线数据
export const getTrainCurves = (params) => request.get('/experiment/curves/', { params });

// 获取模型基本信息
export const getModelInfo = (params) => request.get('/experiment/model-info/', { params });

// 获取历史训练记录 (不需要传参)
export const getTrainHistory = () => request.get('/experiment/train-history/');

// 获取训练配置参数
export const getTrainConfig = () => request.get('/experiment/train-config/');