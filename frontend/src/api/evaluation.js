import request from "./request";

// ==================== 面试评价查询 ====================

/**
 * 获取面试评价列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getEvaluationList(params) {
  return request.get("/evaluations", { params });
}

/**
 * 获取面试评价详情
 * @param {number} id - 评价ID
 * @returns {Promise}
 */
export function getEvaluationDetail(id) {
  return request.get(`/evaluations/detail/${id}`);
}

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

// ==================== 面试评价删除 ====================

/**
 * 删除面试评价
 * @param {number} id - 评价ID
 * @returns {Promise}
 */
export function deleteEvaluation(id) {
  return request.delete(`/evaluations/${id}`);
}
