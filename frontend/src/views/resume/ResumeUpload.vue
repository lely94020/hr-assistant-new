<template>
  <div class="resume-upload-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/resume' }">简历管理</el-breadcrumb-item>
      <el-breadcrumb-item>上传简历</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 页面标题 -->
    <h2 class="page-title">上传简历</h2>

    <!-- 拖拽上传区域 -->
    <el-card class="upload-card" shadow="never">
      <el-upload
        ref="uploadRef"
        drag
        multiple
        :auto-upload="false"
        accept=".pdf,.doc,.docx,.zip"
        :limit="100"
        :file-list="fileList"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :on-exceed="handleExceed"
        class="upload-dragger"
      >
        <el-icon class="upload-icon"><Upload /></el-icon>
        <div class="upload-text">将文件拖到此处，或点击上传</div>
        <div class="upload-tip">支持 PDF、Word、ZIP 格式，单个文件不超过10MB，单次最多100份</div>
      </el-upload>
    </el-card>

    <!-- 上传配置区域 -->
    <el-card class="config-card" shadow="never">
      <template #title>
        <span>上传配置</span>
      </template>
      <el-form :model="config" inline class="config-form">
        <el-form-item label="关联岗位">
          <el-select
            v-model="config.positionId"
            placeholder="可选择关联的岗位"
            clearable
            style="width: 220px"
          >
            <el-option
              v-for="item in positionOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 已选文件列表 -->
    <el-card class="table-card" shadow="never" title="已选文件" v-if="fileList.length">
      <el-table :data="fileList" border stripe style="width: 100%">
        <el-table-column prop="name" label="文件名" show-overflow-tooltip />
        <el-table-column label="文件大小">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="上传进度">
          <template #default="{ row }">
            <el-progress
              v-if="row.status === 'uploading'"
              :percentage="row.progress"
              stroke-width="6"
              size="small"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button
              type="danger"
              link
              icon="Delete"
              @click="handleFileRemove(row)"
              :disabled="row.status !== 'waiting'"
            >
              删除
            </el-button>
            <el-button
              type="primary"
              link
              v-if="row.status === 'failed'"
              @click="showErrorReason(row)"
            >
              查看原因
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 底部操作区域 -->
    <div class="action-footer" v-if="fileList.length">
      <div class="stats" v-if="uploadComplete">
        上传完成：成功 <span class="success-num">{{ uploadResult.success }}</span> 份，
        失败 <span class="failed-num">{{ uploadResult.failed }}</span> 份
      </div>
      <div class="action-buttons">
        <el-button
          type="primary"
          size="large"
          icon="Upload"
          @click="handleStartUpload"
          :loading="uploading"
          :disabled="uploading || uploadComplete"
        >
          开始上传
        </el-button>
        <el-button
          size="large"
          icon="Refresh"
          @click="handleClearList"
          :disabled="uploading"
        >
          清空列表
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Delete } from '@element-plus/icons-vue'
import { uploadResumes } from '@/api/resume'
import { getPositionList } from '@/api/position'

const router = useRouter()
const uploadRef = ref(null)

// 岗位选项
const positionOptions = ref([])

// 上传配置
const config = reactive({
  positionId: null
})

// 文件列表
const fileList = ref([])
// 上传状态
const uploading = ref(false)
const uploadComplete = ref(false)
// 上传结果
const uploadResult = reactive({
  total: 0,
  success: 0,
  failed: 0,
  results: []
})

// 文件状态映射
const statusMap = {
  waiting: { text: '待上传', type: 'info' },
  uploading: { text: '上传中', type: 'primary' },
  success: { text: '成功', type: 'success' },
  failed: { text: '失败', type: 'danger' }
}

// 获取状态标签类型
const getStatusTagType = (status) => statusMap[status]?.type || 'info'
// 获取状态文本
const getStatusText = (status) => statusMap[status]?.text || '未知'

// 文件大小格式化
const formatFileSize = (size) => {
  if (!size) return '0KB'
  if (size < 1024) return size + 'B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + 'KB'
  return (size / (1024 * 1024)).toFixed(1) + 'MB'
}

// 加载岗位列表
const loadPositions = async () => {
  try {
    const res = await getPositionList({ page: 1, page_size: 100 })
    if (res.items) {
      positionOptions.value = res.items.map(item => ({
        id: item.id,
        name: item.name
      }))
    }
  } catch (error) {
    console.error('获取岗位列表失败:', error)
  }
}

