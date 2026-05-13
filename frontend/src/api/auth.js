import request from "./request";

// 用户登录
export function login(data) {
  return request.post("/login", data);
}

// 用户登出
export function logout() {
  return request.post("/logout");
}

// 验证token
export function verifyToken() {
  return request.get("/login/verify");
}
