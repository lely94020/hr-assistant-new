import request from "./request";

// ==================== 面试摘要生成 ====================

/**
 * 生成面试摘要
 * @param {number} recordingId - 录音ID
 * @returns {Promise}
 */
export function generateSummary(recordingId) {
  return request.post("/summaries/generate", {
    recording_id: recordingId,
  });
}

// ==================== 面试摘要查询 ====================

/**
 * 获取面试摘要（通过录音ID）
 * @param {number} recordingId - 录音ID
 * @returns {Promise}
 */
export function getSummaryByRecordingId(recordingId) {
  return request.get(`/summaries/${recordingId}`);
}


// ==================== 面试摘要更新 ====================

/**
 * 更新面试摘要
 * @param {number} summaryId - 摘要ID
 * @param {Object} data - 更新数据
 * @returns {Promise}
 */
export function updateSummary(summaryId, data) {
  return request.put(`/summaries/${summaryId}`, data);
}

/**
 * 重新生成面试摘要
 * @param {number} summaryId - 摘要ID
 * @returns {Promise}
 */
export function regenerateSummary(summaryId) {
  return request.post(`/summaries/${summaryId}/regenerate`);
}

// ==================== 面试摘要删除 ====================

/**
 * 删除面试摘要
 * @param {number} summaryId - 摘要ID
 * @returns {Promise}
 */
export function deleteSummary(summaryId) {
  return request.delete(`/summaries/${summaryId}`);
}