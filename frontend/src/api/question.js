// frontend/src/api/question.js
import request from "./request";

// ==================== 智能面试题生成 ====================

/**
 * 智能生成面试题
 * @param {Object} data - 生成参数
 * @param {string} data.mode - 生成模式：position/resume/mixed
 * @param {number} data.position_id - 岗位ID（mode为position或mixed时必需）
 * @param {number} data.resume_id - 简历ID（mode为resume或mixed时必需）
 * @param {Array<string>} data.question_types - 题目类型列表：technical/behavioral/situational/open
 * @param {string} data.difficulty - 难度等级：junior/middle/senior
 * @param {number} data.count - 题目数量（1-20）
 * @param {boolean} data.with_answer - 是否生成参考答案
 * @returns {Promise}
 */
export function generateQuestions(data) {
  return request.post("/questions/generate", data);
}

/**
 * 获取面试题列表
 * @param {Object} params - 查询参数
 * @param {number} params.position_id - 可选，按岗位筛选
 * @param {number} params.resume_id - 可选，按简历筛选
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise}
 */
export function getQuestionList(params) {
  return request.get("/questions", { params });
}

/**
 * 编辑面试题
 * @param {number} id - 题目ID
 * @param {Object} data - 更新的字段
 * @param {string} data.question_content - 题目内容
 * @param {string} data.reference_answer - 参考答案
 * @param {Array<string>} data.scoring_points - 评分要点
 * @returns {Promise}
 */
export function updateQuestion(id, data) {
  return request.put(`/questions/${id}`, data);
}

/**
 * 删除面试题
 * @param {number} id - 题目ID
 * @returns {Promise}
 */
export function deleteQuestion(id) {
  return request.delete(`/questions/${id}`);
}

/**
 * 保存题目到题库
 * @param {Array<number>} questionIds - 要保存的题目ID列表
 * @returns {Promise}
 */
export function saveToQuestionBank(questionIds) {
  return request.post("/questions/save-to-bank", {
    question_ids: questionIds
  });
}
