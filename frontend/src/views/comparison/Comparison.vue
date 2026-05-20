<template>
  <div class="candidate-compare-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item>面试管理</el-breadcrumb-item>
      <el-breadcrumb-item>候选人对比</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 1. 顶部选择区 -->
    <el-card class="search-card" shadow="never" title="对比配置">
      <el-row :gutter="20" align="middle">
        <el-col :span="6">
          <el-select
            v-model="searchForm.positionId"
            filterable
            placeholder="请选择要对比的岗位"
            style="width: 100%"
            @change="handlePositionChange"
          >
            <el-option
              v-for="item in positionList"
              :key="item.id"
              :label="item.position_name"
              :value="item.id"
            />
          </el-select>
        </el-col>
        <el-col :span="10">
          <el-select
            v-model="searchForm.candidateIds"
            multiple
            filterable
            :multiple-limit="5"
            placeholder="请选择候选人（2-5人）"
            style="width: 100%"
          >
            <el-option
              v-for="item in candidateList"
              :key="item.id"
              :label="item.candidate_name"
              :value="item.id"
            />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-button
            type="primary"
            :loading="comparing"
            :disabled="searchForm.candidateIds.length < 2"
            @click="startCompare"
          >
            开始对比
          </el-button>
          <el-button @click="resetCompare">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 2. 对比结果区（仅对比后显示） -->
    <div v-if="comparisonData" class="result-wrapper">
      <!-- 区域1：基础信息横向对比表格 -->
      <el-card class="result-card" shadow="never" title="基础信息对比">
        <el-table
          :data="tableColumns"
          border
          style="width: 100%"
          header-cell-class-name="table-header"
          cell-class-name="table-cell"
        >
          <el-table-column
            fixed
            prop="label"
            label="对比项"
            width="120"
            align="center"
          />
          <el-table-column
            v-for="candidate in comparisonData.candidates"
            :key="candidate.resume_id"
            :label="candidate.name"
            align="center"
          >
            <template #default="scope">
              <div
                :class="[
                  'cell-content',
                  isBestItem(scope.row.prop, candidate.resume_id) ? 'best-cell' : ''
                ]"
              >
                {{ getCellValue(scope.row.prop, candidate) }}
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 区域2：评分对比（图表切换） -->
      <el-card class="result-card" shadow="never" title="能力维度评分对比">
        <el-radio-group v-model="chartType" class="chart-switch">
          <el-radio value="bar">柱状图对比</el-radio>
          <el-radio value="radar">雷达图叠加</el-radio>
        </el-radio-group>
        <div ref="chartRef" class="chart-container"></div>
      </el-card>

      <!-- 区域3：综合得分排名 -->
      <el-card class="result-card" shadow="never" title="综合得分排名">
        <div class="rank-list">
          <div
            v-for="(item, index) in rankingList"
            :key="index"
            class="rank-item"
          >
            <div class="rank-num">
              <el-icon
                v-if="index === 0"
                color="#ffd700"
                size="20"
              ><Trophy /></el-icon>
              <el-icon
                v-else-if="index === 1"
                color="#c0c0c0"
                size="20"
              ><Medal /></el-icon>
              <el-icon
                v-else-if="index === 2"
                color="#cd7f32"
                size="20"
              ><Star /></el-icon>
              <span v-else>第{{ index + 1 }}名</span>
            </div>
            <div class="rank-info">
              <div class="name">{{ item.name }}</div>
              <div class="score">综合得分：{{ item.score }}分</div>
              <div class="reason">{{ item.reason }}</div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 3. AI对比分析区 -->
      <el-card class="result-card" shadow="never" title="AI智能对比分析">
        <el-button
          type="primary"
          :loading="analyzing"
          :disabled="hasAiAnalysis"
          @click="handleAiAnalyze"
        >
          {{ hasAiAnalysis ? '已生成AI分析' : '生成AI对比分析' }}
        </el-button>

        <div v-if="hasAiAnalysis" class="ai-analysis-content">
          <el-alert
            :title="aiAnalysis.comparison_summary"
            type="info"
            :closable="false"
            style="margin-bottom: 20px"
          />

          <el-tabs v-model="activeTab" class="ai-tabs">
            <el-tab-pane
              v-for="(analysis, index) in aiAnalysis.candidate_analysis"
              :key="index"
              :label="analysis.name"
            >
              <div class="analysis-item">
                <div class="analysis-box">
                  <h4><el-icon color="#67c23a"><Check /></el-icon> 相对优势</h4>
                  <ul class="green-list">
                    <li v-for="(adv, i) in analysis.advantages_over_others" :key="i">
                      {{ adv }}
                    </li>
                  </ul>
                </div>
                <div class="analysis-box">
                  <h4><el-icon color="#e6a23c"><Warning /></el-icon> 相对劣势</h4>
                  <ul class="orange-list">
                    <li v-for="(dis, i) in analysis.disadvantages" :key="i">
                      {{ dis }}
                    </li>
                  </ul>
                </div>
                <div class="analysis-box">
                  <h4>适合场景</h4>
                  <p class="text">{{ analysis.suitable_scenarios }}</p>
                </div>
                <div class="analysis-box">
                  <h4>录用风险</h4>
                  <p class="text">{{ analysis.risk_points }}</p>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>

          <div class="recommend-box">
            <h3>AI最终推荐结论</h3>
            <p><strong>最佳人选：</strong>{{ aiAnalysis.recommendation.best_choice }}</p>
            <p class="text">{{ aiAnalysis.recommendation.reason }}</p>
            <p><strong>备选人选：</strong>{{ aiAnalysis.recommendation.alternative }}</p>
            <p class="text">{{ aiAnalysis.recommendation.alternative_reason }}</p>
            <p class="final-suggestion">{{ aiAnalysis.hiring_advice }}</p>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-wrapper">
      <el-empty description="请选择2-5位候选人，点击开始对比" />
    </div>

    <!-- 4. 底部操作栏 -->
    <div class="bottom-operate">
      <el-button type="primary" :disabled="!comparisonData" @click="handleExport">
        导出对比报告(PDF)
      </el-button>
      <el-button type="success" :disabled="!comparisonData" @click="handleSave">
        保存对比结果
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Trophy, Medal, Star, Check, Warning } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getPositionList } from '@/api/position'
import { getResumeList } from '@/api/resume'
import {
  createComparison,
  analyzeComparison
} from '@/api/comparison'

