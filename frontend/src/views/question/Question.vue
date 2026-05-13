<template>
  <div class="interview-generate-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item>面试管理</el-breadcrumb-item>
      <el-breadcrumb-item>面试题智能生成</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 页面标题 -->
    <h2 class="page-title">面试题智能生成</h2>

    <!-- 上方：生成配置区 -->
    <el-card class="config-card" shadow="never" title="生成配置">
      <!-- 1. 生成方式选择 -->
      <div class="generate-mode">
        <span class="label">生成方式：</span>
        <el-radio-group v-model="mode" size="large" class="ml-15">
          <el-radio value="position">基于岗位生成</el-radio>
          <el-radio value="resume">基于简历生成</el-radio>
          <el-radio value="mixed">
            岗位+简历混合生成
            <el-tag type="success" size="small" class="ml-8">推荐</el-tag>
          </el-radio>
        </el-radio-group>
      </div>

      <!-- 2. 动态选择框 -->
      <div class="dynamic-select mt-20">
        <!-- 岗位选择 -->
        <el-select
          v-if="mode === 'position' || mode === 'mixed'"
          v-model="form.positionId"
          placeholder="请选择目标岗位"
          filterable
          style="width: 280px; margin-right: 20px"
        >
          <el-option
            v-for="item in positionList"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>

        <!-- 简历/候选人选择 -->
        <el-select
          v-if="mode === 'resume' || mode === 'mixed'"
          v-model="form.resumeId"
          placeholder="请选择候选人/简历"
          filterable
          style="width: 280px"
        >
          <el-option
            v-for="item in resumeList"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
      </div>

      <!-- 3. 题目配置表单 -->
      <el-form :model="form" inline class="question-form mt-20">
        <el-form-item label="题目类型">
          <el-checkbox-group v-model="form.type">
            <el-checkbox value="技术类">技术类</el-checkbox>
            <el-checkbox value="行为类">行为类</el-checkbox>
            <el-checkbox value="情景类">情景类</el-checkbox>
            <el-checkbox value="开放类">开放类</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="难度等级">
          <el-radio-group v-model="form.difficulty">
            <el-radio value="初级">初级</el-radio>
            <el-radio value="中级">中级</el-radio>
            <el-radio value="高级">高级</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="生成数量">
          <el-input-number
            v-model="form.count"
            :min="3"
            :max="20"
            :step="1"
            style="width: 120px"
          />
        </el-form-item>

        <el-form-item label="生成参考答案">
          <el-switch v-model="form.showAnswer" active-text="开启" inactive-text="关闭" />
        </el-form-item>
      </el-form>

      <!-- 生成按钮 -->
      <div class="generate-btn-wrapper mt-20">
        <el-button
          type="primary"
          size="large"
          :icon="MagicStick"
          :loading="generating"
          @click="startGenerate"
        >
          开始生成
        </el-button>
      </div>
    </el-card>

    <!-- 下方：生成结果区 -->
    <el-card class="result-card" shadow="never" title="生成结果">
      <!-- 生成中状态：骨架屏 -->
      <div v-if="generating" class="loading-container">
        <el-skeleton active :rows="form.count" />
        <div class="loading-text">AI正在生成面试题，请稍候...</div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="questions.length === 0" class="empty-container">
        <el-empty description="请完成配置后点击开始生成" />
      </div>

      <!-- 生成结果展示 -->
      <div v-else>
        <!-- 标签页分组展示 -->
        <el-tabs v-model="activeTab" class="result-tabs">
          <el-tab-pane
            v-for="type in typeList"
            :key="type"
            :label="`${type}（${getTypeCount(type)}）`"
            :name="type"
          >
            <!-- 题目列表 -->
            <div class="question-list">
              <div
                v-for="(item, index) in getTypeQuestions(type)"
                :key="item.id"
                class="question-item"
              >
                <el-card shadow="hover">
                  <!-- 题目头部 -->
                  <div class="question-header">
                    <div class="left-info">
                      <span class="num">第{{ index + 1 }}题</span>
                      <el-tag
                        :type="getDifficultyType(item.difficulty)"
                        size="small"
                        class="ml-10"
                      >
                        {{ item.difficulty }}
                      </el-tag>
                    </div>
                  </div>

                  <!-- 题目内容 -->
                  <div class="question-content">{{ item.content }}</div>

                  <!-- 参考答案 & 评分要点 -->
                  <el-collapse class="mt-15" v-if="form.showAnswer">
                    <el-collapse-item title="查看参考答案" name="1">
                      <div class="answer-content">{{ item.answer }}</div>
                    </el-collapse-item>
                    <el-collapse-item title="评分要点" name="2">
                      <div class="score-content">
                        <ol>
                          <li v-for="(point, pIndex) in item.scorePoints" :key="pIndex">
                            {{ point }}
                          </li>
                        </ol>
                      </div>
                    </el-collapse-item>
                  </el-collapse>

                  <!-- 操作按钮 -->
                  <div class="question-operate mt-15">
                    <el-button icon="Edit" link @click="openEditDialog(item)">编辑</el-button>
                    <el-button icon="Delete" link type="danger" @click="deleteQuestion(item.id)">删除</el-button>
                    <el-button icon="CopyDocument" link @click="copyQuestion(item)">复制题目</el-button>
                  </div>
                </el-card>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>

        <!-- 底部操作栏 -->
        <div class="result-footer mt-20">
          <el-button @click="resetGenerate">重新生成</el-button>
          <div>
            <el-button type="primary" class="mr-10" @click="handleSaveToBank">保存到题库</el-button>
            <el-button type="success" @click="handleExportWord">导出为Word</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 编辑题目对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑面试题"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="题目类型" prop="type">
          <el-select v-model="editForm.type" style="width: 100%">
            <el-option label="技术类" value="技术类" />
            <el-option label="行为类" value="行为类" />
            <el-option label="情景类" value="情景类" />
            <el-option label="开放类" value="开放类" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度等级" prop="difficulty">
          <el-select v-model="editForm.difficulty" style="width: 100%">
            <el-option label="初级" value="初级" />
            <el-option label="中级" value="中级" />
            <el-option label="高级" value="高级" />
          </el-select>
        </el-form-item>
        <el-form-item label="题目内容" prop="content">
          <el-input v-model="editForm.content" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="参考答案" prop="answer">
          <el-input v-model="editForm.answer" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="评分要点" prop="scorePoints">
          <el-input v-model="editForm.scorePointsText" type="textarea" :rows="3" placeholder="每行一个评分要点" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEditQuestion">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MagicStick, Edit, Delete, CopyDocument } from '@element-plus/icons-vue'
