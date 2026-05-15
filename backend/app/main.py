from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.database import engine, Base
from app.models.position import JobPosition
from app.models.user import SysUser, UserToken
from app.models.resume import Resume
from app.models.recording import InterviewRecording
from app.models.interview_summary import InterviewSummary
from app.api.v1.position import router as position_router
from app.api.v1.login import router as login_router
from app.api.v1.resume import router as resume_router
from app.api.v1.screening import router as screening_router
from app.api.v1.question import router as question_router
from app.api.v1.recording import router as recording_router
from app.api.v1.interview_summary import router as summary_router
import os

app = FastAPI(
    title="HR智能助手API",
    description="企业HR智能助手后端接口",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册静态文件服务
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(position_router)
app.include_router(login_router)
app.include_router(resume_router)
app.include_router(screening_router)
app.include_router(question_router)
app.include_router(recording_router)
app.include_router(summary_router)

@app.on_event("startup")
# 自动创建数据库表
def startup():
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")

@app.get("/")
def root():
    return {"message": "HR智能助手API运行中", "docs": "/docs"}