// 文件选择/变化事件
const handleFileChange = (file) => {
  // 校验文件大小
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (file.size > maxSize) {
    ElMessage.error(`文件 ${file.name} 超过10MB限制`)
    handleFileRemove(file)
    return
  }

  // 校验文件格式
  const allowedExts = ['.pdf', '.doc', '.docx', '.zip']
  const ext = '.' + file.name.split('.').pop().toLowerCase()
  if (!allowedExts.includes(ext)) {
    ElMessage.error(`文件 ${file.name} 格式不支持`)
    handleFileRemove(file)
    return
  }

  // 初始化文件状态
  file.status = 'waiting'
  file.progress = 0
  file.errorReason = ''
}

// 文件超出限制
const handleExceed = () => {
  ElMessage.warning('单次最多上传100份简历')
}

// 移除文件
const handleFileRemove = (file) => {
  const index = fileList.value.findIndex(item => item.uid === file.uid)
  if (index > -1) {
    fileList.value.splice(index, 1)
  }
}

// 清空文件列表
const handleClearList = () => {
  fileList.value = []
  uploadComplete.value = false
  uploadResult.total = 0
  uploadResult.success = 0
  uploadResult.failed = 0
  uploadResult.results = []
}

// 开始批量上传
const handleStartUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploading.value = true
  uploadComplete.value = false

  try {
    // 构建 FormData
    const formData = new FormData()

    // 添加所有文件
    fileList.value.forEach(file => {
      formData.append('files', file.raw)
    })

    // 添加岗位ID（如果选择了）
    if (config.positionId) {
      formData.append('position_id', config.positionId)
    }

    // 调用上传API
    const res = await uploadResumes(formData)

    // 更新上传结果
    uploadResult.total = res.total
    uploadResult.success = res.success
    uploadResult.failed = res.failed
    uploadResult.results = res.results

    // 更新文件列表状态
    res.results.forEach((result, index) => {
      if (fileList.value[index]) {
        fileList.value[index].status = result.status === 'success' ? 'success' : 'failed'
        fileList.value[index].progress = 100
        fileList.value[index].errorReason = result.error || ''
        fileList.value[index].resume_id = result.resume_id
      }
    })

    uploadComplete.value = true

    if (res.failed === 0) {
      ElMessage.success(`上传成功！共 ${res.success} 份简历`)
    } else {
      ElMessage.warning(`上传完成：成功 ${res.success} 份，失败 ${res.failed} 份`)
    }

    // 3秒后跳转到简历列表
    setTimeout(() => {
      router.push('/resume')
    }, 3000)

  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('上传失败，请重试')

    // 标记所有文件为失败
    fileList.value.forEach(file => {
      if (file.status === 'uploading') {
        file.status = 'failed'
        file.errorReason = error.message || '网络错误'
      }
    })
  } finally {
    uploading.value = false
  }
}

// 查看失败原因
const showErrorReason = (row) => {
  ElMessageBox.alert(row.errorReason || '未知错误', '上传失败原因', {
    confirmButtonText: '确定',
    type: 'error'
  })
}

// 初始化
loadPositions()
</script>

<style scoped>
.resume-upload-page {
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
  margin: 0 0 16px 0;
}

/* 上传卡片 */
.upload-card {
  margin-bottom: 16px;
}

/* 拖拽上传区域样式 */
:deep(.upload-dragger .el-upload__dragger) {
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  transition: all 0.3s;
}

/* 拖拽区hover效果 */
:deep(.upload-dragger .el-upload__dragger:hover) {
  border-color: var(--el-color-primary);
}

.upload-icon {
  font-size: 48px;
  color: var(--el-color-primary);
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
}

/* 配置卡片 */
.config-card {
  margin-bottom: 16px;
}

.config-form {
  margin-top: 8px;
}

/* 表格卡片 */
.table-card {
  margin-bottom: 16px;
}

/* 底部操作区 */
.action-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}

.stats {
  font-size: 14px;
  color: #606266;
}

.success-num {
  color: var(--el-color-success);
  font-weight: 600;
}

.failed-num {
  color: var(--el-color-danger);
  font-weight: 600;
}

.action-buttons {
  display: flex;
  gap: 16px;
}
</style>
