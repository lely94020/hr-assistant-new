import request from "./request";

// 获取岗位列表
export function getPositionList(params) {
  return request.get("/positions", { params });
}

// 获取岗位详情

// 这是一个使用ES6模块语法的导出函数，命名为getPositionDetail
// 函数接受一个参数id，用于指定要查询的职位ID
// 函数内部使用request.get()方法发送一个GET请求到API端点/positions/${id}
// 这里使用了模板字符串（template literals）来动态构建API路径，将传入的id参数插入到URL中
// 函数返回这个HTTP请求的Promise对象
// 用途
// 这个函数通常用于前端应用程序中，当需要显示特定职位的详细信息时调用
// 它封装了获取职位数据的API调用，使代码更加模块化和可重用
// 通过导出这个函数，其他模块可以导入并使用它来获取职位数据
export function getPositionDetail(id) {
  return request.get(`/positions/${id}`);
}

// 创建岗位
export function createPosition(data) {
  return request.post("/positions", data);
}

// 更新岗位
export function updatePosition(id, data) {
  return request.put(`/positions/${id}`, data);
}

// 删除岗位
export function deletePosition(id) {
  return request.delete(`/positions/${id}`);
}