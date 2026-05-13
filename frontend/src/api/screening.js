import request from "./request";

// ==================== 智能简历筛选 ====================

/**
 * 岗位匹配筛选
 * @param {Object} data - 筛选参数
 * @param {number} data.position_id - 目标岗位ID
 * @param {number} data.top_n - 返回数量，默认10
 * @param {Object} data.filters - 筛选条件
 * @returns {Promise}
 */
export function screenByPosition(data) {
  return request.post("/screening/match", data);
}

/**
 * 自定义条件筛选
 * @param {Object} data - 筛选参数
 * @param {string} data.query - 自定义查询描述
 * @param {number} data.top_n - 返回数量，默认10
 * @returns {Promise}
 */
export function screenByCustomQuery(data) {
  return request.post("/screening/custom", data);
}

/**
 * 获取简历与岗位的匹配分析
 * @param {number} resumeId - 简历ID
 * @param {number} positionId - 岗位ID
 * @returns {Promise}
 */
export function getResumeAnalysis(resumeId, positionId) {
  return request.get(`/screening/analysis/${resumeId}`, {
    params: { position_id: positionId }
  });
}

/**
 * 批量标记筛选结果
 * @param {Object} data - 标记参数
 * @param {Array<number>} data.resume_ids - 简历ID列表
 * @param {string} data.mark_type - 标记类型：pass/reject/pending
 * @returns {Promise}
 */
export function batchMarkResumes(data) {
  return request.post("/screening/batch-mark", data);
}