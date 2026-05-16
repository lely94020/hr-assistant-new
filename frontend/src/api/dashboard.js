import request from "./request";

/**
 * 获取仪表盘统计数据
 */
export function getDashboardStats() {
  return request.get("/dashboard/stats");
}

/**
 * 获取待办事项列表
 */
export function getTodoList(params) {
  return request.get("/dashboard/todos", { params });
}

/**
 * 创建待办事项
 */
export function createTodo(data) {
  return request.post("/dashboard/todos", data);
}

/**
 * 更新待办事项
 */
export function updateTodo(id, data) {
  return request.put(`/dashboard/todos/${id}`, data);
}

/**
 * 删除待办事项
 */
export function deleteTodo(id) {
  return request.delete(`/dashboard/todos/${id}`);
}

/**
 * 清除已完成待办
 */
export function clearCompletedTodos() {
  return request.delete("/dashboard/todos/completed");
}

/**
 * 获取最近的面试安排
 */
export function getRecentInterviews(params) {
  return request.get("/dashboard/interviews/recent", { params });
}

/**
 * 获取最近动态
 */
export function getRecentActivities(params) {
  return request.get("/dashboard/activities", { params });
}