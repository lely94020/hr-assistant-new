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
          >
            <el-option
              v-for="item in positionList"
              :key="item.id"
              :label="item.name"
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
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-button
            type="primary"
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
            :key="candidate.id"
            :label="candidate.name"
            align="center"
          >
            <template #default="scope">
              <!-- 最优项高亮 -->
              <div
                :class="[
                  'cell-content',
                  isBestItem(scope.row.prop, candidate.id) ? 'best-cell' : ''
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
        <!-- 图表类型切换 -->
        <el-radio-group v-model="chartType" class="chart-switch">
          <el-radio value="bar">柱状图对比</el-radio>
          <el-radio value="radar">雷达图叠加</el-radio>
        </el-radio-group>
        <!-- 图表容器 -->
        <div ref="chartRef" class="chart-container"></div>
      </el-card>

      <!-- 区域3：综合得分排名 -->
      <el-card class="result-card" shadow="never" title="综合得分排名">
        <div class="rank-list">
          <div
            v-for="(item, index) in comparisonData.rankList"
            :key="item.id"
            class="rank-item"
          >
            <div class="rank-num">
              <!-- 金银铜图标 -->
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
              <div class="score">综合得分：{{ item.totalScore }}分</div>
              <div class="reason">{{ item.reason }}</div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 3. AI对比分析区 -->
      <el-card class="result-card" shadow="never" title="AI智能对比分析">
        <!-- 候选人分析标签页 -->
        <el-tabs v-model="activeTab" class="ai-tabs">
          <el-tab-pane
            v-for="candidate in comparisonData.candidates"
            :key="candidate.id"
            :label="candidate.name"
          >
            <div class="analysis-item">
              <div class="analysis-box">
                <h4><el-icon color="#67c23a"><Check /></el-icon> 相对优势</h4>
                <ul class="green-list">
                  <li v-for="(adv, i) in candidate.analysis.advantages" :key="i">
                    {{ adv }}
                  </li>
                </ul>
              </div>
              <div class="analysis-box">
                <h4><el-icon color="#e6a23c"><Warning /></el-icon> 相对劣势</h4>
                <ul class="orange-list">
                  <li v-for="(dis, i) in candidate.analysis.disadvantages" :key="i">
                    {{ dis }}
                  </li>
                </ul>
              </div>
              <div class="analysis-box">
                <h4>适合场景</h4>
                <p class="text">{{ candidate.analysis.fitScene }}</p>
              </div>
              <div class="analysis-box">
                <h4>录用风险</h4>
                <p class="text">{{ candidate.analysis.risk }}</p>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>

        <!-- AI推荐结论 -->
        <div class="recommend-box">
          <h3>AI最终推荐结论</h3>
          <p><strong>最佳人选：</strong>{{ comparisonData.recommend.best }}</p>
          <p><strong>备选人选：</strong>{{ comparisonData.recommend.second }}</p>
          <p class="final-suggestion">{{ comparisonData.recommend.suggestion }}</p>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-wrapper">
      <el-empty description="请选择2-5位候选人，点击开始对比" />
    </div>

    <!-- 4. 底部操作栏 -->
    <div class="bottom-operate">
      <el-button type="primary" :disabled="!comparisonData">
        导出对比报告(PDF)
      </el-button>
      <el-button type="success" :disabled="!comparisonData">
        保存对比结果
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Trophy, Medal, Star, Check, Warning } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// 基础数据
const positionList = ref([
  { id: 1, name: '高级前端开发工程师' },
  { id: 2, name: 'Java开发工程师' },
  { id: 3, name: '产品经理' }
])
const candidateList = ref([
  { id: 1, name: '张三', education: '本科/北京大学', workYear: 5, company: '阿里', job: '前端开发', skills: ['Vue3', 'React', 'TS', 'Vite', '优化'], totalScore: 88 },
  { id: 2, name: '李四', education: '硕士/清华大学', workYear: 3, company: '腾讯', job: '前端开发', skills: ['Vue3', 'TS', '微前端', '工程化'], totalScore: 85 },
  { id: 3, name: '王五', education: '本科/浙江大学', workYear: 4, company: '百度', job: '前端开发', skills: ['React', 'Node', '性能优化'], totalScore: 82 }
])

// 搜索表单
const searchForm = reactive({
  positionId: '',
  candidateIds: []
})

// 对比状态
const comparisonData = ref(null)
const chartType = ref('bar') // bar/radar
const activeTab = ref(1)
const chartRef = ref(null)
let myChart = null

// 表格列配置（基础信息对比项）
const tableColumns = ref([
  { prop: 'name', label: '姓名' },
  { prop: 'education', label: '学历/院校' },
  { prop: 'workYear', label: '工作年限' },
  { prop: 'company', label: '当前公司' },
  { prop: 'job', label: '当前职位' },
  { prop: 'skills', label: '技能标签' }
])

// 维度评分（6个核心维度）
const dimensionList = ['专业能力', '逻辑思维', '沟通表达', '学习能力', '团队协作', '文化匹配']

