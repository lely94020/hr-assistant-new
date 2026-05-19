<template>
  <div class="interview-summary-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item>面试管理</el-breadcrumb-item>
      <el-breadcrumb-item>面试录音</el-breadcrumb-item>
      <el-breadcrumb-item>面试摘要</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 1. 顶部信息栏卡片 -->
    <el-card class="top-info-card" shadow="never" v-loading="loading">
      <div class="left-info">
        <h1 class="candidate-name">{{ summaryInfo.candidateName }}</h1>
        <el-tag type="primary" size="large" class="position-tag">
          {{ summaryInfo.positionName }}
        </el-tag>
      </div>
      <div class="right-info">
        <div class="info-item">
          <span class="label">面试时间：</span>
          <span class="value">{{ summaryInfo.interviewDate }}</span>
        </div>
        <div class="info-item">
          <span class="label">面试官：</span>
          <span class="value">{{ summaryInfo.interviewer }}</span>
        </div>
        <div class="info-item">
          <span class="label">时长：</span>
          <span class="value">{{ summaryInfo.duration }}</span>
        </div>
      </div>
    </el-card>

    <!-- 2. 主内容区卡片列表 -->
    <div class="content-wrapper" v-loading="loading">
      <!-- 卡片1：面试概要 -->
      <el-card class="content-card" shadow="never">
        <div class="card-header">
          <h3>面试概要</h3>
          <el-button
            icon="Edit"
            link
            @click="openEdit('summary')"
            :disabled="editMode"
          >
            编辑
          </el-button>
        </div>
        <!-- 查看模式 -->
        <div
          v-if="!editMode"
          class="summary-content"
        >
          {{ summaryInfo.summary }}
        </div>
        <!-- 编辑模式 -->
        <div v-else-if="editTarget === 'summary'" class="edit-box">
          <el-input
            v-model="editSummary"
            type="textarea"
            :rows="5"
            class="summary-input"
          />
          <div class="edit-buttons">
            <el-button size="small" @click="cancelEdit">取消</el-button>
            <el-button size="small" type="primary" @click="saveSummary" :loading="saving">保存</el-button>
          </div>
        </div>
      </el-card>

      <!-- 卡片2：核心问答 -->
      <el-card class="content-card" shadow="never">
        <div class="card-header">
          <h3>核心问答</h3>
        </div>
        <el-collapse v-model="activeCollapse">
          <el-collapse-item
            v-for="(item, index) in summaryInfo.qaList"
            :key="index"
            :name="index"
          >
            <template #title>
              <span class="question">Q: {{ item.question }}</span>
            </template>
            <div class="answer-box">
              <p class="answer">A: {{ item.answer_summary }}</p>
              <div class="quality">
                <span>回答质量：</span>
                <el-tag :type="getQualityTagType(item.answer_quality)" size="small">
                  {{ item.answer_quality }}
                </el-tag>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
        <el-empty v-if="summaryInfo.qaList.length === 0" description="暂无核心问答" />
      </el-card>

      <!-- 卡片3：能力标签 -->
      <el-card class="content-card" shadow="never">
        <div class="card-header">
          <h3>能力标签</h3>
        </div>
        <div class="skill-tags">
          <div class="tag-group">
            <span class="group-title">技术能力：</span>
            <el-tag
              v-for="tag in summaryInfo.techSkills"
              :key="tag"
              type="primary"
              class="mr-8 mt-8"
            >
              {{ tag }}
            </el-tag>
            <span v-if="summaryInfo.techSkills.length === 0" class="empty-text">暂无数据</span>
          </div>
          <div class="tag-group mt-16">
            <span class="group-title">软技能：</span>
            <el-tag
              v-for="tag in summaryInfo.softSkills"
              :key="tag"
              type="success"
              class="mr-8 mt-8"
            >
              {{ tag }}
            </el-tag>
            <span v-if="summaryInfo.softSkills.length === 0" class="empty-text">暂无数据</span>
          </div>
        </div>
      </el-card>

      <!-- 卡片4：亮点与疑虑 -->
      <el-card class="content-card" shadow="never">
        <div class="card-header">
          <h3>亮点与疑虑</h3>
        </div>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="advantage-box">
              <div class="box-title">
                <el-icon color="#67c23a" size="18"><Check /></el-icon>
                <span>亮点</span>
              </div>
              <ul class="list" v-if="summaryInfo.advantages.length > 0">
                <li v-for="(item, index) in summaryInfo.advantages" :key="index">
                  <el-icon color="#67c23a" size="14" class="mr-8"><Check /></el-icon>
                  {{ item }}
                </li>
              </ul>
              <el-empty v-else description="暂无亮点" :image-size="60" />
            </div>
          </el-col>
          <el-col :span="12">
            <div class="concern-box">
              <div class="box-title">
                <el-icon color="#e6a23c" size="18"><Warning /></el-icon>
                <span>疑虑点</span>
              </div>
              <ul class="list" v-if="summaryInfo.concerns.length > 0">
                <li v-for="(item, index) in summaryInfo.concerns" :key="index">
                  <el-icon color="#e6a23c" size="14" class="mr-8"><Warning /></el-icon>
                  {{ item }}
                </li>
              </ul>
              <el-empty v-else description="暂无疑虑" :image-size="60" />
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 卡片5：候选人提问 -->
      <el-card class="content-card" shadow="never">
        <div class="card-header">
          <h3>候选人提问</h3>
        </div>
        <div class="question-list" v-if="summaryInfo.questions.length > 0">
          <div
            v-for="(item, index) in summaryInfo.questions"
            :key="index"
            class="question-item"
          >
            {{ index + 1 }}. {{ item }}
          </div>
        </div>
        <el-empty v-else description="候选人未提问" />
      </el-card>
    </div>

    <!-- 3. 右侧悬浮操作栏 -->
    <div class="float-operate">
      <el-card shadow="never" class="float-card">
        <div class="btn-group">
          <el-button block @click="regenerateSummary" :loading="regenerating">重新生成摘要</el-button>
          <el-button block type="primary" class="mt-8" @click="goToEvaluation">生成评价</el-button>
          <el-button block class="mt-8" @click="goBackRecord">返回录音</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Edit,
  Check,
  Warning
} from '@element-plus/icons-vue'
import {
  getSummaryByRecordingId,
  updateSummary,
  regenerateSummary as regenerateSummaryApi
} from '@/api/summary'
import { generateEvaluation } from '@/api/evaluation'
import { getRecordingDetail } from '@/api/recording'
import { getResumeDetail } from '@/api/resume'