import { generateQuestions, updateQuestion, deleteQuestion as deleteQuestionApi, saveToQuestionBank } from '@/api/question'
import { getPositionList } from '@/api/position'
import { getResumeList } from '@/api/resume'

// 常量定义
const typeList = ref(['技术类', '行为类', '情景类', '开放类'])

// 类型映射：中文 -> 英文
const typeMap = {
  '技术类': 'technical',
  '行为类': 'behavioral',
  '情景类': 'situational',
  '开放类': 'open'
}

// 难度映射：中文 -> 英文
const difficultyMap = {
  '初级': 'junior',
  '中级': 'middle',
  '高级': 'senior'
}

// 岗位和简历列表
const positionList = ref([])
const resumeList = ref([])

// 核心状态
const mode = ref('mixed')
const generating = ref(false)
const activeTab = ref('技术类')
const editDialogVisible = ref(false)
const editFormRef = ref(null)

// 配置表单
const form = reactive({
  positionId: '',
  resumeId: '',
  type: ['技术类', '行为类'],
  difficulty: '中级',
  count: 5,
  showAnswer: true
})

// 题目列表
const questions = ref([])

// 编辑表单
const editForm = reactive({
  id: null,
  type: '',
  difficulty: '',
  content: '',
  answer: '',
  scorePointsText: ''
})

// 编辑校验规则
const editRules = ref({
  type: [{ required: true, message: '请选择题目类型', trigger: 'change' }],
  difficulty: [{ required: true, message: '请选择难度', trigger: 'change' }],
  content: [{ required: true, message: '请输入题目内容', trigger: 'blur' }]
})

// 获取难度标签类型
const getDifficultyType = (diff) => {
  const map = { '初级':'success', '中级':'warning', '高级':'danger' }
  return map[diff] || 'info'
}

// 统计类型题目数量 - 兼容中英文类型
const getTypeCount = (type) => {
  const count = questions.value.filter(item => {
    // 兼容中英文类型
    return item.type === type ||
           (type === '技术类' && item.type === 'technical') ||
           (type === '行为类' && item.type === 'behavioral') ||
           (type === '情景类' && item.type === 'situational') ||
           (type === '开放类' && item.type === 'open')
  }).length
  return count
}

