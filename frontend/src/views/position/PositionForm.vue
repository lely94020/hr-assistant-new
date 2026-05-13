<template>
  <div class="position-form-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/position' }">岗位管理</el-breadcrumb-item>
      <el-breadcrumb-item>{{ isEdit ? '编辑岗位' : '新建岗位' }}</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 表单卡片 -->
    <el-card shadow="never" class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="right"
        class="position-form"
      >
        <!-- 岗位名称 -->
        <el-form-item label="岗位名称" prop="position_name">
          <el-input
            v-model="form.position_name"
            placeholder="请输入岗位名称"
            maxlength="100"
            show-word-limit
            style="width: 100%"
          />
        </el-form-item>

        <!-- 所属部门 -->
        <el-form-item label="所属部门" prop="department">
          <el-select
            v-model="form.department"
            placeholder="请选择部门"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="dept in departmentOptions"
              :key="dept"
              :label="dept"
              :value="dept"
            />
          </el-select>
        </el-form-item>

        <!-- 工作地点 -->
        <el-form-item label="工作地点">
          <el-input
            v-model="form.location"
            placeholder="请输入工作地点"
            style="width: 100%"
          />
        </el-form-item>

        <!-- 招聘人数 -->
        <el-form-item label="招聘人数">
          <el-input-number
            v-model="form.recruitCount"
            :min="1"
            :max="100"
            :step="1"
          />
        </el-form-item>

        <!-- 薪资范围 -->
        <el-form-item label="薪资范围">
          <div class="salary-range">
            <el-input
              v-model.number="form.minSalary"
              placeholder="最低"
              style="width: 100px"
            />
            <span class="divider">-</span>
            <el-input
              v-model.number="form.maxSalary"
              placeholder="最高"
              style="width: 100px"
            />
            <span class="unit">K</span>
          </div>
        </el-form-item>

        <!-- 岗位职责 -->
        <el-form-item label="岗位职责" prop="job_description">
          <el-input
            v-model="form.job_description"
            type="textarea"
            :rows="6"
            placeholder="请输入岗位职责描述..."
            maxlength="5000"
            show-word-limit
            style="width: 100%"
          />
        </el-form-item>

        <!-- 任职要求 -->
        <el-form-item label="任职要求" prop="requirements">
          <el-input
            v-model="form.requirements"
            type="textarea"
            :rows="6"
            placeholder="请输入任职要求..."
            maxlength="5000"
            show-word-limit
            style="width: 100%"
          />
        </el-form-item>

        <!-- 岗位状态 -->
        <el-form-item label="岗位状态">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">开放招聘</el-radio>
            <el-radio :label="2">暂停招聘</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 底部按钮 -->
        <el-form-item class="form-actions">
          <el-button @click="goBack">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="loading">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const formRef = ref(null)
const loading = ref(false)

// 编辑模式判断（根据路由是否有id参数）
const isEdit = computed(() => !!route.params.id)

// 部门选项
const departmentOptions = ['技术部', '产品部', '设计部', '市场部', '人力资源部', '财务部']

// 表单数据
const form = reactive({
  position_name: '',
  department: '',
  location: '',
  recruitCount: 1,
  minSalary: null,
  maxSalary: null,
  job_description: '',
  requirements: '',
  status: 1 // 1:开放招聘 2:暂停招聘
})

// 表单验证规则
const rules = {
  position_name: [
    { required: true, message: '请输入岗位名称', trigger: 'blur' }
  ],
  department: [
    { required: true, message: '请选择所属部门', trigger: 'change' }
  ],
  job_description: [
    { required: true, message: '请输入岗位职责', trigger: 'blur' },
    { min: 10, message: '岗位职责不能少于10个字符', trigger: 'blur' }
  ],
  requirements: [
    { required: true, message: '请输入任职要求', trigger: 'blur' },
    { min: 10, message: '任职要求不能少于10个字符', trigger: 'blur' }
  ]
}

// 模拟API：获取岗位详情（编辑模式用）
const getPositionDetail = (id) => {
  return new Promise(resolve => {
    setTimeout(() => {
      // 模拟接口返回数据
      resolve({
        id,
        position_name: '高级Java开发工程师',
        department: '技术部',
        location: '北京',
        recruitCount: 2,
        salary_range: '25k-40k',
        job_description: '负责核心业务系统的架构设计与开发',
        requirements: '3年以上Java开发经验，熟悉Spring Cloud微服务架构',
        status: 1
      })
    }, 300)
  })
}

// 模拟API：新建岗位
const createPosition = (data) => {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({ code: 200, message: '新建成功' })
    }, 500)
  })
}

// 模拟API：更新岗位
const updatePosition = (id, data) => {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({ code: 200, message: '更新成功' })
    }, 500)
  })
}

// 初始化编辑模式数据
const initEditData = async () => {
  if (isEdit.value) {
    const res = await getPositionDetail(route.params.id)
    // 拆分薪资范围
    const [min, max] = res.salary_range.replace('k', '').split('-')
    Object.assign(form, {
      position_name: res.position_name,
      department: res.department,
      location: res.location,
      recruitCount: res.recruitCount,
      minSalary: Number(min),
      maxSalary: Number(max),
      job_description: res.job_description,
      requirements: res.requirements,
      status: res.status
    })
  }
}

// 提交表单
const submitForm = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      // 组装提交数据
      const submitData = {
        ...form,
        salary_range: `${form.minSalary}k-${form.maxSalary}k`
      }

      if (isEdit.value) {
        await updatePosition(route.params.id, submitData)
        ElMessage.success('岗位更新成功')
      } else {
        await createPosition(submitData)
        ElMessage.success('岗位新建成功')
      }

      // 成功后返回列表页
      router.push('/position')
    } catch (error) {
      ElMessage.error('操作失败，请重试')
    } finally {
      loading.value = false
    }
  })
}

// 返回列表页
const goBack = () => {
  router.push('/position')
}

// 页面初始化
onMounted(() => {
  initEditData()
})
</script>

<style scoped>
.position-form-page {
  width: 100%;
}

.breadcrumb {
  margin-bottom: 16px;
}

.form-card {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px 40px;
}

.position-form {
  width: 100%;
}

/* 薪资范围样式 */
.salary-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.divider {
  color: #909399;
}

.unit {
  color: #606266;
}

/* 底部按钮 */
.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}
</style>