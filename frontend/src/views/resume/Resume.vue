<template>
  <div class="resume-page">
    <!-- 页面标题 -->
    <h2 class="page-title">简历管理</h2>

    <!-- 搜索筛选区 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item>
          <el-input
            v-model="searchForm.name"
            placeholder="请输入候选人姓名"
            clearable
            style="width: 180px"
          />
        </el-form-item>

        <el-form-item>
          <el-select
            v-model="searchForm.positionId"
            placeholder="全部岗位"
            filterable
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="pos in positionOptions"
              :key="pos.id"
              :label="pos.name"
              :value="pos.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-select
            v-model="searchForm.education"
            placeholder="学历"
            clearable
            style="width: 120px"
          >
            <el-option
              v-for="edu in educationOptions"
              :key="edu.value"
              :label="edu.label"
              :value="edu.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="工作年限">
          <div class="work-year-range">
            <el-input-number
              v-model="searchForm.minWorkYear"
              placeholder="最小"
              :min="0"
              :max="50"
              style="width: 80px"
            />
            <span class="divider">-</span>
            <el-input-number
              v-model="searchForm.maxWorkYear"
              placeholder="最大"
              :min="0"
              :max="50"
              style="width: 80px"
            />
          </div>
        </el-form-item>

        <el-form-item>
          <el-select
            v-model="searchForm.status"
            placeholder="全部状态"
            clearable
            style="width: 130px"
          >
            <el-option
              v-for="stat in statusOptions"
              :key="stat.value"
              :label="stat.label"
              :value="stat.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="loading">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作按钮区 -->
    <div class="action-bar">
      <el-button type="primary" @click="goUpload">
        <el-icon><Upload /></el-icon>
        上传简历
      </el-button>
      <el-button
        :disabled="!selectedIds.length"
        @click="batchDownload"
      >
        <el-icon><Download /></el-icon>
        批量下载
      </el-button>
      <el-button
        type="danger"
        :disabled="!selectedIds.length"
        @click="batchDelete"
      >
        <el-icon><Delete /></el-icon>
        批量删除
      </el-button>
    </div>

    <!-- 数据表格 -->
    <el-table
      :data="tableData"
      stripe
      border
      v-loading="loading"
      @selection-change="handleSelectionChange"
      class="resume-table"
      style="width: 100%"
    >
      <el-table-column type="selection" width="50" />

      <el-table-column label="候选人" width="120">
        <template #default="{ row }">
          <el-button type="primary" link @click="viewDetail(row)">
            {{ row.candidate_name }}
          </el-button>
        </template>
      </el-table-column>

      <el-table-column label="手机号" width="120">
        <template #default="{ row }">
          {{ formatPhone(row.phone) }}
        </template>
      </el-table-column>

      <el-table-column prop="education" label="学历" width="80" />

      <el-table-column label="工作年限" width="100">
        <template #default="{ row }">
          {{ row.work_years || 0 }}年
        </template>
      </el-table-column>

      <el-table-column
        prop="current_company"
        label="当前公司"
        show-overflow-tooltip
        width="150"
      />

      <el-table-column label="关联岗位" width="150">
        <template #default="{ row }">
          {{ getPositionName(row.position_id) || '未关联' }}
        </template>
      </el-table-column>

      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag
            :type="getStatusTagProps(row.status).type"
            :effect="getStatusTagProps(row.status).effect"
            size="small"
          >
            {{ getStatusTagProps(row.status).text }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="上传时间" width="120">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>

      <el-table-column label="操作" fixed="right" width="180">
        <template #default="{ row }">
          <el-button type="primary" link @click="viewDetail(row)">
            查看
          </el-button>
          <el-button type="primary" link @click="downloadResume(row)">
            下载
          </el-button>
          <el-button type="danger" link @click="deleteResumeItem(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页组件 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSearch"
        @current-change="handleSearch"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Upload, Download, Delete } from '@element-plus/icons-vue'
import {
  getResumeList,
  deleteResume,
  batchDeleteResumes,
  downloadResume as downloadResumeApi,
  batchDownloadResumes as batchDownloadApi
} from '@/api/resume'
import { getPositionList } from '@/api/position'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  name: '',
  positionId: '',
  education: '',
  minWorkYear: null,
  maxWorkYear: null,
  status: ''
})

// 岗位选项（从API获取）
const positionOptions = ref([])