const positionList = ref([])
const candidateList = ref([])

const searchForm = reactive({
  positionId: '',
  candidateIds: []
})

const comparisonData = ref(null)
const chartType = ref('bar')
const activeTab = ref(0)
const chartRef = ref(null)
let myChart = null

const comparing = ref(false)
const analyzing = ref(false)
const aiAnalysis = ref(null)

const tableColumns = ref([
  { prop: 'name', label: '姓名' },
  { prop: 'education', label: '学历' },
  { prop: 'school', label: '院校' },
  { prop: 'major', label: '专业' },
  { prop: 'work_years', label: '工作年限' },
  { prop: 'current_company', label: '当前公司' },
  { prop: 'current_position', label: '当前职位' },
  { prop: 'skills', label: '技能标签' },
  { prop: 'total_score', label: '综合得分' }
])

const dimensionList = ['专业能力', '逻辑思维', '沟通表达', '学习能力', '团队协作', '文化匹配']

const hasAiAnalysis = computed(() => {
  return aiAnalysis.value !== null
})

const rankingList = computed(() => {
  if (!aiAnalysis.value || !aiAnalysis.value.ranking) {
    return []
  }
  return aiAnalysis.value.ranking.sort((a, b) => a.rank - b.rank)
})

const loadPositions = async () => {
  try {
    const res = await getPositionList({ page: 1, page_size: 100 })
    positionList.value = res.items || []
  } catch (error) {
    console.error('加载岗位列表失败:', error)
  }
}

