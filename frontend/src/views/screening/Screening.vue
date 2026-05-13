<template>
  <div class="screening-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item>简历管理</el-breadcrumb-item>
      <el-breadcrumb-item>智能简历筛选</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 页面标题 -->
    <h2 class="page-title">智能简历筛选</h2>

    <!-- 主布局：左右分栏 -->
    <el-row :gutter="20">
      <!-- 左侧：筛选条件配置 -->
      <el-col :span="8">
        <!-- 卡片1：岗位选择 -->
        <el-card class="filter-card" shadow="never" title="目标岗位">
          <el-form :model="filterForm" :rules="formRules" ref="formRef">
            <el-form-item prop="positionId">
              <el-select
                v-model="filterForm.positionId"
                placeholder="请选择目标岗位"
                filterable
                clearable
                style="width: 100%"
                @change="getPositionJD"
              >
                <el-option
                  v-for="item in positionList"
                  :key="item.id"
                  :label="item.position_name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>

            <!-- JD摘要展示 -->
            <div class="jd-desc" v-if="jdContent">
              <span class="label">JD摘要：</span>
              <p>{{ jdContent }}</p>
            </div>
          </el-form>
        </el-card>

        <!-- 卡片2：筛选数量 -->
        <el-card class="filter-card" shadow="never" title="筛选数量">
          <div class="slider-wrapper">
            <span>返回Top {{ filterForm.topNum }} 份简历</span>
            <el-slider
              v-model="filterForm.topNum"
              :min="5"
              :max="50"
              :step="5"
              show-input
              class="mt-10"
            />
          </div>
        </el-card>

        <!-- 卡片3：附加条件（可折叠） -->
        <el-card class="filter-card" shadow="never" title="附加筛选条件">
          <el-collapse v-model="activeCollapse">
            <el-collapse-item title="展开/收起" name="1">
              <el-form :model="filterForm" class="extra-form">
                <!-- 最低学历 -->
                <el-form-item label="最低学历">
                  <el-select v-model="filterForm.education" placeholder="不限" style="width: 100%">
                    <el-option label="大专" value="大专" />
                    <el-option label="本科" value="本科" />
                    <el-option label="硕士" value="硕士" />
                    <el-option label="博士" value="博士" />
                  </el-select>
                </el-form-item>

                <!-- 最少工作年限 -->
                <el-form-item label="最少工作年限">
                  <el-input-number
                    v-model="filterForm.workYear"
                    :min="0"
                    :max="30"
                    placeholder="不限"
                    style="width: 100%"
                  />
                  <span class="ml-10">年</span>
                </el-form-item>

                <!-- 必须技能 -->
                <el-form-item label="必须技能">
                  <el-select
                    v-model="filterForm.skills"
                    multiple
                    allow-create
                    filterable
                    placeholder="可输入并创建新技能"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="item in skillOptions"
                      :key="item"
                      :label="item"
                      :value="item"
                    />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-collapse-item>
          </el-collapse>
        </el-card>

        <!-- 卡片4：自定义要求 -->
        <el-card class="filter-card" shadow="never" title="自定义筛选要求">
          <el-input
            v-model="filterForm.customReq"
            type="textarea"
            :rows="3"
            placeholder="输入额外筛选要求，如：有电商行业经验优先、985/211优先"
          />
        </el-card>

        <!-- 开始筛选按钮 -->
        <el-button
          type="primary"
          size="large"
          block
          :loading="loading"
          @click="startScreening"
          class="start-btn"
        >
          AI开始智能筛选
        </el-button>
      </el-col>

      <!-- 右侧：筛选结果展示 -->
      <el-col :span="16">
        <!-- 统计提示 -->
        <el-alert
          v-if="resultList.length > 0"
          type="info"
          :title="`共匹配到 ${resultList.length} 份简历，按匹配度排序`"
          class="result-alert"
        />

        <!-- 加载中状态：骨架屏 -->
        <div v-else-if="loading" class="loading-wrapper">
          <el-skeleton active :rows="8" />
          <div class="loading-text">AI正在智能匹配中，请稍候...</div>
        </div>

        <!-- 空状态 -->
        <div v-else-if="!resultList.length && isScreened" class="empty-wrapper">
          <el-empty description="未找到匹配的简历" />
        </div>
        <div v-else class="empty-wrapper">
          <el-empty description="请选择岗位并点击开始筛选" />
        </div>

        <!-- 筛选结果卡片列表 -->
        <div
          v-for="item in resultList"
          :key="item.resume_id"
          class="result-card"
        >
          <el-card shadow="never" hover>
            <!-- 卡片头部 -->
            <div class="card-header">
              <div class="candidate-info">
                <h3 class="name">{{ item.candidate_name }}</h3>
                <div class="base-tags">
                  <span>{{ item.education || '未知' }}</span>
                  <span>|</span>
                  <span>{{ item.work_years || 0 }}年工作经验</span>
                  <span>|</span>
                  <span>{{ item.current_position || '未知' }}</span>
                </div>
                <!-- 推荐等级标签 -->
                <el-tag
                  :type="getLevelType(item.match_score)"
                  class="level-tag mt-5"
                >
                  {{ item.recommendation }}
                </el-tag>
              </div>

              <!-- 匹配度环形进度条 -->
              <div class="score-wrapper">
                <el-progress
                  type="circle"
                  :percentage="Math.round(item.match_score)"
                  :width="60"
                  :color="getScoreColor(item.match_score)"
                />
                <span class="score-text">{{ Math.round(item.match_score) }}分</span>
              </div>
            </div>

            <!-- 匹配详情折叠面板 -->
            <el-collapse class="mt-15">
              <el-collapse-item title="查看匹配详情">
                <div class="match-detail" v-if="item.match_analysis">
                  <div class="match-item">
                    <span class="label success">匹配优势：</span>
                    <el-tag
                      v-for="tag in item.match_analysis.match_advantages"
                      :key="tag"
                      type="success"
                      class="mr-5 mt-5"
                    >
                      {{ tag }}
                    </el-tag>
                  </div>
                  <div class="match-item mt-10">
                    <span class="label warning">匹配短板：</span>
                    <el-tag
                      v-for="tag in item.match_analysis.match_weaknesses"
                      :key="tag"
                      type="warning"
                      class="mr-5 mt-5"
                    >
                      {{ tag }}
                    </el-tag>
                  </div>
                  <div class="match-item mt-10">
                    <span class="label">AI综合评语：</span>
                    <p class="ai-comment">{{ item.match_analysis.overall_comment }}</p>
                  </div>
                  <div class="match-item mt-10" v-if="item.match_analysis.interview_suggestions?.length">
                    <span class="label">面试建议：</span>
                    <ul class="suggestion-list">
                      <li v-for="(sug, idx) in item.match_analysis.interview_suggestions" :key="idx">
                        {{ sug }}
                      </li>
                    </ul>
                  </div>
                </div>
                <div v-else class="match-detail">
                  <p class="no-analysis">暂无详细分析</p>
                </div>
              </el-collapse-item>
            </el-collapse>

            <!-- 操作按钮组 -->
            <el-button-group class="operate-group mt-15">
              <el-button type="primary" link @click="viewDetail(item.resume_id)">查看详情</el-button>
              <el-button type="success" link @click="generateInterview(item.resume_id)">生成面试题</el-button>
              <el-button type="success" link @click="markPass(item.resume_id)">标记通过</el-button>
              <el-button type="danger" link @click="markReject(item.resume_id)">标记不通过</el-button>
            </el-button-group>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { getPositionList } from '@/api/position'
