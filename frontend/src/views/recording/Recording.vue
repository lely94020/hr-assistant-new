<template>
  <div class="interview-record-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item>面试管理</el-breadcrumb-item>
      <el-breadcrumb-item>面试录音管理</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 1. 顶部操作区 -->
    <div class="top-operate">
      <!-- 左侧：上传录音按钮 -->
      <el-button type="primary" icon="Upload" @click="openUploadDialog">
        上传录音
      </el-button>

      <!-- 右侧：筛选条件 -->
      <div class="filter-group">
        <el-select
          v-model="filter.resumeId"
          filterable
          placeholder="全部候选人"
          style="width: 180px; margin-right: 10px"
          @change="handleFilterChange"
        >
          <el-option
            v-for="item in candidateList"
            :key="item.id"
            :label="item.candidate_name"
            :value="item.id"
          />
        </el-select>
        <el-select
          v-model="filter.transcriptStatus"
          placeholder="转写状态"
          style="width: 140px"
          @change="handleFilterChange"
        >
          <el-option label="全部" value="" />
          <el-option label="未转写" :value="0" />
          <el-option label="转写中" :value="1" />
          <el-option label="已完成" :value="2" />
          <el-option label="转写失败" :value="3" />
        </el-select>
      </div>
    </div>

    <!-- 2. 录音列表表格 -->
    <el-table
      :data="tableData"
      stripe
      border
      style="width: 100%; margin-top: 16px"
      row-class-name="table-row"
      v-loading="loading"
    >
      <el-table-column prop="file_name" label="文件名" show-overflow-tooltip />
      <el-table-column label="关联候选人">
        <template #default="{ row }">
          <el-button
            type="primary"
            link
            @click="goToResume(row.resume_id)"
          >
            {{ getCandidateName(row.resume_id) }}
          </el-button>
        </template>
      </el-table-column>
      <el-table-column label="关联岗位">
        <template #default="{ row }">
          {{ getPositionName(row.position_id) }}
        </template>
      </el-table-column>
      <el-table-column
        label="时长"
      >
        <template #default="{ row }">
          {{ formatDuration(row.duration) }}
        </template>
      </el-table-column>
      <el-table-column
        label="文件大小"
      >
        <template #default="{ row }">
          {{ formatFileSize(row.file_size) }}
        </template>
      </el-table-column>
      <el-table-column label="转写状态">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.transcript_status)">
            <el-icon
              v-if="row.transcript_status === 1"
              class="el-icon-loading"
              style="margin-right: 4px"
            />
            {{ getStatusText(row.transcript_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="上传时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column
        label="操作"
        fixed="right"
        width="400"
      >
        <template #default="{ row }">
          <el-button icon="VideoPlay" link @click="openPlayDialog(row)">
            播放
          </el-button>
          <el-button
            icon="Document"
            link
            v-if="row.transcript_status === 0 || row.transcript_status === 3"
            @click="startTranscribe(row)"
          >
            转写
          </el-button>
          <el-button
            link
            v-if="row.transcript_status === 2"
            @click="openScriptDialog(row)"
          >
            查看文字稿
          </el-button>
          <el-button
            link
            type="primary"
            v-if="row.transcript_status === 2"
            @click="goToSummary(row)"
          >
            生成摘要
          </el-button>
          <el-button
            icon="Delete"
            link
            type="danger"
            @click="deleteRecord(row.id)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 3. 分页组件 -->
    <div class="pagination" style="text-align: right; margin-top: 16px">
      <el-pagination
        v-model:current-page="page.pageNum"
        v-model:page-size="page.pageSize"
        :total="page.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- ==================== 弹窗区域 ==================== -->
    <!-- 4. 上传录音弹窗 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传面试录音"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadRules"
        label-width="100px"
      >
        <!-- 拖拽上传 -->
        <el-upload
          ref="uploadRef"
          drag
          :auto-upload="false"
          accept=".mp3,.wav,.m4a,.aac"
          :on-change="handleFileChange"
          :limit="1"
          class="upload-dragger"
        >
          <el-icon class="icon"><Upload /></el-icon>
          <div class="text">将录音文件拖到此处，或点击上传</div>
          <div class="tip">支持 MP3、WAV、M4A、AAC 格式，最大500MB</div>
        </el-upload>

        <el-form-item label="关联候选人" prop="resume_id">
          <el-select v-model="uploadForm.resume_id" style="width: 100%">
            <el-option
              v-for="item in candidateList"
              :key="item.id"
              :label="item.candidate_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关联岗位">
          <el-select v-model="uploadForm.position_id" style="width: 100%">
            <el-option
              v-for="item in positionList"
              :key="item.id"
              :label="item.position_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="面试日期">
          <el-date-picker
            v-model="uploadForm.interview_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
            placeholder="选择日期"
          />
        </el-form-item>
        <el-form-item label="面试官">
          <el-input v-model="uploadForm.interviewer" placeholder="请输入面试官姓名" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploadLoading" @click="submitUpload">
          确认上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 5. 播放录音弹窗 -->
    <el-dialog
      v-model="playDialogVisible"
      title="播放录音"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="play-info" v-if="currentRecord">
        <p><strong>文件名：</strong>{{ currentRecord.file_name }}</p>
        <p><strong>候选人：</strong>{{ getCandidateName(currentRecord.resume_id) }}</p>
        <p><strong>时长：</strong>{{ formatDuration(currentRecord.duration) }}</p>
      </div>

      <!-- 音频播放器 -->
      <div class="audio-player" v-if="currentRecord">
        <audio
          ref="audioRef"
          :src="getAudioUrl(currentRecord.file_path)"
          controls
          @timeupdate="updatePlayTime"
          class="audio-element"
        />
      </div>

      <template #footer>
        <el-button @click="closePlayDialog">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 6. 文字稿查看弹窗 -->
    <el-dialog
      v-model="scriptDialogVisible"
      title="面试文字稿"
      width="70%"
      :close-on-click-modal="false"
    >
      <div class="script-header" v-if="currentRecord">
        <span>候选人：{{ getCandidateName(currentRecord.resume_id) }}</span>
        <span>岗位：{{ getPositionName(currentRecord.position_id) }}</span>
        <span>时长：{{ formatDuration(currentRecord.duration) }}</span>
      </div>

      <!-- 文字稿内容 -->
      <div class="script-content">
        <!-- 只读模式 -->
        <div
          v-if="!editMode"
          class="script-read"
          v-loading="scriptLoading"
        >{{ scriptContent }}</div>
        <!-- 编辑模式 -->
        <el-input
          v-else
          v-model="scriptContent"
          type="textarea"
          :rows="20"
          class="script-edit"
        />
      </div>

      <template #footer>
        <el-button @click="handleEditToggle">
          {{ editMode ? '保存' : '编辑' }}
        </el-button>
        <el-button @click="scriptDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload,
  VideoPlay,
  Document,
  Delete
} from '@element-plus/icons-vue'
import {
  uploadRecording,
  getRecordingList,
  getRecordingDetail,
  startTranscribe as apiStartTranscribe,
  getTranscript,
  updateTranscript as apiUpdateTranscript,
  deleteRecording
} from '@/api/recording'
import { getResumeList } from '@/api/resume'
import { getPositionList } from '@/api/position'

// 基础数据
const router = useRouter()
const candidateList = ref([])
const positionList = ref([])

// 筛选条件
const filter = reactive({
  resumeId: '',
  transcriptStatus: ''
})

// 分页
const page = reactive({
  pageNum: 1,
  pageSize: 10,
  total: 0
})

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 弹窗显隐
const uploadDialogVisible = ref(false)
const playDialogVisible = ref(false)
const scriptDialogVisible = ref(false)
const editMode = ref(false) // 文字稿编辑模式

// 当前选中的录音
const currentRecord = ref(null)
// 文字稿内容
const scriptContent = ref('')
// 文字稿加载状态
const scriptLoading = ref(false)

// ==================== 工具方法 ====================
// 格式化时长（秒 → HH:MM:SS）
const formatDuration = (seconds) => {
  if (!seconds && seconds !== 0) return '-'
  const h = Math.floor(seconds / 3600).toString().padStart(2, '0')
  const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0')
  const s = (seconds % 60).toString().padStart(2, '0')
  return `${h}:${m}:${s}`
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 MB'
  const mb = (bytes / (1024 * 1024)).toFixed(1)
  return `${mb} MB`
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return dateStr.replace('T', ' ').substring(0, 19)
}

// 转写状态标签类型
const getStatusTagType = (status) => {
  const map = { 0: 'info', 1: 'primary', 2: 'success', 3: 'danger' }
  return map[status] || 'info'
}

// 转写状态文本
const getStatusText = (status) => {
  const map = { 0: '未转写', 1: '转写中', 2: '已完成', 3: '转写失败' }
  return map[status] || '未知'
}

// 获取候选人姓名
const getCandidateName = (resumeId) => {
  const candidate = candidateList.value.find(item => item.id === resumeId)
  return candidate ? candidate.candidate_name : '未知'
}

// 获取岗位名称
const getPositionName = (positionId) => {
  if (!positionId) return '-'
  const position = positionList.value.find(item => item.id === positionId)
  return position ? position.position_name : '未知'
}

// 获取音频URL
const getAudioUrl = (filePath) => {
  if (!filePath) return ''
  return `http://localhost:8000/${filePath}`
}

// 跳转到简历详情
const goToResume = (resumeId) => {
  window.open(`/resume/detail/${resumeId}`, '_blank')
}

// 跳转到面试摘要（生成评价入口）
const goToSummary = (row) => {
  router.push(`/evaluation/summary/${row.id}`)
}

// ==================== 数据加载 ====================
// 加载候选人列表
const loadCandidateList = async () => {
  try {
    const res = await getResumeList({ skip: 0, limit: 1000 })
    candidateList.value = res.items || res
  } catch (error) {
    console.error('加载候选人列表失败:', error)
  }
}

// 加载岗位列表
const loadPositionList = async () => {
  try {
    const res = await getPositionList({ skip: 0, limit: 1000 })
    positionList.value = res.items || res
  } catch (error) {
    console.error('加载岗位列表失败:', error)
  }
}

// 加载录音列表
const loadRecordingList = async () => {
  loading.value = true
  try {
    const params = {
      skip: (page.pageNum - 1) * page.pageSize,
      limit: page.pageSize
    }

    if (filter.resumeId) {
      params.resume_id = filter.resumeId
    }
    if (filter.transcriptStatus !== '' && filter.transcriptStatus !== null) {
      params.transcript_status = filter.transcriptStatus
    }

    const res = await getRecordingList(params)
    tableData.value = res
    page.total = res.length // 实际应该从后端返回总数

  } catch (error) {
    ElMessage.error('加载录音列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 筛选变化
const handleFilterChange = () => {
  page.pageNum = 1
  loadRecordingList()
}

// 分页变化
const handleSizeChange = (val) => {
  page.pageSize = val
  page.pageNum = 1
  loadRecordingList()
}

const handleCurrentChange = (val) => {
  page.pageNum = val
  loadRecordingList()
}

// ==================== 上传录音 ====================
const uploadFormRef = ref(null)
const uploadRef = ref(null)
const uploadLoading = ref(false)
const uploadForm = reactive({
  resume_id: '',
  position_id: '',
  interview_date: '',
  interviewer: '',
  file: null
})
const uploadRules = ref({
  resume_id: [{ required: true, message: '请选择关联候选人', trigger: 'change' }]
})

const openUploadDialog = () => {
  uploadDialogVisible.value = true
  // 重置表单
  uploadForm.resume_id = ''
  uploadForm.position_id = ''
  uploadForm.interview_date = ''
  uploadForm.interviewer = ''
  uploadForm.file = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const handleFileChange = (file) => {
  // 校验文件格式
  const allowedTypes = ['.mp3', '.wav', '.m4a', '.aac']
  const fileExt = '.' + file.name.split('.').pop().toLowerCase()

  if (!allowedTypes.includes(fileExt)) {
    ElMessage.error('仅支持MP3、WAV、M4A、AAC格式')
    uploadRef.value.handleRemove(file)
    return
  }

  // 校验文件大小 (500MB)
  const maxSize = 500 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过500MB')
    uploadRef.value.handleRemove(file)
    return
  }

  uploadForm.file = file.raw
}

const submitUpload = async () => {
  if (!uploadFormRef.value) return

  await uploadFormRef.value.validate(async (valid) => {
    if (!valid) return

    if (!uploadForm.file) {
      ElMessage.error('请选择要上传的文件')
      return
    }

    uploadLoading.value = true

    try {
      const formData = new FormData()
      formData.append('file', uploadForm.file)
      formData.append('resume_id', uploadForm.resume_id)

      if (uploadForm.position_id) {
        formData.append('position_id', uploadForm.position_id)
      }
      if (uploadForm.interview_date) {
        formData.append('interview_date', uploadForm.interview_date)
      }
      if (uploadForm.interviewer) {
        formData.append('interviewer', uploadForm.interviewer)
      }

      await uploadRecording(formData)
      ElMessage.success('录音上传成功')
      uploadDialogVisible.value = false
      loadRecordingList()
    } catch (error) {
      ElMessage.error(error.message || '上传失败')
    } finally {
      uploadLoading.value = false
    }
  })
}

// ==================== 播放录音 ====================
const audioRef = ref(null)
const openPlayDialog = (row) => {
  currentRecord.value = row
  playDialogVisible.value = true
}

const closePlayDialog = () => {
  if (audioRef.value) {
    audioRef.value.pause()
  }
  playDialogVisible.value = false
}

const updatePlayTime = () => {}

// ==================== 转写/文字稿 ====================
const startTranscribe = async (row) => {
  try {
    await ElMessageBox.confirm('确定开始转写该录音？', '提示', {
      type: 'info',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })

    await apiStartTranscribe(row.id)
    ElMessage.success('开始转写，请稍后刷新查看结果')

    // 3秒后刷新列表
    setTimeout(() => {
      loadRecordingList()
    }, 3000)

  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '启动转写失败')
    }
  }
}

const openScriptDialog = async (row) => {
  currentRecord.value = row
  editMode.value = false
  scriptDialogVisible.value = true
  scriptLoading.value = true

  try {
    const res = await getTranscript(row.id)
    scriptContent.value = res.transcript || ''
  } catch (error) {
    ElMessage.error('获取文字稿失败')
    console.error(error)
  } finally {
    scriptLoading.value = false
  }
}

const handleEditToggle = async () => {
  if (editMode.value) {
    // 保存
    try {
      await apiUpdateTranscript(currentRecord.value.id, scriptContent.value)
      ElMessage.success('保存成功')
      editMode.value = false
    } catch (error) {
      ElMessage.error('保存失败')
      console.error(error)
    }
  } else {
    // 进入编辑模式
    editMode.value = true
  }
}

// ==================== 删除 ====================
const deleteRecord = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除该录音文件？', '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })

    await deleteRecording(id)
    ElMessage.success('删除成功')
    loadRecordingList()

  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

onMounted(() => {
  loadCandidateList()
  loadPositionList()
  loadRecordingList()
})
</script>

<style scoped>
.interview-record-page {
  width: 100%;
}

/* 面包屑 */
.breadcrumb {
  margin-bottom: 16px;
}

/* 顶部操作区 */
.top-operate {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
}

/* 表格行高 */
.table-row {
  line-height: 40px !important;
}

/* 上传拖拽区 */
.upload-dragger {
  margin-bottom: 20px;
}
.upload-dragger :deep(.el-upload__dragger) {
  padding: 20px 0;
}
.upload-dragger .icon {
  font-size: 36px;
  color: var(--el-color-primary);
}
.upload-dragger .text {
  margin: 10px 0 5px;
}
.upload-dragger .tip {
  font-size: 12px;
  color: #909399;
}

/* 音频播放器 */
.audio-player {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}
.audio-element {
  width: 100%;
}

/* 文字稿头部 */
.script-header {
  display: flex;
  gap: 20px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 15px;
}

/* 文字稿内容 */
.script-read {
  padding: 15px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  min-height: 400px;
  line-height: 1.8;
  white-space: pre-wrap;
}
.script-edit {
  min-height: 400px;
}
</style>
