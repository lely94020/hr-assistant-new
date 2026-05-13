<template>
  <div class="position-list">
    <!-- 页面标题 -->
    <h2>岗位管理</h2>

    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="岗位名称">
          <el-input
            v-model="searchForm.position_name"
            placeholder="请输入岗位名称"
            clearable
          />
        </el-form-item>
        <el-form-item label="部门">
          <el-select
            v-model="searchForm.department"
            placeholder="全部部门"
            clearable
          >
            <el-option label="技术部" value="技术部" />
            <el-option label="产品部" value="产品部" />
            <el-option label="设计部" value="设计部" />
            <el-option label="市场部" value="市场部" />
            <el-option label="人事部" value="人事部" />
            <el-option label="财务部" value="财务部" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="全部状态"
            clearable
          >
            <el-option label="开放招聘" :value="1" />
            <el-option label="暂停招聘" :value="2" />
            <el-option label="已关闭" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon> 重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作按钮 -->
    <div class="action-bar">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon> 新建岗位
      </el-button>
    </div>

    <!-- 数据表格 -->
    <el-table :data="tableData" stripe border v-loading="loading">
      <el-table-column prop="position_name" label="岗位名称" width="200" />
      <el-table-column prop="department" label="所属部门" width="120" />
      <el-table-column
        prop="headcount"
        label="招聘人数"
        width="100"
        align="center"
      />
      <el-table-column prop="salary_range" label="薪资范围" width="150" />
      <el-table-column prop="work_location" label="工作地点" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusName(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="280">
        <template #default="{ row }">
          <el-button type="success" link @click="handleView(row)">
            <el-icon><View /></el-icon> 查看
          </el-button>
          <el-button type="primary" link @click="handleEdit(row)">
            <el-icon><Edit /></el-icon> 编辑
          </el-button>
          <el-button type="danger" link @click="handleDelete(row)">
            <el-icon><Delete /></el-icon> 删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </div>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="岗位名称" prop="position_name">
          <el-input v-model="formData.position_name" placeholder="请输入岗位名称" />
        </el-form-item>

        <el-form-item label="所属部门" prop="department">
          <el-select v-model="formData.department" placeholder="请选择部门" style="width: 100%">
            <el-option label="技术部" value="技术部" />
            <el-option label="产品部" value="产品部" />
            <el-option label="设计部" value="设计部" />
            <el-option label="市场部" value="市场部" />
            <el-option label="人事部" value="人事部" />
            <el-option label="财务部" value="财务部" />
          </el-select>
        </el-form-item>

        <el-form-item label="岗位职责" prop="job_description">
          <el-input
            v-model="formData.job_description"
            type="textarea"
            :rows="4"
            placeholder="请输入岗位职责描述"
          />
        </el-form-item>

        <el-form-item label="任职要求" prop="requirements">
          <el-input
            v-model="formData.requirements"
            type="textarea"
            :rows="4"
            placeholder="请输入任职要求"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="薪资范围" prop="salary_range">
              <el-input v-model="formData.salary_range" placeholder="例如：15-25K" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工作地点" prop="work_location">
              <el-input v-model="formData.work_location" placeholder="例如：北京" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="招聘人数" prop="headcount">
              <el-input-number
                v-model="formData.headcount"
                :min="1"
                :max="100"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="开放招聘" :value="1" />
                <el-option label="暂停招聘" :value="2" />
                <el-option label="已关闭" :value="3" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="岗位详情"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-descriptions :column="2" border v-loading="detailLoading">
        <el-descriptions-item label="岗位ID">
          {{ detailData.id }}
        </el-descriptions-item>
        <el-descriptions-item label="岗位名称">
          {{ detailData.position_name }}
        </el-descriptions-item>
        <el-descriptions-item label="所属部门">
          {{ detailData.department }}
        </el-descriptions-item>
        <el-descriptions-item label="招聘人数">
          {{ detailData.headcount }} 人
        </el-descriptions-item>
        <el-descriptions-item label="薪资范围">
          {{ detailData.salary_range || '面议' }}
        </el-descriptions-item>
        <el-descriptions-item label="工作地点">
          {{ detailData.work_location || '未指定' }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(detailData.status)">
            {{ getStatusName(detailData.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDate(detailData.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ formatDate(detailData.updated_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="岗位职责" :span="2">
          <div class="description-content">{{ detailData.job_description }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="任职要求" :span="2">
          <div class="description-content">{{ detailData.requirements }}</div>
        </el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleEditFromDetail">
          编辑
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, Refresh, Plus, Edit, Delete, View } from '@element-plus/icons-vue';
import { getPositionList, deletePosition, createPosition, updatePosition, getPositionDetail } from "@/api/position";

// 搜索表单
const searchForm = reactive({
  position_name: "",
  department: "",
  status: null,
});

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

// 表格数据
const tableData = ref([]);
const loading = ref(false);

// 对话框
const dialogVisible = ref(false);
const dialogTitle = ref("新建岗位");
const submitLoading = ref(false);
const formRef = ref(null);

// 表单数据
const formData = reactive({
  id: null,
  position_name: "",
  department: "",
  job_description: "",
  requirements: "",
  salary_range: "",
  work_location: "",
  headcount: 1,
  status: 1,
});

// 详情对话框
const detailDialogVisible = ref(false);
const detailLoading = ref(false);
const detailData = reactive({
  id: null,
  position_name: "",
  department: "",
  job_description: "",
  requirements: "",
  salary_range: "",
  work_location: "",
  headcount: 1,
  status: 1,
  created_at: "",
  updated_at: "",
});

// 表单验证规则
const formRules = {
  position_name: [
    { required: true, message: "请输入岗位名称", trigger: "blur" },
    { min: 2, max: 100, message: "长度在 2 到 100 个字符", trigger: "blur" }
  ],
  department: [
    { required: true, message: "请选择部门", trigger: "change" }
  ],
  job_description: [
    { required: true, message: "请输入岗位职责", trigger: "blur" }
  ],
  requirements: [
    { required: true, message: "请输入任职要求", trigger: "blur" }
  ],
};

// 获取数据
const fetchData = async () => {
  loading.value = true;
  try {
    const res = await getPositionList({
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm,
    });
    tableData.value = res.items;
    pagination.total = res.total;
  } catch (error) {
    console.error(error);
    ElMessage.error("获取数据失败");
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleSearch = () => {
  pagination.page = 1;
  fetchData();
};

// 重置
const handleReset = () => {
  searchForm.position_name = "";
  searchForm.department = "";
  searchForm.status = null;
  handleSearch();
};

// 新建
const handleCreate = () => {
  dialogTitle.value = "新建岗位";
  resetForm();
  dialogVisible.value = true;
};

// 查看详情
const handleView = async (row) => {
  detailDialogVisible.value = true;
  detailLoading.value = true;

  try {
    const data = await getPositionDetail(row.id);
    Object.assign(detailData, data);
  } catch (error) {
    console.error(error);
    ElMessage.error("获取详情失败");
    detailDialogVisible.value = false;
  } finally {
    detailLoading.value = false;
  }
};

// 从详情页编辑
const handleEditFromDetail = () => {
  detailDialogVisible.value = false;
  handleEdit(detailData);
};

// 编辑
const handleEdit = (row) => {
  dialogTitle.value = "编辑岗位";
  // 复制数据到表单
  Object.assign(formData, {
    id: row.id,
    position_name: row.position_name,
    department: row.department,
    job_description: row.job_description,
    requirements: row.requirements,
    salary_range: row.salary_range || "",
    work_location: row.work_location || "",
    headcount: row.headcount || 1,
    status: row.status,
  });
  dialogVisible.value = true;
};

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除岗位"${row.position_name}"吗？`,
      "提示",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );
    await deletePosition(row.id);
    ElMessage.success("删除成功");
    fetchData();
  } catch (error) {
    if (error !== "cancel") {
      console.error(error);
      ElMessage.error("删除失败");
    }
  }
};

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true;
      try {
        if (formData.id) {
          // 编辑
          await updatePosition(formData.id, {
            position_name: formData.position_name,
            department: formData.department,
            job_description: formData.job_description,
            requirements: formData.requirements,
            salary_range: formData.salary_range,
            work_location: formData.work_location,
            headcount: formData.headcount,
            status: formData.status,
          });
          ElMessage.success("更新成功");
        } else {
          // 新建
          await createPosition({
            position_name: formData.position_name,
            department: formData.department,
            job_description: formData.job_description,
            requirements: formData.requirements,
            salary_range: formData.salary_range,
            work_location: formData.work_location,
            headcount: formData.headcount,
            status: formData.status,
          });
          ElMessage.success("创建成功");
        }
        dialogVisible.value = false;
        fetchData();
      } catch (error) {
        console.error(error);
        ElMessage.error(formData.id ? "更新失败" : "创建失败");
      } finally {
        submitLoading.value = false;
      }
    }
  });
};

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    id: null,
    position_name: "",
    department: "",
    job_description: "",
    requirements: "",
    salary_range: "",
    work_location: "",
    headcount: 1,
    status: 1,
  });
  if (formRef.value) {
    formRef.value.clearValidate();
  }
};

// 状态标签类型
const getStatusType = (status) => {
  const map = { 1: "success", 2: "warning", 3: "info" };
  return map[status] || "info";
};

// 状态名称
const getStatusName = (status) => {
  const map = { 1: "开放招聘", 2: "暂停招聘", 3: "已关闭" };
  return map[status] || "未知";
};

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

// 初始化
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.position-list {
  padding: 20px;
}

.position-list h2 {
  margin-bottom: 20px;
  color: #303133;
  font-size: 24px;
}

.search-card {
  margin-bottom: 16px;
}

.action-bar {
  margin-bottom: 16px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.description-content {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}
</style>
