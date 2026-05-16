<template>
  <div class="evaluation-list-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item>面试管理</el-breadcrumb-item>
      <el-breadcrumb-item>面试评价</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 搜索筛选区 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="候选人姓名">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入姓名"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="应聘岗位">
          <el-input
            v-model="searchForm.position"
            placeholder="请输入岗位"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="评价等级">
          <el-select
            v-model="searchForm.level"
            placeholder="请选择等级"
            clearable
            style="width: 150px"
          >
            <el-option label="强烈推荐" value="强烈推荐" />
            <el-option label="推荐" value="推荐" />
            <el-option label="可考虑" value="可考虑" />
            <el-option label="不推荐" value="不推荐" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
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

    <!-- 评价列表 -->
    <el-card class="list-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="evaluationList"
        stripe
        style="width: 100%"
        @row-click="handleRowClick"
      >
        <el-table-column prop="candidate_name" label="候选人" width="120">
          <template #default="{ row }">
            <div class="candidate-cell">
              <el-avatar :size="32" :src="row.avatar">{{ row.candidate_name?.charAt(0) }}</el-avatar>
              <span class="name">{{ row.candidate_name }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="position" label="应聘岗位" min-width="150" show-overflow-tooltip />

        <el-table-column prop="total_score" label="综合得分" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getScoreType(row.total_score)" size="large">
              {{ row.total_score }}分
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="level" label="推荐等级" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="ai_comment" label="AI评语" min-width="200" show-overflow-tooltip />

        <el-table-column prop="created_at" label="评价时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click.stop="viewDetail(row.id)">
              <el-icon><View /></el-icon>
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Refresh, View } from '@element-plus/icons-vue'
import { getEvaluationList } from '@/api/evaluation'

const router = useRouter()
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  name: '',
  position: '',
  level: ''
})

// 分页参数
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 评价列表
const evaluationList = ref([])

// 获取评价列表
const fetchEvaluationList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    }

    const res = await getEvaluationList(params)
    if (res.code === 0) {
      evaluationList.value = res.data.items || []
      pagination.total = res.data.total || 0
    }
  } catch (error) {
    console.error('获取评价列表失败:', error)
    ElMessage.error('获取评价列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchEvaluationList()
}

// 重置
const handleReset = () => {
  searchForm.name = ''
  searchForm.position = ''
  searchForm.level = ''
  pagination.page = 1
  fetchEvaluationList()
}

// 行点击
const handleRowClick = (row) => {
  viewDetail(row.id)
}

// 查看详情
const viewDetail = (id) => {
  router.push(`/evaluation/detail/${id}`)
}

// 分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchEvaluationList()
}

// 页码变化
const handlePageChange = (page) => {
  pagination.page = page
  fetchEvaluationList()
}

// 获取分数类型
const getScoreType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 75) return 'primary'
  if (score >= 60) return 'info'
  return 'danger'
}

// 获取等级类型
const getLevelType = (level) => {
  const types = {
    '强烈推荐': 'success',
    '推荐': 'primary',
    '可考虑': 'info',
    '不推荐': 'danger'
  }
  return types[level] || 'info'
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchEvaluationList()
})
</script>

<style scoped>
.evaluation-list-page {
  width: 100%;
}

.breadcrumb {
  margin-bottom: 16px;
}

.filter-card {
  margin-bottom: 16px;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
}

.list-card {
  min-height: 500px;
}

.candidate-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name {
  font-weight: 500;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>