<template>
  <el-container class="layout-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <el-icon class="logo-icon" size="32" color="#409EFF">
          <Monitor />
        </el-icon>
        <span class="system-name">企业HR智能助手</span>
        <el-icon
          class="collapse-btn"
          @click="toggleCollapse"
          size="20"
        >
          <component :is="isCollapse ? Expand : Fold" />
        </el-icon>
      </div>

      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <div class="user-info">
            <el-avatar :size="32" :src="userInfo.avatar || defaultAvatar" />
            <span class="username">{{ userInfo.username || 'Admin' }}</span>
            <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人信息
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                系统设置
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container>
      <!-- 左侧菜单栏 -->
      <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
        <el-menu
          :collapse="isCollapse"
          :collapse-transition="false"
          mode="vertical"
          router
          active-text-color="#409EFF"
          background-color="#001529"
          text-color="#bfcbd9"
          class="sidebar-menu"
          :default-active="activeMenu"
        >
          <el-menu-item index="/dashboard">
            <el-icon><House /></el-icon>
            <template #title>工作台</template>
          </el-menu-item>

          <el-menu-item index="/position">
            <el-icon><OfficeBuilding /></el-icon>
            <template #title>岗位管理</template>
          </el-menu-item>

          <el-menu-item index="/resume">
            <el-icon><Document /></el-icon>
            <template #title>简历管理</template>
          </el-menu-item>

          <el-menu-item index="/screening">
            <el-icon><Search /></el-icon>
            <template #title>智能筛选</template>
          </el-menu-item>

          <el-menu-item index="/question">
            <el-icon><QuestionFilled /></el-icon>
            <template #title>面试题生成</template>
          </el-menu-item>

          <el-menu-item index="/recording">
            <el-icon><Microphone /></el-icon>
            <template #title>录音管理</template>
          </el-menu-item>

          <el-menu-item index="/evaluation">
            <el-icon><Star /></el-icon>
            <template #title>面试评价</template>
          </el-menu-item>

          <el-menu-item index="/comparison">
            <el-icon><ScaleToOriginal /></el-icon>
            <template #title>候选人对比</template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Monitor, Expand, Fold, ArrowDown, House, OfficeBuilding,
  Document, Search, QuestionFilled, Microphone, Star,
  ScaleToOriginal, User, Setting, SwitchButton
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const isCollapse = ref(false)

// 默认头像
const defaultAvatar = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'

// 用户信息
const userInfo = ref({
  username: '',
  avatar: ''
})

// 当前激活的菜单
const activeMenu = computed(() => {
  return route.path
})

// 切换菜单折叠状态
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// 获取用户信息
const getUserInfo = () => {
  try {
    const userInfoStr = localStorage.getItem('user_info') || sessionStorage.getItem('user_info')
    if (userInfoStr) {
      const parsed = JSON.parse(userInfoStr)
      userInfo.value = {
        username: parsed.real_name || parsed.username || 'Admin',
        avatar: parsed.avatar || ''
      }
    } else {
      userInfo.value.username = 'Admin'
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    userInfo.value.username = 'Admin'
  }
}

// 处理下拉菜单命令
const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      // 清除token和用户信息
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      localStorage.removeItem('username')
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('user_info')
      sessionStorage.removeItem('username')

      ElMessage.success('已退出登录')
      router.push('/login')
    }).catch(() => {
      // 取消退出
    })
  } else if (command === 'profile') {
    ElMessage.info('个人信息页面开发中')
  } else if (command === 'settings') {
    ElMessage.info('系统设置页面开发中')
  }
}

onMounted(() => {
  getUserInfo()
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  width: 100%;
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px !important;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  cursor: pointer;
}

.system-name {
  font-size: 20px;
  font-weight: 600;
  color: #409EFF;
  white-space: nowrap;
}

.collapse-btn {
  cursor: pointer;
  color: #606266;
  margin-left: 20px;
  transition: all 0.3s;
  padding: 4px;
  border-radius: 4px;
}

.collapse-btn:hover {
  color: #409EFF;
  background-color: #f5f7fa;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  font-size: 14px;
  color: #303133;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-icon {
  font-size: 12px;
  color: #909399;
}

.sidebar {
  background-color: #001529;
  transition: width 0.3s;
  overflow-x: hidden;
}

.sidebar-menu {
  border-right: none;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

.sidebar-menu::-webkit-scrollbar {
  width: 6px;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.sidebar-menu :deep(.el-menu-item) {
  background-color: #001529;
  color: #bfcbd9;
  height: 50px;
  line-height: 50px;
  margin: 4px 0;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: #1890ff;
  color: #fff;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #409EFF;
  color: #fff;
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 60px);
}

/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
