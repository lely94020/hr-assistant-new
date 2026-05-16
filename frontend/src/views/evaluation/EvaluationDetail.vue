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
          <el-button type="success" size="large">通过录用</el-button>
          <el-button type="warning" size="large">进入待定</el-button>
          <el-button type="danger" size="large">不予录用</el-button>
          <el-button type="primary" size="large" class="ml-20">导出评价报告</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElLoading } from 'element-plus'
import { Check, Warning } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import {
  generateEvaluation,
  getLatestEvaluation,
  updateHrComment
} from '@/api/evaluation'

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

// 加载评价数据
const loadEvaluation = async (resumeId) => {
  loading.value = true
  try {
    const response = await getLatestEvaluation(resumeId)

    // 填充候选人信息
    if (response.candidate_info) {
      candidateInfo.name = response.candidate_info.name || '未知'
      candidateInfo.position = response.candidate_info.position || '未知岗位'

      // 如果有面试日期，可以格式化显示
      if (response.created_at) {
        const date = new Date(response.created_at)
        candidateInfo.date = date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        })
      }
    }

    // 填充评价数据
    currentEvaluationId.value = response.id
    totalScore.value = response.total_score

    // 填充各维度评分
    dimensionList[0].score = response.scores.professional.score
    dimensionList[0].detail = response.scores.professional.comment || ''

    dimensionList[1].score = response.scores.logic.score
    dimensionList[1].detail = response.scores.logic.comment || ''

    dimensionList[2].score = response.scores.communication.score
    dimensionList[2].detail = response.scores.communication.comment || ''

    dimensionList[3].score = response.scores.learning.score
    dimensionList[3].detail = response.scores.learning.comment || ''

    dimensionList[4].score = response.scores.teamwork.score
    dimensionList[4].detail = response.scores.teamwork.comment || ''

    dimensionList[5].score = response.scores.culture_fit.score
    dimensionList[5].detail = response.scores.culture_fit.comment || ''

    // 填充评价详情
    evaluateInfo.aiComment = response.ai_comment || '暂无AI评语'
    evaluateInfo.advantages = response.key_strengths || []
    evaluateInfo.concerns = response.improvement_areas || []
    evaluateInfo.suggestion = response.hiring_suggestion || '暂无录用建议'

    // HR补充评价
    hrComment.value = response.hr_comment || ''

    // 设置推荐等级
    setLevelInfo()

    // 初始化雷达图
    nextTick(() => initRadarChart())

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
onMounted(() => {
  // 从路由参数获取resumeId或summaryId
  const resumeId = route.query.resumeId
  const summaryId = route.query.summaryId

  console.log('路由参数:', { resumeId, summaryId })

  if (summaryId) {
    // 如果有summaryId，先生成评价
    handleGenerateEvaluation(summaryId)
  } else if (resumeId) {
    // 否则直接加载已有评价
    loadEvaluation(resumeId)
  } else {
    // 没有参数时显示提示，但不跳转（方便调试）
    ElMessage.warning('缺少必要参数，请使用 /evaluation?resumeId=9 访问')

    // 设置默认提示信息
    candidateInfo.name = '请先选择候选人'
    candidateInfo.position = '面试评价系统'
    candidateInfo.date = new Date().toLocaleDateString('zh-CN')
    evaluateInfo.aiComment = '请通过简历管理页面进入评价功能，或直接访问：/evaluation?resumeId=9'
  }
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