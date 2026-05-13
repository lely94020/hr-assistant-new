from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.resume import Resume
from datetime import datetime
import json

def create_sample_resumes():
    """创建简历示例数据"""

    # 创建表（如果不存在）
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 示例数据列表
        sample_resumes = [
            {
                "candidate_name": "张三",
                "phone": "13812345678",
                "email": "zhangsan@example.com",
                "education": "本科",
                "school": "北京大学",
                "major": "计算机科学",
                "work_years": 5,
                "current_company": "阿里巴巴",
                "current_position": "高级Java工程师",
                "skills": json.dumps(["Java", "Spring Boot", "MySQL", "Redis", "微服务"]),
                "work_experience": json.dumps([
                    {
                        "company": "阿里巴巴",
                        "position": "高级Java工程师",
                        "duration": "2020-至今",
                        "description": "负责电商平台后端开发"
                    },
                    {
                        "company": "腾讯",
                        "position": "Java工程师",
                        "duration": "2018-2020",
                        "description": "负责社交产品后端开发"
                    }
                ]),
                "project_experience": json.dumps([
                    {
                        "name": "电商中台系统",
                        "role": "核心开发",
                        "description": "设计并实现订单管理系统，支持日均百万订单"
                    }
                ]),
                "education_experience": json.dumps([
                    {
                        "school": "北京大学",
                        "degree": "本科",
                        "major": "计算机科学",
                        "duration": "2014-2018"
                    }
                ]),
                "resume_summary": "5年Java开发经验，熟悉微服务架构，有大型电商平台开发经验，技术栈全面",
                "original_content": "张三的简历内容...",
                "file_path": "uploads/resumes/zhangsan_resume.pdf",
                "file_name": "张三_简历.pdf",
                "file_type": "pdf",
                "file_size": 524288,
                "position_id": 1,
                "status": 1,
                "parse_status": 2,
                "is_deleted": 0
            },
            {
                "candidate_name": "李四",
                "phone": "13987654321",
                "email": "lisi@example.com",
                "education": "硕士",
                "school": "清华大学",
                "major": "软件工程",
                "work_years": 3,
                "current_company": "字节跳动",
                "current_position": "Python工程师",
                "skills": json.dumps(["Python", "Django", "PostgreSQL", "Docker", "AI"]),
                "work_experience": json.dumps([
                    {
                        "company": "字节跳动",
                        "position": "Python工程师",
                        "duration": "2021-至今",
                        "description": "负责推荐系统后端开发"
                    }
                ]),
                "project_experience": json.dumps([
                    {
                        "name": "智能推荐引擎",
                        "role": "主要负责人",
                        "description": "开发基于机器学习的推荐算法，提升用户点击率30%"
                    }
                ]),
                "education_experience": json.dumps([
                    {
                        "school": "清华大学",
                        "degree": "硕士",
                        "major": "软件工程",
                        "duration": "2018-2021"
                    },
                    {
                        "school": "浙江大学",
                        "degree": "本科",
                        "major": "计算机科学与技术",
                        "duration": "2014-2018"
                    }
                ]),
                "resume_summary": "3年Python开发经验，专注于AI和推荐系统，有扎实的算法基础",
                "original_content": "李四的简历内容...",
                "file_path": "uploads/resumes/lisi_resume.pdf",
                "file_name": "李四_简历.pdf",
                "file_type": "pdf",
                "file_size": 458752,
                "position_id": None,
                "status": 1,
                "parse_status": 2,
                "is_deleted": 0
            },
            {
                "candidate_name": "王五",
                "phone": "13611112222",
                "email": "wangwu@example.com",
                "education": "本科",
                "school": "复旦大学",
                "major": "电子信息工程",
                "work_years": 7,
                "current_company": "华为",
                "current_position": "技术架构师",
                "skills": json.dumps(["Go", "Kubernetes", "微服务", "分布式系统", "云原生"]),
                "work_experience": json.dumps([
                    {
                        "company": "华为",
                        "position": "技术架构师",
                        "duration": "2019-至今",
                        "description": "负责云平台架构设计"
                    },
                    {
                        "company": "中兴",
                        "position": "高级开发工程师",
                        "duration": "2016-2019",
                        "description": "负责通信系统开发"
                    }
                ]),
                "project_experience": json.dumps([
                    {
                        "name": "企业级云平台",
                        "role": "架构师",
                        "description": "设计并实现支持万级节点的云管理平台"
                    }
                ]),
                "education_experience": json.dumps([
                    {
                        "school": "复旦大学",
                        "degree": "本科",
                        "major": "电子信息工程",
                        "duration": "2012-2016"
                    }
                ]),
                "resume_summary": "7年开发经验，3年架构设计经验，精通云原生技术和分布式系统",
                "original_content": "王五的简历内容...",
                "file_path": "uploads/resumes/wangwu_resume.docx",
                "file_name": "王五_简历.docx",
                "file_type": "docx",
                "file_size": 327680,
                "position_id": 1,
                "status": 2,
                "parse_status": 2,
                "is_deleted": 0
            },
            {
                "candidate_name": "赵六",
                "phone": "13733334444",
                "email": "zhaoliu@example.com",
                "education": "硕士",
                "school": "上海交通大学",
                "major": "人工智能",
                "work_years": 2,
                "current_company": "商汤科技",
                "current_position": "算法工程师",
                "skills": json.dumps(["Python", "TensorFlow", "PyTorch", "计算机视觉", "深度学习"]),
                "work_experience": json.dumps([
                    {
                        "company": "商汤科技",
                        "position": "算法工程师",
                        "duration": "2022-至今",
                        "description": "负责计算机视觉算法研发"
                    }
                ]),
                "project_experience": json.dumps([
                    {
                        "name": "智能安防系统",
                        "role": "算法负责人",
                        "description": "开发人脸识别和行为分析算法，准确率达99%"
                    }
                ]),
                "education_experience": json.dumps([
                    {
                        "school": "上海交通大学",
                        "degree": "硕士",
                        "major": "人工智能",
                        "duration": "2019-2022"
                    }
                ]),
                "resume_summary": "2年AI算法经验，专注于计算机视觉领域，发表多篇顶会论文",
                "original_content": "赵六的简历内容...",
                "file_path": "uploads/resumes/zhaoliu_resume.pdf",
                "file_name": "赵六_简历.pdf",
                "file_type": "pdf",
                "file_size": 612352,
                "position_id": None,
                "status": 1,
                "parse_status": 2,
                "is_deleted": 0
            },
            {
                "candidate_name": "陈七",
                "phone": "13555556666",
                "email": "chenqi@example.com",
                "education": "本科",
                "school": "南京大学",
                "major": "信息管理",
                "work_years": 4,
                "current_company": "美团",
                "current_position": "前端工程师",
                "skills": json.dumps(["JavaScript", "React", "Vue.js", "TypeScript", "Node.js"]),
                "work_experience": json.dumps([
                    {
                        "company": "美团",
                        "position": "前端工程师",
                        "duration": "2020-至今",
                        "description": "负责外卖业务前端开发"
                    },
                    {
                        "company": "饿了么",
                        "position": "Web开发工程师",
                        "duration": "2019-2020",
                        "description": "负责商家端页面开发"
                    }
                ]),
                "project_experience": json.dumps([
                    {
                        "name": "外卖小程序",
                        "role": "前端负责人",
                        "description": "主导小程序重构，性能提升50%"
                    }
                ]),
                "education_experience": json.dumps([
                    {
                        "school": "南京大学",
                        "degree": "本科",
                        "major": "信息管理",
                        "duration": "2015-2019"
                    }
                ]),
                "resume_summary": "4年前端开发经验，精通React和Vue生态，有丰富的移动端开发经验",
                "original_content": "陈七的简历内容...",
                "file_path": "uploads/resumes/chenqi_resume.pdf",
                "file_name": "陈七_简历.pdf",
                "file_type": "pdf",
                "file_size": 445440,
                "position_id": None,
                "status": 3,
                "parse_status": 2,
                "is_deleted": 0
            },
            {
                "candidate_name": "刘八",
                "phone": "13877778888",
                "email": "liuba@example.com",
                "education": "博士",
                "school": "中国科学院",
                "major": "计算机网络",
                "work_years": 10,
                "current_company": "百度",
                "current_position": "资深技术专家",
                "skills": json.dumps(["C++", "Python", "分布式系统", "搜索引擎", "大数据"]),
                "work_experience": json.dumps([
                    {
                        "company": "百度",
                        "position": "资深技术专家",
                        "duration": "2018-至今",
                        "description": "负责搜索引擎核心算法优化"
                    },
                    {
                        "company": "谷歌",
                        "position": "高级工程师",
                        "duration": "2014-2018",
                        "description": "参与搜索基础设施建设"
                    }
                ]),
                "project_experience": json.dumps([
                    {
                        "name": "新一代搜索引擎",
                        "role": "技术负责人",
                        "description": "设计并实现下一代搜索架构，支持十亿级索引"
                    }
                ]),
                "education_experience": json.dumps([
                    {
                        "school": "中国科学院",
                        "degree": "博士",
                        "major": "计算机网络",
                        "duration": "2011-2014"
                    }
                ]),
                "resume_summary": "10年技术研发经验，深耕搜索引擎领域，具备国际视野和技术领导力",
                "original_content": "刘八的简历内容...",
                "file_path": "uploads/resumes/liuba_resume.docx",
                "file_name": "刘八_简历.docx",
                "file_type": "docx",
                "file_size": 532480,
                "position_id": 1,
                "status": 4,
                "parse_status": 2,
                "is_deleted": 0
            },
            {
                "candidate_name": "周九",
                "phone": "13699990000",
                "email": "zhoujiu@example.com",
                "education": "本科",
                "school": "武汉大学",
                "major": "网络安全",
                "work_years": 6,
                "current_company": "奇安信",
                "current_position": "安全工程师",
                "skills": json.dumps(["渗透测试", "漏洞挖掘", "Python", "Linux", "安全加固"]),
                "work_experience": json.dumps([
                    {
                        "company": "奇安信",
                        "position": "安全工程师",
                        "duration": "2019-至今",
                        "description": "负责企业安全评估和渗透测试"
                    }
                ]),
                "project_experience": json.dumps([
                    {
                        "name": "企业安全防护体系",
                        "role": "项目负责人",
                        "description": "构建完整的企业安全防护体系，发现并修复多个高危漏洞"
                    }
                ]),
                "education_experience": json.dumps([
                    {
                        "school": "武汉大学",
                        "degree": "本科",
                        "major": "网络安全",
                        "duration": "2014-2018"
                    }
                ]),
                "resume_summary": "6年网络安全经验，持有CISSP认证，擅长渗透测试和安全架构设计",
                "original_content": "周九的简历内容...",
                "file_path": "uploads/resumes/zhoujiu_resume.pdf",
                "file_name": "周九_简历.pdf",
                "file_type": "pdf",
                "file_size": 389120,
                "position_id": None,
                "status": 1,
                "parse_status": 2,
                "is_deleted": 0
            },
            {
                "candidate_name": "吴十",
                "phone": "13512121212",
                "email": "wushi@example.com",
                "education": "硕士",
                "school": "中山大学",
                "major": "数据科学",
                "work_years": 3,
                "current_company": "滴滴出行",
                "current_position": "数据分析师",
                "skills": json.dumps(["SQL", "Python", "Tableau", "统计学", "机器学习"]),
                "work_experience": json.dumps([
                    {
                        "company": "滴滴出行",
                        "position": "数据分析师",
                        "duration": "2021-至今",
                        "description": "负责业务数据分析和决策支持"
                    }
                ]),
                "project_experience": json.dumps([
                    {
                        "name": "智能定价系统",
                        "role": "数据分析师",
                        "description": "通过数据分析优化定价策略，提升营收15%"
                    }
                ]),
                "education_experience": json.dumps([
                    {
                        "school": "中山大学",
                        "degree": "硕士",
                        "major": "数据科学",
                        "duration": "2018-2021"
                    }
                ]),
                "resume_summary": "3年数据分析经验，擅长数据挖掘和商业洞察，有较强的业务理解能力",
                "original_content": "吴十的简历内容...",
                "file_path": "uploads/resumes/wushi_resume.pdf",
                "file_name": "吴十_简历.pdf",
                "file_type": "pdf",
                "file_size": 421888,
                "position_id": None,
                "status": 5,
                "parse_status": 2,
                "is_deleted": 0
            }
        ]

        # 插入数据
        for resume_data in sample_resumes:
            resume = Resume(**resume_data)
            db.add(resume)

        db.commit()

        print(f"✅ 成功创建 {len(sample_resumes)} 条简历示例数据")

        # 查询验证
        count = db.query(Resume).count()
        print(f"📊 数据库中简历总数: {count}")

    except Exception as e:
        db.rollback()
        print(f"❌ 创建示例数据失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_resumes()
