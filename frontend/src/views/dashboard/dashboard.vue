<template>
  <div class="dashboard-container">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon blue">
              <el-icon :size="24"><OfficeBuilding /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">开放岗位数</div>
              <div class="stat-number">{{ stats.openPositions }}</div>
              <div class="stat-change positive">
                <el-icon><ArrowUp /></el-icon>
                <span>{{ stats.openPositionsRate }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon green">
              <el-icon :size="24"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">简历总数</div>
              <div class="stat-number">{{ stats.totalResumes }}</div>
              <div class="stat-change positive">
                <el-icon><ArrowUp /></el-icon>
                <span>{{ stats.totalResumesRate }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon orange">
              <el-icon :size="24"><Search /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">待筛选简历</div>
              <div class="stat-number">{{ stats.pendingScreening }}</div>
              <div class="stat-change negative">
                <el-icon><ArrowDown /></el-icon>
                <span>{{ stats.pendingScreeningRate }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon purple">
              <el-icon :size="24"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">面试中候选人</div>
              <div class="stat-number">{{ stats.interviewing }}</div>
              <div class="stat-change positive">
                <el-icon><ArrowUp /></el-icon>
                <span>{{ stats.interviewingRate }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 中部两列布局 -->
    <el-row :gutter="16" class="middle-row">
      <!-- 待办事项 -->
      <el-col :span="12">
        <el-card class="todo-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">待办事项</span>
              <el-button type="text" size="small">查看全部</el-button>
            </div>
          </template>
          <el-list :data="todoList">
            <template #default="{ item }">
              <el-list-item class="todo-item">
                <div class="todo-content">
                  <el-icon class="todo-icon" :color="item.completed ? '#67C23A' : '#409EFF'">
                    <component :is="item.completed ? 'CircleCheck' : 'Circle'" />
                  </el-icon>
                  <span :class="{ completed: item.completed }">{{ item.text }}</span>
                </div>
                <el-button
                  type="text"
                  size="small"
                  :disabled="item.completed"
                  @click="completeTodo(item)"
                >
                  完成
                </el-button>
              </el-list-item>
            </template>
          </el-list>
        </el-card>
      </el-col>

      <!-- 最近面试安排 -->
      <el-col :span="12">
        <el-card class="interview-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">最近面试安排</span>
              <el-button type="text" size="small">查看全部</el-button>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="item in interviewList"
              :key="item.id"
              :timestamp="item.time"
              placement="top"
            >
              <div class="interview-item">
                <div class="interview-name">{{ item.name }}</div>
                <div class="interview-position">{{ item.position }}</div>
                <div class="interview-status" :class="item.status">
                  {{ getStatusText(item.status) }}
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部最近动态 -->
    <el-row class="bottom-row">
      <el-col :span="24">
        <el-card class="activity-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">最近动态</span>
              <el-button type="text" size="small">查看全部</el-button>
            </div>
          </template>
          <el-table :data="activityList" style="width: 100%">
            <el-table-column prop="user" label="用户" width="100" />
            <el-table-column prop="action" label="操作" />
            <el-table-column prop="target" label="对象" width="150" />
            <el-table-column prop="time" label="时间" width="150" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  OfficeBuilding, Document, Search, User,
  ArrowUp, ArrowDown, Circle, CircleCheck
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 统计数据
const stats = ref({
  openPositions: 28,
  openPositionsRate: 12.5,
  totalResumes: 1256,
  totalResumesRate: 8.3,
  pendingScreening: 156,
  pendingScreeningRate: 5.2,
  interviewing: 32,
  interviewingRate: 18.7
})

// 待办事项列表
const todoList = ref([
  { id: 1, text: '完成岗位A的面试安排', completed: false },
  { id: 2, text: '审核候选人简历', completed: false },
  { id: 3, text: '更新面试题库', completed: true },
  { id: 4, text: '发送面试邀请', completed: false },
  { id: 5, text: '整理面试记录', completed: false }
])

// 面试安排列表
const interviewList = ref([
  { id: 1, name: '张三', position: '前端工程师', time: '10:00', status: 'pending' },
  { id: 2, name: '李四', position: '后端开发', time: '14:00', status: 'ongoing' },
  { id: 3, name: '王五', position: '产品经理', time: '16:30', status: 'completed' },
  { id: 4, name: '赵六', position: '测试工程师', time: '明天 09:30', status: 'pending' }
])

// 最近动态列表
const activityList = ref([
  { user: 'Admin', action: '创建了新岗位', target: '后端开发', time: '10分钟前' },
  { user: 'HR1', action: '审核了简历', target: '候选人-张三', time: '30分钟前' },
  { user: 'Admin', action: '安排了面试', target: '李四-前端工程师', time: '1小时前' },
  { user: 'HR2', action: '更新了面试题库', target: 'JavaScript题目', time: '2小时前' }
])

// 完成待办事项
const completeTodo = (item) => {
  item.completed = true
  ElMessage.success('任务已完成')
}

// 获取面试状态文本
const getStatusText = (status) => {
  const statusMap = {
    pending: '待面试',
    ongoing: '进行中',
    completed: '已完成'
  }
  return statusMap[status] || status
}
</script>

<style scoped>
.dashboard-container {
  width: 100%;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-icon.blue {
  background-color: #409EFF;
}

.stat-icon.green {
  background-color: #67C23A;
}

.stat-icon.orange {
  background-color: #E6A23C;
}

.stat-icon.purple {
  background-color: #909399;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stat-change {
  display: flex;
  align-items: center;
  font-size: 12px;
}

.stat-change.positive {
  color: #67C23A;
}

.stat-change.negative {
  color: #F56C6C;
}

/* 中部布局 */
.middle-row {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 待办事项 */
.todo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.todo-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.todo-icon {
  font-size: 18px;
}

.todo-item .completed {
  color: #909399;
  text-decoration: line-through;
}

/* 面试安排 */
.interview-item {
  padding: 8px 0;
}

.interview-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.interview-position {
  font-size: 12px;
  color: #909399;
  margin: 4px 0;
}

.interview-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.interview-status.pending {
  background-color: #ecf5ff;
  color: #409EFF;
}

.interview-status.ongoing {
  background-color: #fdf6ec;
  color: #E6A23C;
}

.interview-status.completed {
  background-color: #f0f9eb;
  color: #67C23A;
}

/* 最近动态 */
.activity-card {
  margin-top: 16px;
}
</style>