// ==================== 核心方法 ====================
// 开始对比
const startCompare = () => {
  if (!searchForm.positionId) {
    return ElMessage.warning('请选择对比岗位')
  }
  // 筛选选中的候选人
  const selected = candidateList.value.filter(item =>
    searchForm.candidateIds.includes(item.id)
  )
  // 构造对比数据
  comparisonData.value = {
    candidates: selected.map(item => ({
      ...item,
      scores: [88, 85, 90, 82, 86, 79], // 维度分数
      analysis: {
        advantages: item.id === 1 ? ['技术栈全面', '经验丰富'] : item.id === 2 ? ['学历高', '学习能力强'] : ['性能优化精通', '稳定性好'],
        disadvantages: item.id === 1 ? ['学历一般'] : item.id === 2 ? ['经验较少'] : ['技术广度不足'],
        fitScene: '负责核心业务模块开发',
        risk: '无重大风险'
      }
    })),
    // 排名数据
    rankList: [...selected].sort((a, b) => b.totalScore - a.totalScore).map(item => ({
      id: item.id,
      name: item.name,
      totalScore: item.totalScore,
      reason: item.id === 1 ? '技术全面，经验匹配度最高' : item.id === 2 ? '学历优秀，潜力大' : '专项能力突出'
    })),
    // AI推荐
    recommend: {
      best: '张三（综合得分最高，技术栈完全匹配）',
      second: '李四（学历优秀，学习能力强）',
      suggestion: '张三为最佳录用人选，技术能力、工作经验完全满足岗位要求，可快速上手工作；李四作为优质备选，培养潜力巨大。两人均符合岗位录用标准，建议优先录用张三。'
    }
  }
  // 初始化图表
  nextTick(() => initChart())
  ElMessage.success('对比完成！')
}

// 重置对比
const resetCompare = () => {
  searchForm.positionId = ''
  searchForm.candidateIds = []
  comparisonData.value = null
}

// 获取单元格值
const getCellValue = (prop, candidate) => {
  if (prop === 'skills') return candidate.skills.join('、')
  if (prop === 'workYear') return candidate[prop] + '年'
  return candidate[prop]
}

// 最优项高亮判断
const isBestItem = (prop, id) => {
  if (!comparisonData.value) return false
  const candidates = comparisonData.value.candidates
  if (prop === 'workYear') {
    const max = Math.max(...candidates.map(i => i.workYear))
    return candidates.find(i => i.id === id).workYear === max
  }
  if (prop === 'totalScore') {
    const max = Math.max(...candidates.map(i => i.totalScore))
    return candidates.find(i => i.id === id).totalScore === max
  }
  return false
}

// ==================== ECharts 图表 ====================
const initChart = () => {
  if (!chartRef.value) return
  if (myChart) myChart.dispose()
  myChart = echarts.init(chartRef.value)

  const candidates = comparisonData.value.candidates
  const names = candidates.map(i => i.name)
  const scoreData = candidates.map(i => i.scores)

  let option = {}
  if (chartType.value === 'bar') {
    // 柱状图配置
    option = {
      legend: { data: dimensionList },
      xAxis: { type: 'category', data: names },
      yAxis: { type: 'value', min: 0, max: 100 },
      series: dimensionList.map((item, index) => ({
        name: item,
        type: 'bar',
        data: scoreData.map(item => item[index])
      }))
    }
  } else {
    // 雷达图配置
    option = {
      legend: { data: names, bottom: 0 },
      radar: {
        indicator: dimensionList.map(item => ({ name: item, max: 100 })),
        radius: '70%'
      },
      series: candidates.map((item, index) => ({
        name: item.name,
        type: 'radar',
        data: item.scores,
        areaStyle: { opacity: 0.2 }
      }))
    }
  }
  myChart.setOption(option)
  window.addEventListener('resize', () => myChart.resize())
}

// 监听图表类型切换
watch(chartType, () => initChart())

// 窗口适配
onMounted(() => {
  window.addEventListener('resize', () => myChart?.resize())
})
</script>

<style scoped>
.candidate-compare-page {
  width: 100%;
  padding-bottom: 80px;
}

/* 面包屑 */
.breadcrumb {
  margin-bottom: 16px;
}

/* 顶部选择卡片 */
.search-card {
  margin-bottom: 20px;
}

/* 结果卡片 */
.result-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.result-card {
  margin-bottom: 0;
}

/* 表格样式 */
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
/* 最优项高亮 */
.best-cell {
  background-color: #f0f9eb;
  color: #67c23a;
  font-weight: 500;
}

/* 图表容器 */
.chart-switch {
  margin-bottom: 15px;
}
.chart-container {
  width: 100%;
  height: 400px;
}

/* 排名列表 */
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

/* AI分析区 */
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

/* 推荐结论 */
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

/* 空状态 */
.empty-wrapper {
  padding: 60px 0;
  text-align: center;
}

/* 底部操作栏 */
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