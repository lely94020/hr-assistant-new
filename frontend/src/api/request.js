import axios from "axios";
import { ElMessage } from "element-plus";
import router from "@/router";

const request = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  timeout: 180000,
});

// 请求拦截器 - 自动添加token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      // 清除token
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('user_info')
      // 跳转到登录页
      router.push('/login')
    } else {
      ElMessage.error(error.response?.data?.detail || "请求失败");
    }
    return Promise.reject(error);
  },
);

export default request;
