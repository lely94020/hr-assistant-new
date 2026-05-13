<template>
  <el-container class="layout-container">
    <!-- 顶部导航栏 -->
    <el-header class="layout-header">
      <div class="header-left">
        <!-- 菜单折叠按钮 -->
        <el-button
          type="text"
          @click="collapsed = !collapsed"
          class="collapse-btn"
        >
          <el-icon :size="20">
            <component :is="collapsed ? Expand : Fold" />
          </el-icon>
        </el-button>

        <!-- Logo和系统名称 -->
        <div class="logo-section">
          <el-icon class="logo-icon" :size="28">
            <Service />
          </el-icon>
          <span class="system-name">企业HR智能助手</span>
        </div>
      </div>

      <!-- 右侧用户信息 -->
      <div class="header-right">
        <el-dropdown @command="handleUserCommand">
          <div class="user-info">
            <el-avatar :size="32" icon="User" />
            <span class="username">Admin</span>
            <el-icon><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                <span style="margin-left: 8px;">个人信息</span>
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon>
                <span style="margin-left: 8px;">退出登录</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <!-- 主体区域 -->
    <el-container>
      <!-- 左侧菜单栏 -->
      <el-aside
        :width="collapsed ? '64px' : '200px'"
        class="layout-aside"
      >
        <el-menu
          :default-active="$route.path"
          :collapse="collapsed"
          router
          class="sidebar-menu"
          background-color="#001529"
          text-color="#fff"
          active-text-color="#409EFF"
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
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  Expand, Fold, User, ArrowDown, SwitchButton,
  Service, House, OfficeBuilding, Document,
  Search, QuestionFilled, Microphone, Star,
  ScaleToOriginal
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const collapsed = ref(false)

// 用户下拉菜单事件处理
const handleUserCommand = (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人信息功能开发中')
      break
    case 'logout':
      ElMessage.success('已退出登录')
      router.push('/login')
      break
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

/* 顶部导航栏 */
.layout-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  color: #409EFF;
}

.system-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
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
  padding: 0 12px;
  height: 100%;
}

.username {
  font-size: 14px;
  color: #606266;
}

/* 左侧菜单栏 */
.layout-aside {
  height: calc(100vh - 60px);
  overflow: hidden;
}

.sidebar-menu {
  height: 100%;
  border-right: none;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #409EFF !important;
  color: #fff;
}

/* 主内容区 */
.layout-main {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>