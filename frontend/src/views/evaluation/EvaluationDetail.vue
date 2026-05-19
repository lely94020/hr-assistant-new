<template>
  <div class="interview-evaluate-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item>面试管理</el-breadcrumb-item>
      <el-breadcrumb-item>面试评价</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 主布局：左右结构 -->
    <el-row :gutter="20" class="main-row">
      <!-- 左侧：评分区域（sticky 固定） -->
      <el-col :span="10">
        <el-card class="left-card" shadow="never">
          <!-- 1. 候选人信息 -->
          <div class="candidate-info">
            <h2 class="name">{{ candidateInfo.name }}</h2>
            <el-tag type="primary" class="position-tag">{{ candidateInfo.position }}</el-tag>
            <div class="date">面试日期：{{ candidateInfo.date }}</div>
          </div>

          <!-- 2. 综合得分环形进度条 -->
          <div class="total-score">
            <el-progress
              type="circle"
              :percentage="totalScore"
              :width="150"
              :color="getScoreColor(totalScore)"
            >
              <!-- 圆环内自定义分数 -->
              <div class="inner-score">{{ totalScore }}</div>
            </el-progress>
            <!-- 推荐等级标签 -->
            <el-tag
              :type="getLevelInfo.type"
              size="large"
              class="level-tag mt-15"
            >
              {{ getLevelInfo.text }}
            </el-tag>
          </div>

          <!-- 3. 各维度评分 -->
          <div class="dimension-scores mt-25">
            <h3 class="card-title">维度评分</h3>
            <div
              v-for="item in dimensionList"
              :key="item.name"
              class="dimension-item"
            >
              <div class="label">
                {{ item.name }} <span class="weight">({{ item.weight }})</span>
              </div>
              <el-progress
                :percentage="item.score"
                :color="getScoreColor(item.score)"
                stroke-width="8"
                class="progress"
              />
              <div class="score" :style="{ color: getScoreColor(item.score) }">
                {{ item.score }}
              </div>
            </div>
          </div>

          <!-- 4. ECharts 雷达图 -->
          <div class="radar-chart mt-25">
            <h3 class="card-title">能力维度雷达图</h3>
            <div ref="radarRef" class="chart-box"></div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：评价详情 -->
      <el-col :span="14">
        <!-- 卡片1：AI综合评语 -->
        <el-card class="right-card" shadow="never" title="AI综合评语">
          <div class="comment-content">{{ evaluateInfo.aiComment }}</div>
        </el-card>

        <!-- 卡片2：各维度详细评价 -->
        <el-card class="right-card" shadow="never" title="各维度详细评价">
          <el-collapse v-model="activeCollapse">
            <el-collapse-item
              v-for="(item, index) in dimensionList"
              :key="item.name"
              :title="`${item.name} · ${item.score}分`"
              :name="index"
            >
              <div class="detail-text">{{ item.detail }}</div>
            </el-collapse-item>
          </el-collapse>
        </el-card>

        <!-- 卡片3：核心优势 & 待提升 -->
        <el-card class="right-card" shadow="never" title="核心优势与待提升">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="advantage-box">
                <h4 class="box-title success">
                  <el-icon><Check /></el-icon>核心优势
                </h4>
                <ul class="list">
                  <li v-for="(item, index) in evaluateInfo.advantages" :key="index">
                    {{ item }}
                  </li>
                </ul>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="concern-box">
                <h4 class="box-title warning">
                  <el-icon><Warning /></el-icon>待提升领域
                </h4>
                <ul class="list">
                  <li v-for="(item, index) in evaluateInfo.concerns" :key="index">
                    {{ item }}
                  </li>
                </ul>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 卡片4：HR补充评价 -->
        <el-card class="right-card" shadow="never" title="HR补充评价">
          <el-input
            v-model="hrComment"
            type="textarea"
            :rows="4"
            placeholder="请输入HR补充评价..."
            class="mb-10"
          />
          <el-button type="primary" @click="saveHrComment">保存评价</el-button>
        </el-card>

        <!-- 卡片5：录用建议 -->
        <el-card class="right-card" shadow="never" title="录用建议">
          <div class="suggestion-box">{{ evaluateInfo.suggestion }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部固定操作栏 -->
    <div class="bottom-operate">
      <el-card shadow="never" class="operate-card">
        <div class="btn-group">
          <el-button type="success" size="large" :loading="statusUpdating" @click="handleUpdateStatus(4)">通过录用</el-button>
          <el-button type="warning" size="large" :loading="statusUpdating" @click="handleUpdateStatus(3)">进入待定</el-button>
          <el-button type="danger" size="large" :loading="statusUpdating" @click="handleUpdateStatus(5)">不予录用</el-button>
          <el-button type="primary" size="large" class="ml-20" @click="handleExport">导出评价报告</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { Check, Warning } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import {
  generateEvaluation,
  getLatestEvaluation,
  getEvaluationDetail,
  updateHrComment
} from '@/api/evaluation'
import { updateResumeStatus } from '@/api/resume'

const route = useRoute()
const router = useRouter()

// 候选人基础信息
const candidateInfo = reactive({
  name: '',
  position: '',
  date: ''
})

// 综合得分
const totalScore = ref(0)
// 折叠面板激活项
const activeCollapse = ref([0])
// HR补充评价
const hrComment = ref('')
// 当前评价ID
const currentEvaluationId = ref(null)
// 当前简历ID（用于底部操作更新状态）
const currentResumeId = ref(null)
// 状态更新中
const statusUpdating = ref(false)
// 加载状态
const loading = ref(false)
// 雷达图 DOM 引用
const radarRef = ref(null)
let radarChart = null

// 维度评分列表（权重+分数+详情）
const dimensionList = reactive([
  { name: '专业能力', weight: '30%', score: 0, detail: '' },
  { name: '逻辑思维', weight: '20%', score: 0, detail: '' },
  { name: '沟通表达', weight: '15%', score: 0, detail: '' },
  { name: '学习能力', weight: '15%', score: 0, detail: '' },
  { name: '团队协作', weight: '10%', score: 0, detail: '' },
  { name: '文化匹配', weight: '10%', score: 0, detail: '' }
])

// 评价详情数据
const evaluateInfo = reactive({
  aiComment: '',
  advantages: [],
  concerns: [],
  suggestion: ''
})

// ==================== 工具方法 ====================
// 获取分数对应颜色
const getScoreColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 75) return '#409eff'
  if (score >= 60) return '#909399'
  return '#f56c6c'
}

