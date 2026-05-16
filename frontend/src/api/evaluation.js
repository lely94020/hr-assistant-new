import request from "./request";

// ==================== 面试评价生成 ====================

/**
 * 生成面试评价
 * @param {number} summaryId - 面试摘要ID
 * @returns {Promise}
 */
export function generateEvaluation(summaryId) {
  return request.post("/evaluations/generate", {
    summary_id: summaryId,
  });
}

// ==================== 面试评价查询 ====================

/**
 * 获取最新面试评价（通过简历ID）
 * @param {number} resumeId - 简历ID
 * @returns {Promise}
 */
export function getLatestEvaluation(resumeId) {
  return request.get(`/evaluations/${resumeId}`);
}

/**
 * 获取面试评价历史（通过简历ID）
 * @param {number} resumeId - 简历ID
 * @returns {Promise}
 */
export function getEvaluationHistory(resumeId) {
  return request.get(`/evaluations/history/${resumeId}`);
}

// ==================== HR补充评价 ====================

/**
 * 添加或更新HR补充评价
 * @param {number} evaluationId - 评价ID
 * @param {string} hrComment - HR补充评价内容
 * @returns {Promise}
 */
export function updateHrComment(evaluationId, hrComment) {
  return request.put(`/evaluations/${evaluationId}/hr-comment`, {
    hr_comment: hrComment,
  });
}