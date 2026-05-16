<template>
  <div class="dashboard-container">
    <!-- 统计卡片区域 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover" @click="goToPosition">
          <div class="stat-content">
            <div class="stat-icon blue">
              <el-icon :size="32"><OfficeBuilding /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.positionCount }}</div>
              <div class="stat-label">开放岗位数</div>
              <div class="stat-change positive" v-if="stats.positionChange > 0">
                <el-icon><Top /></el-icon>
                <span>{{ stats.positionChange }}%</span>
              </div>
              <div class="stat-change negative" v-else-if="stats.positionChange < 0">
                <el-icon><Bottom /></el-icon>
                <span>{{ Math.abs(stats.positionChange) }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover" @click="goToResume">
          <div class="stat-content">
            <div class="stat-icon green">
              <el-icon :size="32"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ formatNumber(stats.resumeCount) }}</div>
              <div class="stat-label">简历总数</div>
              <div class="stat-change positive" v-if="stats.resumeChange > 0">
                <el-icon><Top /></el-icon>
                <span>{{ stats.resumeChange }}%</span>
              </div>
              <div class="stat-change negative" v-else-if="stats.resumeChange < 0">
                <el-icon><Bottom /></el-icon>
                <span>{{ Math.abs(stats.resumeChange) }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover" @click="goToScreening">
          <div class="stat-content">
            <div class="stat-icon orange">
              <el-icon :size="32"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.pendingCount }}</div>
              <div class="stat-label">待筛选简历</div>
              <div class="stat-change negative" v-if="stats.pendingChange > 0">
                <el-icon><Bottom /></el-icon>
                <span>{{ stats.pendingChange }}%</span>
              </div>
              <div class="stat-change positive" v-else-if="stats.pendingChange < 0">
                <el-icon><Top /></el-icon>
                <span>{{ Math.abs(stats.pendingChange) }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover" @click="goToInterview">
          <div class="stat-content">
            <div class="stat-icon purple">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.interviewCount }}</div>
              <div class="stat-label">面试中候选人</div>
              <div class="stat-change positive" v-if="stats.interviewChange > 0">
                <el-icon><Top /></el-icon>
                <span>{{ stats.interviewChange }}%</span>
              </div>
              <div class="stat-change negative" v-else-if="stats.interviewChange < 0">
                <el-icon><Bottom /></el-icon>
                <span>{{ Math.abs(stats.interviewChange) }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 操作按钮区域 -->
    <el-row class="action-row">
      <el-button type="primary" @click="refreshData" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
      <el-button type="success" @click="goToResumeUpload">
        <el-icon><Upload /></el-icon>
        上传简历
      </el-button>
      <el-button type="warning" @click="goToInterviewSchedule">
        <el-icon><Calendar /></el-icon>
        安排面试
      </el-button>
    </el-row>

    <!-- 中部两列布局 -->
    <el-row :gutter="16" class="content-row">
      <!-- 待办事项 -->
      <el-col :xs="24" :md="12">
        <el-card class="content-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">待办事项 ({{ unfinishedTodoCount }})</span>
              <div class="header-actions">
                <el-button
                  type="primary"
                  link
                  size="small"
                  @click="clearCompletedTodos"
                  :disabled="completedTodoCount === 0"
                >
                  清除已完成
                </el-button>
                <el-button type="primary" link size="small" @click="showAddTodoDialog">
                  <el-icon><Plus /></el-icon>
                  新增
                </el-button>
              </div>
            </div>
          </template>
          <el-scrollbar max-height="400px">
            <div class="todo-list">
              <div
                v-for="item in todoList"
                :key="item.id"
                class="todo-item"
                @click="handleTodoClick(item)"
              >
                <el-checkbox
                  v-model="item.completed"
                  @change="handleTodoComplete(item)"
                  @click.stop
                />
                <div class="todo-content">
                  <span class="todo-text" :class="{ completed: item.completed }">
                    {{ item.title }}
                  </span>
                  <el-tag :type="getTodoTagType(item)" size="small">
                    {{ getTodoTagText(item) }}
                  </el-tag>
                </div>
                <el-button
                  type="danger"
                  link
                  size="small"
                  @click.stop="deleteTodoItem(item.id)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
              <el-empty v-if="todoList.length === 0" description="暂无待办事项" />
            </div>
          </el-scrollbar>
        </el-card>
      </el-col>

      <!-- 最近面试安排 -->
      <el-col :xs="24" :md="12">
        <el-card class="content-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">最近面试安排</span>
              <el-button type="primary" link size="small" @click="goToInterviewPage">
                查看全部
              </el-button>
            </div>
          </template>
          <el-scrollbar max-height="400px">
            <el-timeline class="interview-timeline">
              <el-timeline-item
                v-for="interview in interviewList"
                :key="interview.id"
                :timestamp="interview.time"
                placement="top"
                :type="interview.type"
              >
                <div class="interview-item" @click="viewInterviewDetail(interview)">
                  <div class="interview-header">
                    <span class="interview-name">{{ interview.name }}</span>
                    <el-tag size="small" :type="getStatusType(interview.status)">
                      {{ getStatusText(interview.status) }}
                    </el-tag>
                  </div>
                  <span class="interview-position">{{ interview.position }}</span>
                </div>
              </el-timeline-item>
              <el-empty v-if="interviewList.length === 0" description="暂无面试安排" />
            </el-timeline>
          </el-scrollbar>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近动态 -->
    <el-row class="bottom-row">
      <el-col :span="24">
        <el-card class="content-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">最近动态</span>
              <el-button type="primary" link size="small">查看全部</el-button>
            </div>
          </template>
          <el-scrollbar max-height="300px">
            <div class="activity-list">
              <div
                v-for="activity in activityList"
                :key="activity.id"
                class="activity-item"
                @click="viewActivityDetail(activity)"
              >
                <div class="activity-icon">
                  <el-icon :size="18" :color="activity.color">
                    <component :is="getActivityIcon(activity.icon)" />
                  </el-icon>
                </div>
                <div class="activity-content">
                  <div class="activity-text">{{ activity.text }}</div>
                  <div class="activity-time">{{ activity.time }}</div>
                </div>
              </div>
              <el-empty v-if="activityList.length === 0" description="暂无动态" />
            </div>
          </el-scrollbar>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新增待办对话框 -->
    <el-dialog
      v-model="addTodoDialogVisible"
      title="新增待办事项"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="newTodoForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input
            v-model="newTodoForm.title"
            placeholder="请输入待办标题"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker
            v-model="newTodoForm.deadline"
            type="datetime"
            placeholder="选择截止时间"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="newTodoForm.priority" placeholder="请选择优先级" style="width: 100%">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addTodoDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitNewTodo" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  OfficeBuilding, Document, Clock, User, Top, Bottom,
  Check, Edit, Delete, Message, Refresh, Upload, Calendar, Plus
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getDashboardStats,
  getTodoList,
  createTodo,
  updateTodo,
  deleteTodo,
  clearCompletedTodos as apiClearCompletedTodos,
  getRecentInterviews,
  getRecentActivities
} from '@/api/dashboard'

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)