const handlePositionChange = async () => {
  searchForm.candidateIds = []
  candidateList.value = []

  if (!searchForm.positionId) return

  try {
    const res = await getResumeList({
      position_id: searchForm.positionId,
      page: 1,
      page_size: 100
    })
    candidateList.value = res.items || []
  } catch (error) {
    console.error('加载候选人列表失败:', error)
    ElMessage.error('加载候选人列表失败')
  }
}

const startCompare = async () => {
  if (!searchForm.positionId) {
    return ElMessage.warning('请选择对比岗位')
  }

  if (searchForm.candidateIds.length < 2) {
    return ElMessage.warning('至少选择2个候选人')
  }

  comparing.value = true
  try {
    const res = await createComparison(
      searchForm.positionId,
      searchForm.candidateIds
    )

    comparisonData.value = res

    aiAnalysis.value = null

    nextTick(() => initChart())
    ElMessage.success('对比创建成功！')
  } catch (error) {
    console.error('创建对比失败:', error)
    ElMessage.error(error.response?.data?.detail || '创建对比失败')
  } finally {
    comparing.value = false
  }
}

const handleAiAnalyze = async () => {
  if (!comparisonData.value) return

  analyzing.value = true
  try {
    const res = await analyzeComparison(comparisonData.value.id)
    aiAnalysis.value = res
    ElMessage.success('AI分析生成成功！')
  } catch (error) {
    console.error('AI分析失败:', error)
    ElMessage.error(error.response?.data?.detail || 'AI分析失败')
  } finally {
    analyzing.value = false
  }
}

const resetCompare = () => {
  searchForm.positionId = ''
  searchForm.candidateIds = []
  comparisonData.value = null
  aiAnalysis.value = null
  candidateList.value = []
  if (myChart) {
    myChart.dispose()
    myChart = null
  }
}

const getCellValue = (prop, candidate) => {
  if (prop === 'skills') {
    return candidate.skills && candidate.skills.length > 0
      ? candidate.skills.join('、')
      : '-'
  }
  if (prop === 'work_years') {
    return candidate[prop] ? candidate[prop] + '年' : '-'
  }
  if (prop === 'total_score') {
    return candidate.evaluation ? candidate.evaluation.total_score : '-'
  }
  return candidate[prop] || '-'
}

const isBestItem = (prop, resumeId) => {
  if (!comparisonData.value || !comparisonData.value.candidates) return false

  const candidates = comparisonData.value.candidates

  if (prop === 'work_years') {
    const values = candidates.map(c => c.work_years || 0)
    const max = Math.max(...values)
    const candidate = candidates.find(c => c.resume_id === resumeId)
    return candidate && candidate.work_years === max && max > 0
  }

  if (prop === 'total_score') {
    const validCandidates = candidates.filter(c => c.evaluation)
    if (validCandidates.length === 0) return false

    const values = validCandidates.map(c => c.evaluation.total_score)
    const max = Math.max(...values)
    const candidate = validCandidates.find(c => c.resume_id === resumeId)
    return candidate && candidate.evaluation.total_score === max
  }

  return false
}

