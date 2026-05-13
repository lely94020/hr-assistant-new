<template>
  <div class="resume-detail-page">

    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/resume' }">简历管理</el-breadcrumb-item>
      <el-breadcrumb-item>简历详情</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 主布局：左右两栏 -->
    <el-row :gutter="20" v-loading="loading">
      <!-- 左侧：简历详细信息 -->
      <el-col :span="17">
        <!-- 卡片1：基本信息 -->
        <el-card class="info-card" shadow="never">
          <div class="base-header">
            <el-avatar :size="80" icon="UserFilled" class="avatar" />
            <div class="base-info">
              <h2 class="name">{{ resumeInfo.candidate_name || '未知' }}</h2>
              <p class="job">{{ resumeInfo.current_position || '未填写' }}</p>
            </div>
          </div>
          <el-descriptions :column="2" border class="descriptions">
            <el-descriptions-item label="手机号">
              {{ formatPhone(resumeInfo.phone) }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ resumeInfo.email || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="学历">{{ resumeInfo.education || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="工作年限">{{ resumeInfo.work_years || 0 }}年</el-descriptions-item>
            <el-descriptions-item label="毕业院校" :span="2">
              {{ resumeInfo.school || '未填写' }}
            </el-descriptions-item>
            <el-descriptions-item label="专业" :span="2">
              {{ resumeInfo.major || '未填写' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 卡片2：工作经历 -->
        <el-card class="info-card" shadow="never" title="工作经历" v-if="resumeInfo.work_experience && resumeInfo.work_experience.length">
          <el-timeline>
            <el-timeline-item
              v-for="(item, index) in resumeInfo.work_experience"
              :key="index"
              :timestamp="item.duration || ''"
            >
              <div class="work-title">{{ item.company }}</div>
              <div class="work-job">{{ item.position }}</div>
              <div class="work-desc">{{ item.description }}</div>
            </el-timeline-item>
          </el-timeline>
        </el-card>

        <!-- 卡片3：项目经验 -->
        <el-card class="info-card" shadow="never" title="项目经验" v-if="resumeInfo.project_experience && resumeInfo.project_experience.length">
          <el-collapse v-model="activeProject">
            <el-collapse-item
              v-for="(item, index) in resumeInfo.project_experience"
              :key="index"
              :title="item.name"
            >
              <div class="project-item">
                <p><strong>项目角色：</strong>{{ item.role }}</p>
                <p><strong>项目描述：</strong>{{ item.description }}</p>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-card>

        <!-- 卡片4：教育经历 -->
        <el-card class="info-card" shadow="never" title="教育经历" v-if="resumeInfo.education_experience && resumeInfo.education_experience.length">
          <div class="edu-list">
            <div
              class="edu-item"
              v-for="(item, index) in resumeInfo.education_experience"
              :key="index"
            >
              <span class="edu-school">{{ item.school }}</span>
              <span class="edu-major">{{ item.major }}</span>
              <span class="edu-degree">{{ item.degree }}</span>
              <span class="edu-time">{{ item.duration }}</span>
            </div>
          </div>
        </el-card>

        <!-- 卡片5：技能标签 -->
        <el-card class="info-card" shadow="never" title="技能特长" v-if="resumeInfo.skills && resumeInfo.skills.length">
          <el-tag
            v-for="(tag, index) in resumeInfo.skills"
            :key="index"
            type="primary"
            class="skill-tag"
            size="large"
          >
            {{ tag }}
          </el-tag>
        </el-card>
      </el-col>

      <!-- 右侧：操作面板 & AI分析 -->
      <el-col :span="7">
        <div class="right-sticky">
          <!-- 右侧卡片1：简历状态 -->
          <el-card shadow="never" class="right-card">
            <div class="status-header">
              <span>简历状态</span>
            </div>
            <div class="current-status">
              <el-tag
                :type="getStatusTagType(resumeInfo.status)"
                size="large"
                effect="light"
              >
                {{ getStatusText(resumeInfo.status) }}
              </el-tag>
            </div>
            <el-form :model="statusForm" label-width="80px" class="status-form">
              <el-form-item label="修改状态">
                <el-select v-model="statusForm.status" style="width: 100%">
                  <el-option
                    v-for="item in statusOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="关联岗位">
                <el-select v-model="statusForm.positionId" style="width: 100%">
                  <el-option
                    v-for="item in positionOptions"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  block
                  @click="saveStatus"
                  :loading="saving"
                >
                  保存状态
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 右侧卡片2：AI简历摘要 -->
          <el-card shadow="never" class="right-card" title="AI智能摘要" v-if="resumeInfo.resume_summary">
            <div class="ai-content">
              {{ resumeInfo.resume_summary }}
            </div>
          </el-card>

          <!-- 右侧卡片3：快捷操作 -->
          <el-card shadow="never" class="right-card" title="快捷操作">
            <div class="operate-btns">
              <el-button
                type="info"
                block
                @click="downloadResume"
                icon="Download"
              >
                下载原文件
              </el-button>
              <el-button
                type="danger"
                block
                @click="deleteResume"
                icon="Delete"
              >
                删除简历
              </el-button>
              <el-button
                block
                @click="goBack"
              >
                返回列表
              </el-button>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getResumeDetail, updateResumeStatus, bindPosition, deleteResume, downloadResume as downloadResumeApi } from '@/api/resume'
import { getPositionList } from '@/api/position'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const saving = ref(false)
const activeProject = ref([0])

// 状态选项
const statusOptions = [
  { label: '待筛选', value: 1 },
  { label: '初筛通过', value: 2 },
  { label: '面试中', value: 3 },
  { label: '已录用', value: 4 },
  { label: '已淘汰', value: 5 }
]

// 岗位选项
const positionOptions = ref([])

// 状态表单
const statusForm = reactive({
  status: 1,
  positionId: null
})

// 简历详情数据
const resumeInfo = ref({})

// 手机号脱敏
const formatPhone = (phone) => {
  if (!phone) return ''
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const map = {
    1: 'info',
    2: 'success',
    3: 'warning',
    4: 'success',
    5: 'danger'
  }
  return map[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const map = {
    1: '待筛选',
    2: '初筛通过',
    3: '面试中',
    4: '已录用',
    5: '已淘汰'
  }
  return map[status] || '未知'
}

// 加载岗位列表
const loadPositions = async () => {
  try {
    const res = await getPositionList({ page: 1, page_size: 100 })
    if (res.items) {
      positionOptions.value = res.items.map(item => ({
        id: item.id,
        name: item.name
      }))
    }
  } catch (error) {
    console.error('获取岗位列表失败:', error)
  }
}

// 加载简历详情
const loadResumeDetail = async () => {
  const resumeId = route.params.id
  if (!resumeId) {
    ElMessage.error('简历ID不存在')
    router.push('/resume')
    return
  }

  loading.value = true
  try {
    const res = await getResumeDetail(resumeId)
    resumeInfo.value = res

    // 初始化表单
    statusForm.status = res.status
    statusForm.positionId = res.position_id

    console.log('✅ 简历详情加载成功:', res)
  } catch (error) {
    console.error('获取简历详情失败:', error)
    ElMessage.error('获取简历详情失败')
  } finally {
    loading.value = false
  }
}

// 保存状态
const saveStatus = async () => {
  const resumeId = route.params.id

  saving.value = true
  try {
    // 更新状态
    if (statusForm.status !== resumeInfo.value.status) {
      await updateResumeStatus(resumeId, statusForm.status)
    }

    // 关联岗位
    if (statusForm.positionId !== resumeInfo.value.position_id) {
      await bindPosition(resumeId, statusForm.positionId)
    }

    ElMessage.success('状态保存成功')
    loadResumeDetail()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 下载简历
const downloadResume = async () => {
  try {
    const blob = await downloadResumeApi(route.params.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = resumeInfo.value.file_name || `${resumeInfo.value.candidate_name}_简历`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

// 删除简历
const deleteResumeItem = async () => {
  try {
    await ElMessageBox.confirm('确定删除该简历吗？删除后无法恢复', '提示', {
      type: 'warning'
    })

    await deleteResume(route.params.id)
    ElMessage.success('删除成功')
    router.push('/resume')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 返回
const goBack = () => {
  router.push('/resume')
}

// 初始化
onMounted(() => {
  console.log('📄 简历详情页 mounted')
  loadPositions()
  loadResumeDetail()
})
</script>

<style scoped>
.resume-detail-page {
  width: 100%;
}

/* 面包屑 */
.breadcrumb {
  margin-bottom: 16px;
}

/* 左侧卡片样式 */
.info-card {
  margin-bottom: 16px;
}

/* 基本信息头部 */
.base-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.avatar {
  background-color: #409eff;
}

.base-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.name {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.job {
  font-size: 16px;
  color: #606266;
  margin: 0;
}

/* 描述列表 */
.descriptions {
  margin-top: 10px;
}

/* 工作经历 */
.work-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.work-job {
  color: #606266;
  margin: 4px 0;
}

.work-desc {
  color: #909399;
  font-size: 14px;
}

/* 项目经验 */
.project-item {
  line-height: 1.8;
  color: #606266;
}

/* 教育经历 */
.edu-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.edu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.edu-school {
  font-weight: 600;
}

/* 技能标签 */
.skill-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

/* 右侧固定定位 */
.right-sticky {
  position: sticky;
  top: 20px;
}

.right-card {
  margin-bottom: 16px;
}

/* 状态卡片 */
.status-header {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.current-status {
  margin-bottom: 16px;
}

.status-form {
  margin-top: 10px;
}

/* AI摘要 */
.ai-content {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  color: #606266;
  line-height: 1.6;
  font-size: 14px;
}

/* 快捷操作按钮 */
.operate-btns {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
