<template>
  <div class="interview-summary-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item>面试管理</el-breadcrumb-item>
      <el-breadcrumb-item>面试录音</el-breadcrumb-item>
      <el-breadcrumb-item>面试摘要</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 1. 顶部信息栏卡片 -->
    <el-card class="top-info-card" shadow="never">
      <div class="left-info">
        <h1 class="candidate-name">{{ summaryInfo.candidateName }}</h1>
        <el-tag type="primary" size="large" class="position-tag">
          {{ summaryInfo.positionName }}
        </el-tag>
      </div>
      <div class="right-info">
        <div class="info-item">
          <span class="label">面试日期：</span>
          <span class="value">{{ summaryInfo.interviewDate }}</span>
        </div>
        <div class="info-item">
          <span class="label">面试时长：</span>
          <span class="value">{{ summaryInfo.duration }}</span>
        </div>
      </div>
    </el-card>

    <!-- 2. 主内容区卡片列表 -->
    <div class="content-wrapper">
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
            <el-button size="small" type="primary" @click="saveSummary">保存</el-button>
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
              <p class="answer">A: {{ item.answer }}</p>
              <div class="quality">
                <span>回答质量：</span>
                <el-tag :type="item.qualityType" size="small">
                  {{ item.qualityText }}
                </el-tag>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
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
              <ul class="list">
                <li v-for="(item, index) in summaryInfo.advantages" :key="index">
                  <el-icon color="#67c23a" size="14" class="mr-8"><Check /></el-icon>
                  {{ item }}
                </li>
              </ul>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="concern-box">
              <div class="box-title">
                <el-icon color="#e6a23c" size="18"><Warning /></el-icon>
                <span>疑虑点</span>
              </div>
              <ul class="list">
                <li v-for="(item, index) in summaryInfo.concerns" :key="index">
                  <el-icon color="#e6a23c" size="14" class="mr-8"><Warning /></el-icon>
                  {{ item }}
                </li>
              </ul>
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
        <div v-else class="empty-tip">候选人未提问</div>
      </el-card>
    </div>

    <!-- 3. 右侧悬浮操作栏 -->
    <div class="float-operate">
      <el-card shadow="never" class="float-card">
        <div class="btn-group">
          <el-button block @click="regenerateSummary">重新生成摘要</el-button>
          <el-button block type="primary" class="mt-8">生成评价</el-button>
          <el-button block class="mt-8" @click="goBackRecord">返回录音</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Edit,
  Check,
  Warning,
  Refresh,
  Document,
  Back
} from '@element-plus/icons-vue'

// 编辑状态
const editMode = ref(false)
const editTarget = ref('')
const editSummary = ref('')
const activeCollapse = ref([0])

// 面试摘要数据（Mock）
const summaryInfo = reactive({
  candidateName: '张三',
  positionName: '高级前端开发工程师',
  interviewDate: '2025-01-20 14:00-15:30',
  duration: '1小时30分钟',
  summary: '本次面试主要考察候选人的前端技术栈、项目经验和解决问题的能力。候选人拥有5年前端开发经验，熟练掌握Vue3、React、TypeScript等核心技术，具备大型企业级项目开发经验。技术基础扎实，对前端工程化、性能优化有深入理解。沟通能力良好，逻辑思维清晰，符合岗位核心要求。在微前端架构和低代码平台方面有实践经验，是岗位的优质候选人。',
  // 核心问答
  qaList: [
    {
      question: '请详细介绍Vue3的响应式原理？',
      answer: 'Vue3基于Proxy实现数据劫持，相比Vue2的Object.defineProperty，支持监听数组、新增属性，性能更高。在初始化时创建响应式对象，收集依赖，数据变化时触发更新。',
      qualityType: 'success',
      qualityText: '优秀'
    },
    {
      question: '项目中遇到的最大性能问题是什么，如何解决的？',
      answer: '遇到过首屏加载过慢的问题，通过路由懒加载、代码分割、图片懒加载、开启gzip压缩等方式优化，首屏加载速度提升60%。',
      qualityType: 'primary',
      qualityText: '良好'
    },
    {
      question: '如何理解前端工程化？',
      answer: '前端工程化是指用工程化的思想管理前端项目，包括模块化、组件化、规范化、自动化，提升开发效率和代码质量。',
      qualityType: 'info',
      qualityText: '一般'
    }
  ],
  // 能力标签
  techSkills: ['Vue3', 'React', 'TypeScript', 'Vite', '性能优化'],
  softSkills: ['沟通能力强', '逻辑清晰', '学习能力强', '团队协作'],
  // 亮点与疑虑
  advantages: ['5年大厂前端经验', '技术栈全面', '项目经验丰富', '沟通能力优秀'],
  concerns: ['微前端经验不足', '低代码平台实践较少'],
  // 候选人提问
  questions: ['公司的技术栈规划是什么？', '岗位的晋升机制是怎样的？']
})

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
const saveSummary = () => {
  summaryInfo.summary = editSummary.value
  editMode.value = false
  editTarget.value = ''
  ElMessage.success('概要保存成功')
}

// 重新生成摘要
const regenerateSummary = () => {
  ElMessage.success('AI正在重新生成面试摘要...')
}

// 返回录音页面
const goBackRecord = () => {
  ElMessage.success('返回面试录音管理页面')
}
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
}

.info-item .label {
  color: #606266;
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