import request from "./request";

// ==================== 候选人对比 ====================

/**
 * 创建候选人对比
 * @param {number} positionId - 岗位ID
 * @param {Array<number>} resumeIds - 简历ID数组（2-5个）
 * @returns {Promise}
 */
export function createComparison(positionId, resumeIds) {
  return request.post("/comparison/create", {
    position_id: positionId,
    resume_ids: resumeIds,
  });
}

/**
 * 获取对比详情
 * @param {number} comparisonId - 对比ID
 * @returns {Promise}
 */
export function getComparisonDetail(comparisonId) {
  return request.get(`/comparison/${comparisonId}`);
}

/**
 * AI对比分析
 * @param {number} comparisonId - 对比ID
 * @returns {Promise}
 */
export function analyzeComparison(comparisonId) {
  return request.post(`/comparison/${comparisonId}/analyze`);
}

/**
 * 获取对比历史
 * @param {Object} params - 查询参数 { page, page_size }
 * @returns {Promise}
 */
export function getComparisonHistory(params) {
  return request.get("/comparison/history", { params });
}

/**
 * 导出对比报告
 * @param {number} comparisonId - 对比ID
 * @returns {Promise}
 */
export function exportComparisonReport(comparisonId) {
  return request.get(`/comparison/${comparisonId}/export`);
}