// 获取推荐等级信息
const getLevelInfo = reactive({
  type: '',
  text: ''
})
const setLevelInfo = () => {
  const score = totalScore.value
  if (score >= 90) {
    getLevelInfo.type = 'success'
    getLevelInfo.text = '强烈推荐'
  } else if (score >= 75) {
    getLevelInfo.type = 'primary'
    getLevelInfo.text = '推荐'
  } else if (score >= 60) {
    getLevelInfo.type = 'info'
    getLevelInfo.text = '可考虑'
  } else {
    getLevelInfo.type = 'danger'
    getLevelInfo.text = '不推荐'
  }
}

// 保存HR评价
const saveHrComment = async () => {
  if (!currentEvaluationId.value) {
    ElMessage.warning('暂无评价数据')
    return
  }

  if (!hrComment.value.trim()) {
    ElMessage.warning('请输入HR补充评价')
    return
  }

  try {
    await updateHrComment(currentEvaluationId.value, hrComment.value)
    ElMessage.success('HR补充评价保存成功！')
  } catch (error) {
    console.error('保存HR评价失败:', error)
    ElMessage.error('保存失败，请重试')
  }
}

// 填充评价数据到视图
const fillEvaluationData = (data) => {
  // 填充候选人信息
  if (data.candidate_info) {
    candidateInfo.name = data.candidate_info.name || '未知'
    candidateInfo.position = data.candidate_info.position || '未知岗位'
  }
  if (data.created_at) {
    const date = new Date(data.created_at)
    candidateInfo.date = date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // 填充评价数据
  currentEvaluationId.value = data.id
  currentResumeId.value = data.resume_id
  totalScore.value = data.total_score

  // 填充各维度评分
  dimensionList[0].score = data.scores.professional.score
  dimensionList[0].detail = data.scores.professional.comment || ''

  dimensionList[1].score = data.scores.logic.score
  dimensionList[1].detail = data.scores.logic.comment || ''

  dimensionList[2].score = data.scores.communication.score
  dimensionList[2].detail = data.scores.communication.comment || ''

  dimensionList[3].score = data.scores.learning.score
  dimensionList[3].detail = data.scores.learning.comment || ''

  dimensionList[4].score = data.scores.teamwork.score
  dimensionList[4].detail = data.scores.teamwork.comment || ''

  dimensionList[5].score = data.scores.culture_fit.score
  dimensionList[5].detail = data.scores.culture_fit.comment || ''

  // 填充评价详情
  evaluateInfo.aiComment = data.ai_comment || '暂无AI评语'
  evaluateInfo.advantages = data.key_strengths || []
  evaluateInfo.concerns = data.improvement_areas || []
  evaluateInfo.suggestion = data.hiring_suggestion || '暂无录用建议'

  // HR补充评价
  hrComment.value = data.hr_comment || ''

  // 设置推荐等级
  setLevelInfo()

  // 初始化雷达图
  nextTick(() => initRadarChart())
}

// 加载评价数据（通过简历ID获取最新评价）
const loadEvaluation = async (resumeId) => {
  loading.value = true
  try {
    const response = await getLatestEvaluation(resumeId)
    fillEvaluationData(response)
  } catch (error) {
    console.error('加载评价失败:', error)
    ElMessage.error('加载评价数据失败')
  } finally {
    loading.value = false
  }
}

// 生成评价
const handleGenerateEvaluation = async (summaryId) => {
  const hideLoading = ElLoading.service({
    lock: true,
    text: '正在生成面试评价...',
    background: 'rgba(0, 0, 0, 0.7)'
  })

  try {
    const response = await generateEvaluation(summaryId)

    ElMessage.success('评价生成成功！')

    // 重新加载评价数据
    await loadEvaluation(response.resume_id)

  } catch (error) {
    console.error('生成评价失败:', error)
    ElMessage.error('生成评价失败，请重试')
  } finally {
    hideLoading.close()
  }
}

// ==================== 底部操作 ====================
// 更新候选人状态
const handleUpdateStatus = async (status) => {
  if (!currentResumeId.value) {
    ElMessage.warning('暂无候选人信息')
    return
  }

  const statusMap = { 3: '进入待定', 4: '通过录用', 5: '不予录用' }
  const actionText = statusMap[status] || '更新状态'

  try {
    await ElMessageBox.confirm(
      `确定将候选人状态标记为"${actionText}"吗？`,
      '确认操作',
      { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' }
    )
  } catch {
    return
  }

  statusUpdating.value = true
  try {
    await updateResumeStatus(currentResumeId.value, status)
    ElMessage.success(`已${actionText}`)
  } catch (error) {
    console.error('更新状态失败:', error)
    ElMessage.error('更新状态失败')
  } finally {
    statusUpdating.value = false
  }
}

// 导出评价报告
const handleExport = () => {
  if (!currentEvaluationId.value) {
    ElMessage.warning('暂无评价数据')
    return
  }

  const printContent = `
    <html>
    <head><meta charset="utf-8"><title>面试评价报告</title>
    <style>
      body { font-family: 'Microsoft YaHei', sans-serif; padding: 40px; }
      h1 { text-align: center; color: #303133; }
      h2 { color: #409eff; border-bottom: 2px solid #409eff; padding-bottom: 6px; }
      .info { display: flex; gap: 20px; margin: 20px 0; }
      .info-item { flex: 1; }
      .score-box { text-align: center; margin: 30px 0; }
      .score-num { font-size: 48px; font-weight: bold; color: #409eff; }
      .dimension { margin: 12px 0; }
      .dimension .bar { height: 20px; background: #e4e7ed; border-radius: 10px; }
      .dimension .fill { height: 20px; background: #409eff; border-radius: 10px; }
      .footer { text-align: center; color: #909399; margin-top: 40px; font-size: 12px; }
    </style>
    </head>
    <body>
      <h1>面试评价报告</h1>
      <div class="info">
        <div class="info-item"><strong>候选人：</strong>${candidateInfo.name}</div>
        <div class="info-item"><strong>应聘岗位：</strong>${candidateInfo.position}</div>
        <div class="info-item"><strong>面试日期：</strong>${candidateInfo.date}</div>
      </div>
      <div class="score-box">
        <div style="font-size:16px;color:#606266">综合得分</div>
        <div class="score-num">${totalScore.value}</div>
        <div style="color:#606266">${getLevelInfo.text}</div>
      </div>
      <h2>维度评分</h2>
      ${dimensionList.map(d => `
        <div class="dimension">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px">
            <span>${d.name} (${d.weight})</span><span>${d.score}分</span>
          </div>
          <div class="bar"><div class="fill" style="width:${d.score}%"></div></div>
        </div>
      `).join('')}
      <h2>AI综合评语</h2>
      <p style="line-height:1.8;color:#303133">${evaluateInfo.aiComment}</p>
      <h2>核心优势</h2>
      <ul>${evaluateInfo.advantages.map(a => `<li>${a}</li>`).join('')}</ul>
      <h2>待提升领域</h2>
      <ul>${evaluateInfo.concerns.map(c => `<li>${c}</li>`).join('')}</ul>
      <h2>录用建议</h2>
      <p style="line-height:1.8;color:#303133">${evaluateInfo.suggestion}</p>
      <div class="footer">由企业HR智能助手生成</div>
    </body>
    </html>
  `

  const win = window.open('', '_blank')
  win.document.write(printContent)
  win.document.close()
  win.print()
}

// ==================== ECharts 雷达图初始化 ====================
const initRadarChart = () => {
  if (!radarRef.value) return

  if (radarChart) {
    radarChart.dispose()
  }

  radarChart = echarts.init(radarRef.value)
  const indicator = dimensionList.map(item => ({ name: item.name, max: 100 }))
  const data = dimensionList.map(item => item.score)

  const option = {
    radar: {
      radius: '70%',
      indicator: indicator,
      splitLine: { lineStyle: { color: '#e4e7ed' } },
      axisLine: { lineStyle: { color: '#e4e7ed' } }
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: data,
            name: '能力评分',
            areaStyle: {
              color: 'rgba(64, 158, 255, 0.2)'
            },
            itemStyle: { color: '#409eff' },
            lineStyle: { width: 2 }
          }
        ]
      }
    ]
  }
  radarChart.setOption(option)
  window.addEventListener('resize', () => radarChart.resize())
}

