import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    component: () => import('@/views/login/login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/dashboard',
    component: () => import('@/views/dashboard/dashboard.vue'),
    meta: { title: '工作台', requiresAuth: true }
  },
  {
    path: '/position',
    component: () => import('@/views/position/PositionList.vue'),
    meta: { title: '岗位管理', requiresAuth: true }
  },
  {
    path: '/resume',
    component: () => import('@/views/resume/Resume.vue'),
    meta: { title: '简历管理', requiresAuth: true }
  },
  {
    path: '/resume/upload',
    component: () => import('@/views/resume/ResumeUpload.vue'),
    meta: { title: '上传简历', requiresAuth: true }
  },
  {
    path: '/resume/detail/:id',
    component: () => import('@/views/resume/ResumeDetail.vue'),
    meta: { title: '简历详情', requiresAuth: true },
    props: true
  },
  {
    path: '/screening',
    component: () => import('@/views/screening/Screening.vue'),
    meta: { title: '简历筛选', requiresAuth: true }
  },
  {
    path: '/comparison',
    component: () => import('@/views/comparison/Comparison.vue'),
    meta: { title: '候选人对比', requiresAuth: true }
  },
  {
    path: '/question',
    component: () => import('@/views/question/Question.vue'),
    meta: { title: '面试题库', requiresAuth: true }
  },
  {
    path: '/recording',
    component: () => import('@/views/recording/Recording.vue'),
    meta: { title: '面试录音', requiresAuth: true }
  },
  {
    path: '/evaluation',
    component: () => import('@/views/evaluation/Evaluation.vue'),
    meta: { title: '面试评价', requiresAuth: true }
  },
  {
    path: '/',
    redirect: '/login'
  }
]

// ... existing code ...


const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫 - 验证登录状态
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 企业HR智能助手` : '企业HR智能助手'

  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')

  // 需要登录的页面
  if (to.meta.requiresAuth) {
    if (!token) {
      // 未登录，跳转到登录页，并记录要访问的页面
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    // 不需要登录的页面（如登录页）
    if (to.path === '/login' && token) {
      // 已登录用户访问登录页，跳转到首页
      next('/dashboard')
    } else {
      next()
    }
  }
})

export default router