import { screenByPosition, batchMarkResumes } from '@/api/screening'
import { updateResumeStatus } from '@/api/resume'

const router = useRouter()

// 表单引用
const formRef = ref(null)
// 折叠面板激活项
const activeCollapse = ref(['1'])
// 加载状态
const loading = ref(false)
// 是否已筛选
const isScreened = ref(false)

// 岗位列表
const positionList = ref([])

// 技能选项
const skillOptions = ref(['Vue3', 'React', 'Java', 'MySQL', 'Python', 'Spring', '微服务', 'TypeScript', 'Docker', 'Kubernetes'])

// 筛选表单
const filterForm = reactive({
  positionId: '',
  topNum: 10,
  education: '',
  workYear: 0,
  skills: [],
  customReq: ''
})

// 表单校验规则
const formRules = ref({
  positionId: [{ required: true, message: '请选择目标岗位', trigger: 'change' }]
})

// JD摘要
const jdContent = ref('')
// 筛选结果
const resultList = ref([])

// 获取岗位列表
const fetchPositionList = async () => {
  try {
    const res = await getPositionList({ page: 1, page_size: 100, status: 1 })
    positionList.value = res.items || []
  } catch (error) {
    console.error('获取岗位列表失败:', error)
    ElMessage.error('获取岗位列表失败')
  }
}

// 获取岗位JD
const getPositionJD = (id) => {
  const item = positionList.value.find(i => i.id === id)
  if (item) {
    const jd = item.job_description || ''
    const req = item.requirements || ''
    const fullText = `${jd}\n${req}`
    jdContent.value = fullText.length > 200 ? fullText.slice(0, 200) + '...' : fullText
  } else {
    jdContent.value = ''
  }
}

// 推荐等级类型
const getLevelType = (score) => {
  if (score >= 85) return 'success'
  if (score >= 70) return 'primary'
  if (score >= 55) return 'info'
  return 'danger'
}

// 分数颜色
const getScoreColor = (score) => {
  if (score >= 85) return '#67c23a'
  if (score >= 70) return '#409eff'
  if (score >= 55) return '#909399'
  return '#f56c6c'
}