const initChart = () => {
  if (!chartRef.value || !comparisonData.value) return
  if (myChart) myChart.dispose()
  myChart = echarts.init(chartRef.value)

  const candidates = comparisonData.value.candidates.filter(c => c.evaluation)
  const names = candidates.map(c => c.name)

  if (names.length === 0) {
    ElMessage.warning('暂无评价数据，无法生成图表')
    return
  }

  const scoreData = candidates.map(c => [
    c.evaluation.professional_score,
    c.evaluation.logic_score,
    c.evaluation.communication_score,
    c.evaluation.learning_score,
    c.evaluation.teamwork_score,
    c.evaluation.culture_score
  ])

  let option = {}
  if (chartType.value === 'bar') {
    option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      legend: {
        data: dimensionList,
        bottom: 0
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: names,
        axisLabel: {
          interval: 0,
          rotate: 30
        }
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        name: '分数'
      },
      series: dimensionList.map((item, index) => ({
        name: item,
        type: 'bar',
        data: scoreData.map(scores => scores[index]),
        emphasis: {
          focus: 'series'
        }
      }))
    }
  } else {
    option = {
      tooltip: {
        trigger: 'item'
      },
      legend: {
        data: names,
        bottom: 0
      },
      radar: {
        indicator: dimensionList.map(item => ({
          name: item,
          max: 100
        })),
        radius: '65%'
      },
      series: candidates.map((candidate, index) => {
        const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de']
        return {
          name: candidate.name,
          type: 'radar',
          data: candidate.evaluation ? [{
            value: [
              candidate.evaluation.professional_score,
              candidate.evaluation.logic_score,
              candidate.evaluation.communication_score,
              candidate.evaluation.learning_score,
              candidate.evaluation.teamwork_score,
              candidate.evaluation.culture_score
            ]
          }] : [],
          areaStyle: { opacity: 0.2 },
          lineStyle: {
            color: colors[index % colors.length]
          },
          itemStyle: {
            color: colors[index % colors.length]
          }
        }
      })
    }
  }
  myChart.setOption(option)
  window.addEventListener('resize', resizeChart)
}

const resizeChart = () => {
  if (myChart) myChart.resize()
}

watch(chartType, () => {
  nextTick(() => initChart())
})

const handleExport = () => {
  if (!comparisonData.value) return

  const baseUrl = 'http://localhost:8000/api/v1'
  window.open(`${baseUrl}/comparison/${comparisonData.value.id}/export`, '_blank')
}

const handleSave = () => {
  ElMessage.success('对比结果已保存')
}

onMounted(() => {
  loadPositions()
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  if (myChart) {
    myChart.dispose()
  }
})
</script>

<style scoped>
.candidate-compare-page {
  width: 100%;
  padding-bottom: 80px;
}

.breadcrumb {
  margin-bottom: 16px;
}

.search-card {
  margin-bottom: 20px;
}

.result-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.result-card {
  margin-bottom: 0;
}

.table-header {
  background: #f5f7fa;
  font-weight: 600;
}
.table-cell {
  padding: 12px 0;
}
.cell-content {
  padding: 4px 8px;
  border-radius: 4px;
}
.best-cell {
  background-color: #f0f9eb;
  color: #67c23a;
  font-weight: 500;
}

.chart-switch {
  margin-bottom: 15px;
}
.chart-container {
  width: 100%;
  height: 400px;
}

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.rank-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.rank-num {
  width: 40px;
  text-align: center;
  margin-right: 16px;
}
.rank-info {
  flex: 1;
}
.rank-info .name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}
.rank-info .score {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}
.rank-info .reason {
  font-size: 13px;
  color: #909399;
}

.ai-analysis-content {
  margin-top: 20px;
}

.ai-tabs {
  margin-bottom: 20px;
}
.analysis-item {
  padding: 10px 0;
}
.analysis-box {
  margin-bottom: 16px;
}
.analysis-box h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}
.green-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.green-list li {
  color: #67c23a;
  line-height: 1.8;
}
.orange-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.orange-list li {
  color: #e6a23c;
  line-height: 1.8;
}
.text {
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.recommend-box {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}
.recommend-box h3 {
  margin: 0 0 12px 0;
  color: #303133;
}
.recommend-box p {
  line-height: 1.8;
  margin: 0 0 8px 0;
}
.final-suggestion {
  color: #409eff;
  font-weight: 500;
}

.empty-wrapper {
  padding: 60px 0;
  text-align: center;
}

.bottom-operate {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 16px 24px;
  box-shadow: 0 -2px 12px rgba(0,0,0,0.08);
  text-align: center;
  z-index: 99;
}
.bottom-operate .el-button {
  margin: 0 8px;
}
</style>