// 获取对应类型的题目 - 兼容中英文类型
const getTypeQuestions = (type) => {
  const filtered = questions.value.filter(item => {
    // 兼容中英文类型
    return item.type === type ||
           (type === '技术类' && item.type === 'technical') ||
           (type === '行为类' && item.type === 'behavioral') ||
           (type === '情景类' && item.type === 'situational') ||
           (type === '开放类' && item.type === 'open')
  })
  return filtered
}

// 加载岗位列表
const loadPositions = async () => {
  try {
    const res = await getPositionList({ page: 1, page_size: 100 })
    console.log('岗位列表API响应:', res)

    // 兼容两种响应格式
    let items = []
    if (res.code === 0) {
      // 格式1: { code: 0, data: { items: [...] } }
      items = res.data?.items || []
    } else if (res.items) {
      // 格式2: { total: 3, items: [...], page: 1, page_size: 100 }
      items = res.items || []
    }

    positionList.value = items.map(item => ({
      id: item.id,
      name: item.position_name
    }))

    console.log('岗位列表数据:', positionList.value)

    if (positionList.value.length === 0) {
      ElMessage.warning('暂无岗位数据，请先创建岗位')
    }
  } catch (error) {
    console.error('加载岗位列表失败:', error)
    ElMessage.error('加载岗位列表失败')
  }
}

// 加载简历列表
const loadResumes = async () => {
  try {
    const res = await getResumeList({ page: 1, page_size: 100 })
    console.log('简历列表API响应:', res)

    // 兼容两种响应格式
    let items = []
    if (res.code === 0) {
      // 格式1: { code: 0, data: { items: [...] } }
      items = res.data?.items || []
    } else if (res.items) {
      // 格式2: { total: 8, items: [...], page: 1, page_size: 100 }
      items = res.items || []
    }

    resumeList.value = items.map(item => ({
      id: item.id,
      name: item.candidate_name
    }))

    console.log('简历列表数据:', resumeList.value)

    if (resumeList.value.length === 0) {
      ElMessage.warning('暂无简历数据，请先上传简历')
    }
  } catch (error) {
    console.error('加载简历列表失败:', error)
    ElMessage.error('加载简历列表失败')
  }
}

// 开始生成
const startGenerate = async () => {
  if ((mode.value === 'position' || mode.value === 'mixed') && !form.positionId) {
    return ElMessage.warning('请选择目标岗位')
  }
  if ((mode.value === 'resume' || mode.value === 'mixed') && !form.resumeId) {
    return ElMessage.warning('请选择候选人/简历')
  }
  if (form.type.length === 0) {
    return ElMessage.warning('请至少选择一种题目类型')
  }

  // 构建请求参数
  const requestData = {
    mode: mode.value,
    position_id: form.positionId || undefined,
    resume_id: form.resumeId || undefined,
    question_types: form.type.map(t => typeMap[t]),
    difficulty: difficultyMap[form.difficulty],
    count: form.count,
    with_answer: form.showAnswer
  }

  generating.value = true
  questions.value = []

  try {
    const res = await generateQuestions(requestData)
    console.log('生成面试题API响应:', res)

    if (res.questions && res.questions.length > 0) {
      // 转换后端返回的数据格式为前端格式
      questions.value = res.questions.map(q => {
        console.log('原始题目数据:', q)
        return {
          id: q.id,
          type: q.type_name,
          difficulty: q.difficulty_name,
          content: q.question,
          answer: q.reference_answer || '',
          scorePoints: q.scoring_points || []
        }
      })

      console.log('转换后的题目列表:', questions.value)
      console.log('题目类型分布:', questions.value.map(q => q.type))

      // 设置默认激活的tab
      const firstType = questions.value[0]?.type
      if (firstType) {
        activeTab.value = firstType
        console.log('设置激活tab:', activeTab.value)
      }

      // 检查每个类型的题目数量
      typeList.value.forEach(type => {
        const count = getTypeCount(type)
        console.log(`${type}: ${count}题`)
      })

      ElMessage.success(`成功生成${questions.value.length}道面试题`)
    } else {
      ElMessage.warning('未生成任何题目，请调整配置后重试')
    }
  } catch (error) {
    console.error('生成面试题失败:', error)
    ElMessage.error(error.message || '生成失败，请稍后重试')
  } finally {
    generating.value = false
  }
}