// 开始筛选
const startScreening = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    isScreened.value = true
    resultList.value = []

    try {
      // 构建筛选条件
      const filters = {}
      if (filterForm.education) {
        filters.min_education = filterForm.education
      }
      if (filterForm.workYear > 0) {
        filters.min_work_years = filterForm.workYear
      }
      if (filterForm.skills && filterForm.skills.length > 0) {
        filters.required_skills = filterForm.skills
      }

      // 调用后端API
      const requestData = {
        position_id: filterForm.positionId,
        top_n: filterForm.topNum
      }

      // 如果有筛选条件，添加到请求中
      if (Object.keys(filters).length > 0) {
        requestData.filters = filters
      }

      const res = await screenByPosition(requestData)

      if (res.code === 0 && res.data) {
        resultList.value = res.data.results || []
        ElMessage.success(`AI智能筛选完成，共匹配到 ${resultList.value.length} 份简历`)
      } else {
        ElMessage.error(res.message || '筛选失败')
      }
    } catch (error) {
      console.error('筛选失败:', error)
      ElMessage.error(error.response?.data?.detail || '筛选失败，请稍后重试')
    } finally {
      loading.value = false
    }
  })
}

// 查看详情
const viewDetail = (resumeId) => {
  router.push(`/resume/detail/${resumeId}`)
}

// 生成面试题
const generateInterview = (resumeId) => {
  ElMessage.info('生成功能开发中...')
  // TODO: 实现生成面试题功能
}

// 标记通过
const markPass = async (resumeId) => {
  try {
    await ElMessageBox.confirm('确定标记该简历为"通过初筛"吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    })

    await updateResumeStatus(resumeId, 2)
    ElMessage.success('标记成功')

    // 从列表中移除或更新状态
    const index = resultList.value.findIndex(item => item.resume_id === resumeId)
    if (index !== -1) {
      resultList.value.splice(index, 1)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('标记失败:', error)
      ElMessage.error('标记失败')
    }
  }
}

// 标记不通过
const markReject = async (resumeId) => {
  try {
    await ElMessageBox.confirm('确定标记该简历为"不通过"吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await updateResumeStatus(resumeId, 5)
    ElMessage.success('标记成功')

    // 从列表中移除或更新状态
    const index = resultList.value.findIndex(item => item.resume_id === resumeId)
    if (index !== -1) {
      resultList.value.splice(index, 1)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('标记失败:', error)
      ElMessage.error('标记失败')
    }
  }
}

// 组件挂载时获取岗位列表
onMounted(() => {
  fetchPositionList()
})
</script>

<style scoped>
.screening-page {
  width: 100%;
}

/* 面包屑 */
.breadcrumb {
  margin-bottom: 16px;
}

/* 页面标题 */
.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
}

/* 左侧筛选卡片 */
.filter-card {
  margin-bottom: 16px;
}

/* JD摘要样式 */
.jd-desc {
  margin-top: 12px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}
.jd-desc .label {
  font-weight: 600;
  color: #303133;
}
.jd-desc p {
  margin: 5px 0 0;
}

/* 附加条件表单 */
.extra-form {
  margin-top: 10px;
}

/* 开始筛选按钮 */
.start-btn {
  margin-top: 10px;
}

/* 右侧结果提示 */
.result-alert {
  margin-bottom: 16px;
}

/* 加载/空状态包装器 */
.loading-wrapper, .empty-wrapper {
  padding: 40px 0;
  text-align: center;
}
.loading-text {
  margin-top: 20px;
  color: #606266;
  font-size: 14px;
}

/* 结果卡片 */
.result-card {
  margin-bottom: 12px;
  transition: all 0.3s;
}
.result-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.candidate-info .name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 5px;
}
.base-tags {
  font-size: 14px;
  color: #606266;
}
.level-tag {
  margin-top: 5px;
}

/* 分数包装 */
.score-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}
.score-text {
  font-size: 12px;
  color: #606266;
  font-weight: 600;
}

/* 匹配详情 */
.match-detail {
  line-height: 1.8;
}
.match-item .label {
  font-weight: 600;
  margin-right: 8px;
}
.match-item .label.success {
  color: #67c23a;
}
.match-item .label.warning {
  color: #e6a23c;
}
.ai-comment {
  color: #606266;
  margin: 5px 0 0;
  line-height: 1.6;
}
.suggestion-list {
  margin: 5px 0 0 20px;
  padding: 0;
  color: #606266;
}
.suggestion-list li {
  margin: 3px 0;
}
.no-analysis {
  color: #909399;
  text-align: center;
  padding: 10px 0;
}

/* 操作按钮组 */
.operate-group {
  width: 100%;
  display: flex;
  justify-content: flex-start;
}

/* 通用间距类 */
.mt-5 { margin-top: 5px; }
.mt-10 { margin-top: 10px; }
.mt-15 { margin-top: 15px; }
.ml-10 { margin-left: 10px; }
.mr-5 { margin-right: 5px; }
</style>