// 统计数据
const stats = ref({
  positionCount: 0,
  positionChange: 0,
  resumeCount: 0,
  resumeChange: 0,
  pendingCount: 0,
  pendingChange: 0,
  interviewCount: 0,
  interviewChange: 0
})

// 待办事项数据
const todoList = ref([])

// 面试安排数据
const interviewList = ref([])

// 最近动态数据
const activityList = ref([])

// 新增待办对话框
const addTodoDialogVisible = ref(false)
const newTodoForm = ref({
  title: '',
  deadline: null,
  priority: 'medium'
})

// 计算属性
const unfinishedTodoCount = computed(() => {
  return todoList.value.filter(item => !item.completed).length
})

const completedTodoCount = computed(() => {
  return todoList.value.filter(item => item.completed).length
})

// 格式化数字
const formatNumber = (num) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const res = await getDashboardStats()
    if (res.code === 0 && res.data) {
      stats.value = res.data
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  }
}

// 获取待办事项列表
const fetchTodoList = async () => {
  try {
    const res = await getTodoList({ page: 1, page_size: 10 })
    if (res.code === 0 && res.data) {
      todoList.value = res.data.items || []
    }
  } catch (error) {
    console.error('获取待办事项失败:', error)
  }
}

// 获取面试安排
const fetchInterviews = async () => {
  try {
    const res = await getRecentInterviews({ limit: 5 })
    if (res.code === 0 && res.data) {
      interviewList.value = res.data
    }
  } catch (error) {
    console.error('获取面试安排失败:', error)
  }
}

// 获取最近动态
const fetchActivities = async () => {
  try {
    const res = await getRecentActivities({ limit: 10 })
    if (res.code === 0 && res.data) {
      activityList.value = res.data
    }
  } catch (error) {
    console.error('获取最近动态失败:', error)
  }
}

// 刷新数据
const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchStats(),
      fetchTodoList(),
      fetchInterviews(),
      fetchActivities()
    ])
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  } finally {
    loading.value = false
  }
}

// 跳转到岗位管理
const goToPosition = () => {
  router.push('/position')
}

// 跳转到简历管理
const goToResume = () => {
  router.push('/resume')
}

// 跳转到智能筛选
const goToScreening = () => {
  router.push('/screening')
}

// 跳转到录音管理
const goToInterview = () => {
  router.push('/recording')
}

// 跳转到简历上传页面
const goToResumeUpload = () => {
  router.push('/resume/upload')
}

// 跳转到面试安排页面
const goToInterviewSchedule = () => {
  ElMessage.info('面试安排功能开发中')
}

// 跳转到面试管理页面
const goToInterviewPage = () => {
  router.push('/recording')
}