// 打开编辑弹窗
const openEditDialog = (item) => {
  editForm.id = item.id
  editForm.type = item.type
  editForm.difficulty = item.difficulty
  editForm.content = item.content
  editForm.answer = item.answer
  editForm.scorePointsText = item.scorePoints.join('\n')
  editDialogVisible.value = true
}

// 保存编辑
const saveEditQuestion = async () => {
  try {
    const valid = await editFormRef.value.validate().catch(() => false)
    if (!valid) return

    const updates = {
      question_content: editForm.content,
      reference_answer: editForm.answer,
      scoring_points: editForm.scorePointsText.split('\n').filter(i => i.trim())
    }

    await updateQuestion(editForm.id, updates)

    // 更新本地数据
    const index = questions.value.findIndex(i => i.id === editForm.id)
    if (index > -1) {
      questions.value[index] = {
        ...questions.value[index],
        type: editForm.type,
        difficulty: editForm.difficulty,
        content: editForm.content,
        answer: editForm.answer,
        scorePoints: updates.scoring_points
      }
    }

    editDialogVisible.value = false
    ElMessage.success('编辑成功')
  } catch (error) {
    console.error('编辑失败:', error)
    ElMessage.error('编辑失败，请稍后重试')
  }
}

// 删除题目
const deleteQuestion = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除该题目？', '提示', { type: 'warning' })
    await deleteQuestionApi(id)
    questions.value = questions.value.filter(i => i.id !== id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }
}

// 复制题目
const copyQuestion = (item) => {
  navigator.clipboard.writeText(item.content)
  ElMessage.success('题目复制成功')
}

// 重新生成
const resetGenerate = () => {
  questions.value = []
  startGenerate()
}

// 保存到题库
const handleSaveToBank = async () => {
  if (questions.value.length === 0) {
    return ElMessage.warning('没有可保存的题目')
  }

  try {
    const questionIds = questions.value.map(q => q.id)
    const res = await saveToQuestionBank(questionIds)

    if (res.code === 0) {
      ElMessage.success(res.data?.message || '保存成功')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请稍后重试')
  }
}

// 导出为Word（待实现）
const handleExportWord = () => {
  ElMessage.info('导出功能开发中...')
}

// 组件挂载时加载数据
onMounted(() => {
  loadPositions()
  loadResumes()
})
</script>

<style scoped>
.interview-generate-page {
  width: 100%;
}

/* 面包屑 & 标题 */
.breadcrumb { margin-bottom: 16px; }
.page-title { font-size: 24px; font-weight: 600; color: #303133; margin: 0 0 20px 0; }

/* 配置卡片 */
.config-card { margin-bottom: 20px; }
.generate-mode { display: flex; align-items: center; }
.generate-mode .label { font-weight: 500; color: #303133; }
.question-form { margin-top: 20px; }
.generate-btn-wrapper { display: flex; justify-content: center; }

/* 结果卡片 */
.result-card { min-height: 400px; }

/* 加载/空状态 */
.loading-container, .empty-container { padding: 40px 0; text-align: center; }
.loading-text { margin-top: 20px; color: #606266; }

/* 结果标签页 */
.result-tabs { margin-bottom: 20px; }

/* 题目列表 */
.question-list { display: flex; flex-direction: column; gap: 12px; }
.question-item { transition: all 0.3s; }

/* 题目头部 */
.question-header { display: flex; justify-content: space-between; align-items: center; }
.left-info { display: flex; align-items: center; }
.num { font-size: 14px; font-weight: 600; color: #303133; }

/* 题目内容 */
.question-content {
  font-size: 15px;
  font-weight: 500;
  line-height: 1.6;
  margin-top: 10px;
  font-family: "Microsoft YaHei", monospace;
}

/* 参考答案/评分要点 */
.answer-content, .score-content {
  color: #606266;
  line-height: 1.8;
  padding: 10px 0;
}
.score-content ol { margin: 0; padding-left: 20px; }

/* 题目操作栏 */
.question-operate { display: flex; justify-content: flex-end; gap: 10px; }

/* 结果底部操作栏 */
.result-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

/* 通用间距类 */
.mt-10 { margin-top: 10px; }
.mt-15 { margin-top: 15px; }
.mt-20 { margin-top: 20px; }
.ml-8 { margin-left: 8px; }
.ml-10 { margin-left: 10px; }
.ml-15 { margin-left: 15px; }
.mr-10 { margin-right: 10px; }
</style>
