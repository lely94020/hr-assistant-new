"""
面试评价API快速测试脚本
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

# 从命令行参数获取resume_id，默认为1
RESUME_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1


def test_generate_evaluation(summary_id=1):
    """测试生成评价"""
    print("=" * 50)
    print("测试1: 生成面试评价")
    print("=" * 50)
    
    url = f"{BASE_URL}/evaluations/generate"
    payload = {"summary_id": summary_id}
    
    try:
        response = requests.post(url, json=payload, timeout=180)
        data = response.json()
        
        if response.status_code == 200:
            print("✓ 生成成功！")
            print(f"评价ID: {data['id']}")
            print(f"简历ID: {data['resume_id']}")
            print(f"综合得分: {data['total_score']}")
            print(f"推荐等级: {data['recommendation']}")
            print(f"\n各维度评分:")
            for dim, info in data['scores'].items():
                print(f"  - {dim}: {info['score']}分")
            return data
        else:
            print(f"✗ 生成失败: {data.get('detail', '未知错误')}")
            return None
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return None


def test_get_evaluation(resume_id):
    """测试获取评价"""
    print("\n" + "=" * 50)
    print(f"测试2: 获取简历 {resume_id} 的评价")
    print("=" * 50)
    
    url = f"{BASE_URL}/evaluations/{resume_id}"
    
    try:
        response = requests.get(url, timeout=30)
        data = response.json()
        
        if response.status_code == 200:
            print("✓ 获取成功！")
            if 'candidate_info' in data:
                print(f"候选人: {data['candidate_info']['name']}")
                print(f"应聘岗位: {data['candidate_info']['position']}")
            print(f"综合得分: {data['total_score']}")
            print(f"推荐等级: {data['recommendation']}")
            if data.get('hr_comment'):
                print(f"HR评价: {data['hr_comment']}")
            return data
        else:
            print(f"✗ 获取失败: {data.get('detail', '未知错误')}")
            return None
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return None


def test_update_hr_comment(evaluation_id, hr_comment="测试评价：候选人表现优秀，建议录用。"):
    """测试更新HR评价"""
    print("\n" + "=" * 50)
    print(f"测试3: 更新HR补充评价 (评价ID: {evaluation_id})")
    print("=" * 50)
    
    url = f"{BASE_URL}/evaluations/{evaluation_id}/hr-comment"
    payload = {"hr_comment": hr_comment}
    
    try:
        response = requests.put(url, json=payload, timeout=30)
        data = response.json()
        
        if response.status_code == 200:
            print("✓ 更新成功！")
            print(f"HR评价: {data.get('hr_comment', '')}")
            return True
        else:
            print(f"✗ 更新失败: {data.get('detail', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return False


def test_get_history(resume_id):
    """测试获取评价历史"""
    print("\n" + "=" * 50)
    print(f"测试4: 获取简历 {resume_id} 的评价历史")
    print("=" * 50)
    
    url = f"{BASE_URL}/evaluations/history/{resume_id}"
    
    try:
        response = requests.get(url, timeout=30)
        data = response.json()
        
        if response.status_code == 200:
            print(f"✓ 获取成功！共 {len(data)} 条评价记录")
            for i, item in enumerate(data, 1):
                print(f"  {i}. 评价ID: {item['id']}, 得分: {item['total_score']}, 推荐: {item['recommendation']}")
            return True
        else:
            print(f"✗ 获取失败: {data.get('detail', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return False


if __name__ == "__main__":
    print(f"\n开始测试面试评价API (使用简历ID: {RESUME_ID})...\n")
    
    # 首先尝试获取已有评价
    evaluation_data = test_get_evaluation(RESUME_ID)
    
    if not evaluation_data:
        print("\n未找到评价，尝试生成新评价...")
        # 如果没有评价，尝试生成（需要summary_id）
        summary_id = input("请输入面试摘要ID (默认1): ").strip() or "1"
        evaluation_data = test_generate_evaluation(int(summary_id))
    
    if evaluation_data:
        evaluation_id = evaluation_data['id']
        
        # 测试更新HR评价
        test_update_hr_comment(evaluation_id)
        
        # 测试获取历史
        test_get_history(RESUME_ID)
    
    print("\n测试完成！")