// 学历选项
const educationOptions = [
  { label: '全部', value: '' },
  { label: '大专', value: '大专' },
  { label: '本科', value: '本科' },
  { label: '硕士', value: '硕士' },
  { label: '博士', value: '博士' }
]

// 状态选项
const statusOptions = [
  { label: '全部', value: '' },
  { label: '待筛选', value: 1 },
  { label: '初筛通过', value: 2 },
  { label: '面试中', value: 3 },
  { label: '已录用', value: 4 },
  { label: '已淘汰', value: 5 }
]

// 表格数据与分页
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const selectedIds = ref([])
const loading = ref(false)

// 手机号脱敏处理
const formatPhone = (phone) => {
  if (!phone) return ''
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

// 获取状态标签配置
const getStatusTagProps = (status) => {
  const statusMap = {
    1: { type: 'info', effect: 'light', text: '待筛选' },
    2: { type: 'success', effect: 'light', text: '初筛通过' },
    3: { type: 'warning', effect: 'light', text: '面试中' },
    4: { type: 'success', effect: 'plain', text: '已录用' },
    5: { type: 'danger', effect: 'light', text: '已淘汰' }
  }
  return statusMap[status] || { type: 'info', effect: 'light', text: '未知' }
}

// 获取岗位名称
const getPositionName = (positionId) => {
  if (!positionId) return ''
  const position = positionOptions.value.find(p => p.id === positionId)
  return position ? position.name : ''
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${month}-${day}`
}

// 获取岗位列表
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

// 获取简历列表（调用真实API）
const getResumeListData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchForm.name || undefined,
      position_id: searchForm.positionId || undefined,
      education: searchForm.education || undefined,
      work_years_min: searchForm.minWorkYear,
      work_years_max: searchForm.maxWorkYear,
      status: searchForm.status
    }

    const res = await getResumeList(params)

    if (res.items) {
      tableData.value = res.items
      total.value = res.total
    }
  } catch (error) {
    console.error('获取简历列表失败:', error)
    ElMessage.error('获取简历列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索操作
const handleSearch = () => {
  currentPage.value = 1
  getResumeListData()
}

// 重置操作
const handleReset = () => {
  Object.assign(searchForm, {
    name: '',
    positionId: '',
    education: '',
    minWorkYear: null,
    maxWorkYear: null,
    status: ''
  })
  currentPage.value = 1
  getResumeListData()
}

// 表格多选事件
const handleSelectionChange = (val) => {
  selectedIds.value = val.map(item => item.id)
}

// 跳转到上传简历页
const goUpload = () => {
  router.push('/resume/upload')
}

// 查看简历详情
const viewDetail = (row) => {
  router.push(`/resume/detail/${row.id}`)
}

// 下载简历
const downloadResume = async (row) => {
  try {
    const blob = await downloadResumeApi(row.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = row.file_name || `${row.candidate_name}_简历`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

// 删除单条简历
const deleteResumeItem = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除候选人「${row.candidate_name}」的简历吗？`,
      '操作确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteResume(row.id)
    ElMessage.success('删除成功')
    getResumeListData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 批量下载简历
const batchDownload = async () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要下载的简历')
    return
  }

  try {
    const blob = await batchDownloadApi(selectedIds.value)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'resumes.zip'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success(`开始下载 ${selectedIds.value.length} 份简历`)
  } catch (error) {
    console.error('批量下载失败:', error)
    ElMessage.error('批量下载失败')
  }
}

// 批量删除简历
const batchDelete = async () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要删除的简历')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 份简历吗？`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await batchDeleteResumes(selectedIds.value)
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    getResumeListData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

// 页面加载时初始化数据
onMounted(() => {
  loadPositions()
  getResumeListData()
})
</script>

<style scoped>
.resume-page {
  width: 100%;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
}

.search-card {
  margin-bottom: 16px;
}

.search-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

/* 工作年限范围样式 */
.work-year-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.divider {
  color: #909399;
}

.action-bar {
  margin-bottom: 16px;
}

.resume-table {
  margin-bottom: 16px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 8px 0;
}

/* 表格行hover高亮 */
:deep(.el-table__row:hover > td) {
  background-color: #f5f7fa !important;
}

/* 操作列按钮间距 */
:deep(.el-button + .el-button) {
  margin-left: 8px;
}
</style>
