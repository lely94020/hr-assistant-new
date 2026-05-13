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
              v-for="item in dimensionList"
              :key="item.name"
              :title="`${item.name} · ${item.score}分`"
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
import { ElMessage } from 'element-plus'
import { Check, Warning } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// 候选人基础信息
const candidateInfo = reactive({
  name: '张三',
  position: '高级前端开发工程师',
  date: '2025-01-20 14:00-15:30'
})

// 综合得分
const totalScore = ref(84.7)
// 折叠面板激活项
const activeCollapse = ref([0])
// HR补充评价
const hrComment = ref('候选人综合素质优秀，符合岗位要求，建议录用。')
// 雷达图 DOM 引用
const radarRef = ref(null)
let radarChart = null

// 维度评分列表（权重+分数+详情）
const dimensionList = reactive([
  { name: '专业能力', weight: '30%', score: 88, detail: '熟练掌握Vue3/React/TS，前端工程化经验丰富，技术栈完全匹配岗位需求，代码规范度高。' },
  { name: '逻辑思维', weight: '20%', score: 85, detail: '分析问题思路清晰，能快速定位问题核心，算法和逻辑推理能力良好，应对复杂场景表现优秀。' },
  { name: '沟通表达', weight: '15%', score: 90, detail: '表达流畅，逻辑清晰，善于倾听和总结，团队沟通协作能力突出。' },
  { name: '学习能力', weight: '15%', score: 82, detail: '主动学习新技术，有自我提升意识，对前沿技术有一定了解，学习效率较高。' },
  { name: '团队协作', weight: '10%', score: 86, detail: '有团队项目经验，善于配合他人工作，责任心强，具备良好的团队意识。' },
  { name: '文化匹配', weight: '10%', score: 79, detail: '价值观与公司匹配度较高，职业规划清晰，稳定性较好。' }
])

// 评价详情数据
const evaluateInfo = reactive({
  aiComment: '该候选人拥有5年前端开发经验，技术栈全面且扎实，熟练掌握Vue3、React、TypeScript等核心技术，具备大型企业级项目开发与性能优化经验。专业能力突出，逻辑思维与沟通表达能力优秀，学习能力和团队协作意识良好。整体综合素质远超岗位基础要求，是极具潜力的优质候选人。不足之处在于微前端架构实践经验较少，对低代码平台的了解不够深入。建议入职后针对性培养微前端相关技术，未来可成长为团队核心骨干，完全符合岗位录用标准。',
  advantages: ['技术栈全面匹配', '项目经验丰富', '沟通表达优秀', '逻辑思维清晰'],
  concerns: ['微前端经验不足', '低代码平台实践较少'],
  suggestion: '候选人综合素质优秀，专业能力、软技能均满足岗位要求，建议直接录用，可作为核心开发人员培养。'
})

// ==================== 工具方法 ====================
// 获取分数对应颜色
const getScoreColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 70) return '#409eff'
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
  } else if (score >= 70) {
    getLevelInfo.type = 'primary'
    getLevelInfo.text = '推荐'
  } else if (score >= 60) {
    getLevelInfo.type = 'info'
    getLevelInfo.text = '一般'
  } else {
    getLevelInfo.type = 'danger'
    getLevelInfo.text = '不推荐'
  }
}

// 保存HR评价
const saveHrComment = () => {
  ElMessage.success('HR补充评价保存成功！')
}

// ==================== ECharts 雷达图初始化 ====================
const initRadarChart = () => {
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
              color: 'rgba(64, 158, 255, 0.2)' // 半透明填充
            },
            itemStyle: { color: '#409eff' },
            lineStyle: { width: 2 }
          }
        ]
      }
    ]
  }
  radarChart.setOption(option)
  // 响应式适配
  window.addEventListener('resize', () => radarChart.resize())
}

// 生命周期
onMounted(() => {
  setLevelInfo()
  nextTick(() => initRadarChart())
})
</script>

<style scoped>
.interview-evaluate-page {
  width: 100%;
  padding-bottom: 80px; /* 预留底部操作栏高度 */
}

/* 面包屑 */
.breadcrumb {
  margin-bottom: 16px;
}

/* 主布局 */
.main-row {
  width: 100%;
}

/* 左侧卡片：sticky 固定定位 */
.left-card {
  position: sticky;
  top: 20px;
  padding: 24px;
}

/* 候选人信息 */
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

/* 综合得分 */
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

/* 维度评分 */
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

/* 雷达图容器 */
.chart-box {
  width: 100%;
  height: 300px;
  margin: 0 auto;
}

/* 右侧卡片 */
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

/* 优势/待提升模块 */
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

/* 录用建议 */
.suggestion-box {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 4px;
  line-height: 1.6;
  color: #303133;
  font-weight: 500;
}

/* 底部固定操作栏 */
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

/* 通用间距类 */
.mt-15 { margin-top: 15px; }
.mt-25 { margin-top: 25px; }
.mb-10 { margin-bottom: 10px; }
.ml-20 { margin-left: 20px; }
</style>