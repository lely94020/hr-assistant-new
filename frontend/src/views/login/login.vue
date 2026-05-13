<template>
  <div class="login-container">
    <!-- 左侧品牌区域 -->
    <div class="brand-section">
      <div class="brand-content">
        <h1>AI赋能招聘全流程</h1>
        <p>智能、高效、安全的企业人力资源管理解决方案</p>
      </div>
    </div>

    <!-- 右侧登录表单区域 -->
    <div class="login-section">
      <div class="login-card">
        <!-- Logo和标题 -->
        <div class="login-header">
          <el-icon class="logo-icon" size="40">
            <OfficeBuilding />
          </el-icon>
          <h1 class="system-title">企业HR智能助手</h1>
        </div>

        <!-- 登录表单 -->
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              size="large"
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              show-password
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item class="form-options">
            <el-checkbox v-model="loginForm.rememberMe">记住我</el-checkbox>
            <el-link type="primary" class="forgot-password">忘记密码?</el-link>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { OfficeBuilding, User, Lock } from '@element-plus/icons-vue'
import { login } from '@/api/auth'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)

// 表单数据
const loginForm = reactive({
  username: '',
  password: '',
  rememberMe: false
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

// 登录处理
const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true

      try {
        // 调用后端登录API
        const res = await login({
          username: loginForm.username,
          password: loginForm.password
        })

        // 登录成功，保存token和用户信息
        localStorage.setItem('access_token', res.access_token)
        localStorage.setItem('user_info', JSON.stringify(res.user))

        // 如果选择了"记住我"，保存到localStorage
        if (loginForm.rememberMe) {
          localStorage.setItem('remember_me', 'true')
        } else {
          // 否则同时保存到sessionStorage（会话级别）
          sessionStorage.setItem('access_token', res.access_token)
          sessionStorage.setItem('user_info', JSON.stringify(res.user))
        }

        ElMessage.success('登录成功')

        // 跳转到之前访问的页面或dashboard
        const redirect = router.currentRoute.value.query.redirect || '/dashboard'
        router.push(redirect)
      } catch (error) {
        console.error('登录失败:', error)
        ElMessage.error(error.message || '登录失败，请检查用户名和密码')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  width: 100%;
  height: 100vh;
}

/* 左侧品牌区域 */
.brand-section {
  flex: 0 0 60%;
  background: linear-gradient(135deg, #409EFF 0%, #67C23A 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.brand-content {
  text-align: center;
  padding: 20px;
}

.brand-content h1 {
  font-size: 36px;
  margin-bottom: 16px;
  font-weight: 600;
}

.brand-content p {
  font-size: 18px;
  opacity: 0.9;
}

/* 右侧登录区域 */
.login-section {
  flex: 0 0 40%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 40px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  color: #409EFF;
  margin-bottom: 12px;
}

.system-title {
  font-size: 28px;
  color: #303133;
  margin: 0;
  font-weight: 600;
}

.login-form {
  width: 100%;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.forgot-password {
  font-size: 14px;
}

.login-btn {
  width: 100%;
  background-color: #409EFF;
  border-color: #409EFF;
}

.login-btn:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .brand-section {
    display: none;
  }

  .login-section {
    flex: 1;
  }

  .login-card {
    max-width: 100%;
    margin: 0 20px;
  }

  .system-title {
    font-size: 24px;
  }
}
</style>