// 处理待办完成状态改变
const handleTodoComplete = async (item) => {
  try {
    await updateTodo(item.id, { completed: item.completed })
    ElMessage.success(item.completed ? '已标记为完成' : '已标记为未完成')
  } catch (error) {
    ElMessage.error('更新状态失败')
    item.completed = !item.completed
  }
}

// 点击待办事项
const handleTodoClick = (item) => {
  ElMessage.info(`查看待办详情: ${item.title}`)
}

// 删除待办事项
const deleteTodoItem = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条待办吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteTodo(id)
    const index = todoList.value.findIndex(item => item.id === id)
    if (index > -1) {
      todoList.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 清除已完成待办
const clearCompletedTodos = async () => {
  try {
    await ElMessageBox.confirm('确定要清除所有已完成的待办吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await apiClearCompletedTodos()
    todoList.value = todoList.value.filter(item => !item.completed)
    ElMessage.success('清除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清除失败')
    }
  }
}

// 显示新增待办对话框
const showAddTodoDialog = () => {
  newTodoForm.value = {
    title: '',
    deadline: null,
    priority: 'medium'
  }
  addTodoDialogVisible.value = true
}

// 提交新待办
const submitNewTodo = async () => {
  if (!newTodoForm.value.title) {
    ElMessage.warning('请输入待办标题')
    return
  }

  submitting.value = true
  try {
    const res = await createTodo(newTodoForm.value)
    if (res.code === 0) {
      ElMessage.success('添加成功')
      addTodoDialogVisible.value = false
      fetchTodoList()
    }
  } catch (error) {
    ElMessage.error('添加失败')
  } finally {
    submitting.value = false
  }
}

// 查看面试详情
const viewInterviewDetail = (interview) => {
  router.push(`/resume/detail/${interview.id}`)
}

// 查看动态详情
const viewActivityDetail = (activity) => {
  ElMessage.info(`查看动态详情: ${activity.text}`)
}

// 获取活动图标组件
const getActivityIcon = (iconName) => {
  const icons = {
    Check,
    Edit,
    Delete,
    Message
  }
  return icons[iconName] || Edit
}

// 获取待办标签类型
const getTodoTagType = (item) => {
  switch (item.priority) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return 'info'
  }
}

// 获取待办标签文本
const getTodoTagText = (item) => {
  switch (item.priority) {
    case 'high': return '高优先级'
    case 'medium': return '中优先级'
    case 'low': return '低优先级'
    default: return '普通'
  }
}

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    1: 'info',
    2: 'warning',
    3: 'primary',
    4: 'success',
    5: 'danger'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    1: '待筛选',
    2: '初筛通过',
    3: '面试中',
    4: '已录用',
    5: '已淘汰'
  }
  return texts[status] || '未知'
}

// 组件挂载时获取数据
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.dashboard-container {
  width: 100%;
  padding-bottom: 20px;
}

.stats-row {
  margin-bottom: 16px;
}

.action-row {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
}

.stat-card {
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
  border-radius: 8px;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.stat-icon.blue {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
}

.stat-icon.green {
  background: linear-gradient(135deg, #67C23A, #85ce61);
}

.stat-icon.orange {
  background: linear-gradient(135deg, #E6A23C, #ebb563);
}

.stat-icon.purple {
  background: linear-gradient(135deg, #909399, #a6a9ad);
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 6px;
}

.stat-change {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 2px;
}

.stat-change.positive {
  color: #67C23A;
}

.stat-change.negative {
  color: #F56C6C;
}

.content-row {
  margin-bottom: 16px;
}

.content-card {
  height: 100%;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.todo-list {
  padding: 8px 0;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f2f5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.todo-item:last-child {
  border-bottom: none;
}

.todo-item:hover {
  background-color: #f5f7fa;
}

.todo-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  min-width: 0;
}

.todo-text {
  flex: 1;
  font-size: 14px;
  color: #303133;
  transition: color 0.3s;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.todo-text:hover {
  color: #409EFF;
}

.todo-text.completed {
  text-decoration: line-through;
  color: #909399;
}

.interview-timeline {
  padding: 16px 0;
}

.interview-item {
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.interview-item:hover {
  background-color: #f5f7fa;
}

.interview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 4px;
}

.interview-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.interview-position {
  font-size: 12px;
  color: #909399;
}

.bottom-row {
  width: 100%;
}

.activity-list {
  padding: 8px 0;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f2f5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-item:hover {
  background-color: #f5f7fa;
}

.activity-icon {
  margin-top: 2px;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-text {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
  transition: color 0.3s;
}

.activity-item:hover .activity-text {
  color: #409EFF;
}

.activity-time {
  font-size: 12px;
  color: #909399;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .stat-number {
    font-size: 24px;
  }

  .stat-icon {
    width: 48px;
    height: 48px;
  }

  .action-row {
    flex-wrap: wrap;
  }
}
</style>