const route = useRoute()
const router = useRouter()

// 加载状态
const loading = ref(false)
const saving = ref(false)
const regenerating = ref(false)

// 编辑状态
const editMode = ref(false)
const editTarget = ref('')
const editSummary = ref('')
const activeCollapse = ref([0])

// 摘要ID（用于更新）
const summaryId = ref(null)

// 面试摘要数据
const summaryInfo = reactive({
  candidateName: '-',
  positionName: '-',
  interviewDate: '-',
  interviewer: '-',
  duration: '-',
  summary: '',
  qaList: [],
  techSkills: [],
  softSkills: [],
  advantages: [],
  concerns: [],
  questions: []
})

// 获取质量标签类型
const getQualityTagType = (quality) => {
  const typeMap = {
    '优秀': 'success',
    '良好': 'primary',
    '一般': 'info',
    '较差': 'danger'
  }
  return typeMap[quality] || 'info'
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 格式化时长
const formatDuration = (seconds) => {
  if (!seconds) return '-'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

// 加载摘要数据
const loadSummary = async () => {
  const recordingId = route.params.recordingId || route.query.recordingId

  if (!recordingId) {
    ElMessage.error('缺少录音ID参数')
    return
  }

  loading.value = true
  try {
    // 获取录音详情
    const recordingRes = await getRecordingDetail(recordingId)

    // 填充录音信息
    if (recordingRes) {
      // 格式化面试时间
      summaryInfo.interviewDate = recordingRes.interview_date
        ? formatDate(recordingRes.interview_date)
        : '-'

      // 面试官
      summaryInfo.interviewer = recordingRes.interviewer || '-'

      // 格式化时长
      summaryInfo.duration = formatDuration(recordingRes.duration)

      // 获取简历信息（如果有resume_id）
      if (recordingRes.resume_id) {
        try {
          const resumeRes = await getResumeDetail(recordingRes.resume_id)
          if (resumeRes) {
            summaryInfo.candidateName = resumeRes.candidate_name || '-'
          }
        } catch (error) {
          console.error('获取简历信息失败:', error)
        }
      }

      // 获取岗位信息（如果有position_id）
      if (recordingRes.position_id) {
        // 这里可以调用获取岗位详情的API
        // 暂时显示岗位ID
        summaryInfo.positionName = `岗位ID: ${recordingRes.position_id}`
      }
    }

    // 获取摘要信息
    const summaryRes = await getSummaryByRecordingId(recordingId).catch(() => null)

    // 填充摘要信息
    if (summaryRes) {
      summaryId.value = summaryRes.id
      summaryInfo.summary = summaryRes.summary_overview || ''
      summaryInfo.qaList = summaryRes.key_qa || []
      summaryInfo.techSkills = summaryRes.technical_skills || []
      summaryInfo.softSkills = summaryRes.soft_skills || []

      // 将字符串转换为数组（后端存储为换行分隔的字符串）
      summaryInfo.advantages = summaryRes.highlights
        ? summaryRes.highlights.split('\n').filter(item => item.trim())
        : []
      summaryInfo.concerns = summaryRes.concerns
        ? summaryRes.concerns.split('\n').filter(item => item.trim())
        : []
      summaryInfo.questions = summaryRes.candidate_questions
        ? summaryRes.candidate_questions.split('\n').filter(item => item.trim())
        : []
    } else {
      ElMessage.warning('尚未生成面试摘要，请点击"重新生成摘要"')
    }
  } catch (error) {
    console.error('加载摘要失败:', error)
    ElMessage.error('加载摘要失败')
  } finally {
    loading.value = false
  }
}

// 打开编辑
const openEdit = (target) => {
  editMode.value = true
  editTarget.value = target
  editSummary.value = summaryInfo.summary
}

// 取消编辑
const cancelEdit = () => {
  editMode.value = false
  editTarget.value = ''
}

// 保存概要
const saveSummary = async () => {
  if (!summaryId.value) {
    ElMessage.error('摘要ID不存在')
    return
  }

  saving.value = true
  try {
    await updateSummary(summaryId.value, {
      summary_overview: editSummary.value
    })

    summaryInfo.summary = editSummary.value
    editMode.value = false
    editTarget.value = ''
    ElMessage.success('概要保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 重新生成摘要
const regenerateSummary = async () => {
  const recordingId = route.params.recordingId || route.query.recordingId

  if (!recordingId) {
    ElMessage.error('缺少录音ID参数')
    return
  }

  regenerating.value = true
  try {
    const res = await regenerateSummaryApi(summaryId.value || recordingId)

    // 更新本地数据
    summaryId.value = res.id
    summaryInfo.summary = res.summary_overview || ''
    summaryInfo.qaList = res.key_qa || []
    summaryInfo.techSkills = res.technical_skills || []
    summaryInfo.softSkills = res.soft_skills || []
    summaryInfo.advantages = res.highlights
      ? res.highlights.split('\n').filter(item => item.trim())
      : []
    summaryInfo.concerns = res.concerns
      ? res.concerns.split('\n').filter(item => item.trim())
      : []
    summaryInfo.questions = res.candidate_questions
      ? res.candidate_questions.split('\n').filter(item => item.trim())
      : []

    ElMessage.success('摘要重新生成成功')
  } catch (error) {
    console.error('重新生成失败:', error)
    ElMessage.error('重新生成摘要失败')
  } finally {
    regenerating.value = false
  }
}

// 生成并跳转到评价页面
const goToEvaluation = async () => {
  if (!summaryId.value) {
    ElMessage.warning('请先生成面试摘要')
    return
  }
  try {
    const res = await generateEvaluation(summaryId.value)
    ElMessage.success('评价生成成功')
    router.push(`/evaluation/detail/${res.id}`)
  } catch (error) {
    console.error('生成评价失败:', error)
    ElMessage.error('生成评价失败，请重试')
  }
}

// 返回录音页面
const goBackRecord = () => {
  router.back()
}

// 组件挂载时加载数据
onMounted(() => {
  loadSummary()
})
</script>

<style scoped>
.interview-summary-page {
  width: 100%;
  position: relative;
  padding-bottom: 20px;
}

/* 面包屑 */
.breadcrumb {
  margin-bottom: 16px;
}

/* 顶部信息卡片 */
.top-info-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  margin-bottom: 20px;
}

.left-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.candidate-name {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.position-tag {
  height: 32px;
  line-height: 32px;
}

.right-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  font-size: 14px;
  display: flex;
  align-items: center;
}

.info-item .label {
  color: #606266;
  min-width: 70px;
}

.info-item .value {
  color: #303133;
  font-weight: 500;
}

/* 主内容区 */
.content-wrapper {
  width: calc(100% - 200px); /* 预留右侧悬浮栏位置 */
}

/* 内容卡片通用样式 */
.content-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 面试概要 */
.summary-content {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  line-height: 1.8;
  color: #303133;
  font-size: 14px;
}

.edit-box {
  margin-top: 8px;
}

.summary-input {
  margin-bottom: 12px;
}

.edit-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

/* 核心问答 */
.question {
  font-size: 15px;
  font-weight: bold;
  color: #303133;
}

.answer-box {
  padding: 8px 0;
}

.answer {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 8px 0;
}

.quality {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

/* 能力标签 */
.skill-tags {
  margin-top: 8px;
}

.tag-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.group-title {
  font-weight: 500;
  color: #303133;
  margin-right: 12px;
}

.empty-text {
  color: #909399;
  font-size: 14px;
}

/* 亮点与疑虑 */
.advantage-box, .concern-box {
  padding: 8px 0;
}

.box-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list li {
  display: flex;
  align-items: center;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 8px;
}

/* 候选人提问 */
.question-list {
  margin-top: 8px;
}

.question-item {
  line-height: 1.8;
  color: #606266;
  margin-bottom: 8px;
}

.empty-tip {
  color: #909399;
  font-size: 14px;
  padding: 10px 0;
}

/* 右侧悬浮操作栏 */
.float-operate {
  position: fixed;
  top: 120px;
  right: 20px;
  width: 160px;
  z-index: 10;
}

.float-card {
  padding: 16px;
}

.btn-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 通用间距类 */
.mt-8 { margin-top: 8px; }
.mt-16 { margin-top: 16px; }
.mr-8 { margin-right: 8px; }
</style>
