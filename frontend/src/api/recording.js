import request from "./request";

// ==================== 录音上传 ====================

/**
 * 上传录音文件
 * @param {FormData} formData - 包含file、resume_id等字段
 * @returns {Promise}
 */
export function uploadRecording(formData) {
  return request.post("/recordings/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
}

// ==================== 录音查询 ====================

/**
 * 获取录音列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getRecordingList(params) {
  return request.get("/recordings/", { params });
}

/**
 * 获取录音详情
 * @param {number} id - 录音ID
 * @returns {Promise}
 */
export function getRecordingDetail(id) {
  return request.get(`/recordings/${id}`);
}

// ==================== 语音转写 ====================

/**
 * 开始语音转文字
 * @param {number} id - 录音ID
 * @returns {Promise}
 */
export function startTranscribe(id) {
  return request.post(`/recordings/${id}/transcribe`);
}

/**
 * 获取转写状态
 * @param {number} id - 录音ID
 * @returns {Promise}
 */
export function getTranscribeStatus(id) {
  return request.get(`/recordings/${id}/status`);
}

/**
 * 获取文字稿
 * @param {number} id - 录音ID
 * @returns {Promise}
 */
export function getTranscript(id) {
  return request.get(`/recordings/${id}/transcript`);
}

/**
 * 更新文字稿
 * @param {number} id - 录音ID
 * @param {string} transcript - 文字稿内容
 * @returns {Promise}
 */
export function updateTranscript(id, transcript) {
  return request.put(`/recordings/${id}/transcript`, { transcript });
}

// ==================== 录音删除 ====================

/**
 * 删除录音
 * @param {number} id - 录音ID
 * @returns {Promise}
 */
export function deleteRecording(id) {
  return request.delete(`/recordings/${id}`);
}