// 生命周期
onMounted(async () => {
  const evaluationId = route.params.id
  const summaryId = route.query.summaryId
  const resumeId = route.query.resumeId

  console.log('路由参数:', { evaluationId, summaryId, resumeId })

  // 1. 优先使用路由 param id（从评价列表点击进入或刚生成后跳转）
  if (evaluationId && evaluationId !== '0') {
    loading.value = true
    try {
      const response = await getEvaluationDetail(evaluationId)
      if (response.code === 0) {
        fillEvaluationData(response.data)
      } else {
        ElMessage.error(response.message || '获取评价详情失败')
      }
    } catch (error) {
      console.error('加载评价详情失败:', error)
      ElMessage.error('加载评价详情失败')
    } finally {
      loading.value = false
    }
    return
  }

  // 2. 有 summaryId，生成新评价
  if (summaryId) {
    await handleGenerateEvaluation(summaryId)
    return
  }

  // 3. 有 resumeId，加载已有评价
  if (resumeId) {
    await loadEvaluation(resumeId)
    return
  }

  // 4. 没有参数时显示提示
  ElMessage.warning('缺少必要参数，请使用 /evaluation?resumeId=9 访问')

  candidateInfo.name = '请先选择候选人'
  candidateInfo.position = '面试评价系统'
  candidateInfo.date = new Date().toLocaleDateString('zh-CN')
  evaluateInfo.aiComment = '请通过简历管理页面进入评价功能，或直接访问：/evaluation?resumeId=9'
})
</script>

