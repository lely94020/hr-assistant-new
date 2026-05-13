import request from "./request";

// ==================== 简历上传 ====================

/**
 * 上传简历（支持批量）
 * @param {FormData} formData - 包含files和可选的position_id
 * @returns {Promise}
 */
export function uploadResumes(formData) {
  return request.post("/resumes/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
}

// ==================== 简历查询 ====================

/**
 * 获取简历列表（分页+筛选）
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getResumeList(params) {
  return request.get("/resumes", { params });
}

/**
 * 获取简历详情
 * @param {number} id - 简历ID
 * @returns {Promise}
 */
export function getResumeDetail(id) {
  return request.get(`/resumes/${id}`);
}

// ==================== 简历下载 ====================

/**
 * 下载单个简历
 * @param {number} id - 简历ID
 * @returns {Promise}
 */
export function downloadResume(id) {
  return request.get(`/resumes/${id}/download`, {
    responseType: "blob",
  });
}

/**
 * 批量下载简历
 * @param {Array<number>} resumeIds - 简历ID数组
 * @returns {Promise}
 */
export function batchDownloadResumes(resumeIds) {
  return request.post(
    "/resumes/batch-download",
    { resume_ids: resumeIds },
    {
      responseType: "blob",
    }
  );
}

// ==================== 简历删除 ====================

/**
 * 删除单个简历
 * @param {number} id - 简历ID
 * @returns {Promise}
 */
export function deleteResume(id) {
  return request.delete(`/resumes/${id}`);
}

/**
 * 批量删除简历
 * @param {Array<number>} resumeIds - 简历ID数组
 * @returns {Promise}
 */
export function batchDeleteResumes(resumeIds) {
  return request.post("/resumes/batch-delete", {
    resume_ids: resumeIds,
  });
}

// ==================== 简历状态管理 ====================

/**
 * 关联岗位
 * @param {number} id - 简历ID
 * @param {number} positionId - 岗位ID
 * @returns {Promise}
 */
export function bindPosition(id, positionId) {
  return request.put(`/resumes/${id}/bindPosition`, { position_id: positionId });
}

/**
 * 更新简历状态
 * @param {number} id - 简历ID
 * @param {number} status - 状态值 (1-待筛选 2-初筛通过 3-面试中 4-已录用 5-已淘汰)
 * @returns {Promise}
 */
export function updateResumeStatus(id, status) {
  return request.patch(`/resumes/${id}/status`, { status });
}

// ==================== 简历信息更新 ====================

/**
 * 更新简历信息
 * @param {number} id - 简历ID
 * @param {Object} data - 更新的字段
 * @returns {Promise}
 */
export function updateResume(id, data) {
  return request.put(`/resumes/${id}`, data);
}

/**
 * 重新解析简历
 * @param {number} id - 简历ID
 * @returns {Promise}
 */
export function reparseResume(id) {
  return request.post(`/resumes/${id}/reparse`);
}