<style scoped>
.interview-evaluate-page {
  width: 100%;
  padding-bottom: 80px;
}

.breadcrumb {
  margin-bottom: 16px;
}

.main-row {
  width: 100%;
}

.left-card {
  position: sticky;
  top: 20px;
  padding: 24px;
}

.candidate-info {
  text-align: center;
  margin-bottom: 30px;
}
.name {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}
.position-tag {
  margin-bottom: 8px;
}
.date {
  font-size: 14px;
  color: #606266;
}

.total-score {
  text-align: center;
  margin-bottom: 20px;
}
.inner-score {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}
.level-tag {
  font-size: 14px;
  padding: 6px 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 15px 0;
}
.dimension-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}
.label {
  width: 120px;
  font-size: 14px;
  color: #303133;
}
.weight {
  color: #909399;
  font-size: 12px;
}
.progress {
  flex: 1;
  margin: 0 10px;
}
.score {
  width: 40px;
  text-align: right;
  font-weight: 600;
  font-size: 14px;
}

.chart-box {
  width: 100%;
  height: 300px;
  margin: 0 auto;
}

.right-card {
  margin-bottom: 16px;
}
.comment-content {
  line-height: 1.8;
  color: #303133;
  font-size: 14px;
}
.detail-text {
  line-height: 1.6;
  color: #606266;
}

.box-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
}
.box-title.success { color: #67c23a; }
.box-title.warning { color: #e6a23c; }
.list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.list li {
  line-height: 1.8;
  color: #606266;
  margin-bottom: 6px;
}

.suggestion-box {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 4px;
  line-height: 1.6;
  color: #303133;
  font-weight: 500;
}

.bottom-operate {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 999;
  background: #fff;
}
.operate-card {
  padding: 16px 24px;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.08);
}
.btn-group {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.mt-15 { margin-top: 15px; }
.mt-25 { margin-top: 25px; }
.mb-10 { margin-bottom: 10px; }
.ml-20 { margin-left: 20px; }
</style>