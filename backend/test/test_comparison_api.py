"""
测试候选人对比API
"""
import requests
import json

# 先获取岗位列表
print("=" * 60)
print("步骤1: 获取岗位列表")
print("=" * 60)
positions_url = "http://localhost:8000/api/v1/positions?page=1&page_size=10"
positions_response = requests.get(positions_url)
if positions_response.status_code == 200:
    positions_data = positions_response.json()
    print(f"岗位总数: {positions_data.get('total', 0)}")
    if positions_data.get('items'):
        print("可用岗位:")
        for pos in positions_data['items'][:3]:
            print(f"  - ID: {pos['id']}, 名称: {pos['position_name']}")
        test_position_id = positions_data['items'][0]['id']
    else:
        print("❌ 没有可用岗位")
        exit(1)
else:
    print(f"❌ 获取岗位列表失败: {positions_response.text}")
    exit(1)

# 获取所有简历（不限岗位）
print("\n" + "=" * 60)
print("步骤2: 获取简历列表")
print("=" * 60)
resumes_url = "http://localhost:8000/api/v1/resumes?page=1&page_size=10"
resumes_response = requests.get(resumes_url)
if resumes_response.status_code == 200:
    resumes_data = resumes_response.json()
    print(f"简历总数: {resumes_data.get('total', 0)}")
    if resumes_data.get('items'):
        print("可用简历:")
        for resume in resumes_data['items'][:5]:
            position_info = f", 岗位ID: {resume.get('position_id', '未关联')}" if resume.get('position_id') else ""
            print(f"  - ID: {resume['id']}, 姓名: {resume['candidate_name']}{position_info}")
        
        # 取前2个简历ID
        test_resume_ids = [resume['id'] for resume in resumes_data['items'][:2]]
        print(f"\n使用简历IDs: {test_resume_ids}")
        print(f"使用岗位ID: {test_position_id}")
    else:
        print("❌ 系统中没有简历，请先上传简历")
        print("\n提示：可以通过以下方式上传简历：")
        print("  1. 访问前端页面上传简历")
        print("  2. 运行测试脚本: python test/create_sample_resumes.py")
        exit(1)
else:
    print(f"❌ 获取简历列表失败: {resumes_response.text}")
    exit(1)

# 发送对比请求
print("\n" + "=" * 60)
print("步骤3: 创建候选人对比")
print("=" * 60)
test_data = {
    "position_id": test_position_id,
    "resume_ids": test_resume_ids
}

url = "http://localhost:8000/api/v1/comparison/create"
headers = {"Content-Type": "application/json"}

print(f"请求URL: {url}")
print(f"请求数据: {json.dumps(test_data, ensure_ascii=False)}")

try:
    response = requests.post(url, json=test_data, headers=headers)
    print(f"\n状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ 请求成功")
        data = response.json()
        print("\n响应数据:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 测试 AI 分析
        comparison_id = data.get('id')
        if comparison_id:
            print("\n" + "=" * 60)
            print("步骤4: 测试 AI 对比分析")
            print("=" * 60)
            
            analyze_url = f"http://localhost:8000/api/v1/comparison/{comparison_id}/analyze"
            print(f"请求URL: {analyze_url}")
            
            try:
                analyze_response = requests.post(analyze_url, headers=headers, timeout=60)
                print(f"状态码: {analyze_response.status_code}")
                
                if analyze_response.status_code == 200:
                    print("✅ AI 分析成功")
                    analyze_data = analyze_response.json()
                    print("\nAI 分析结果:")
                    print(json.dumps(analyze_data, indent=2, ensure_ascii=False))
                else:
                    print(f"❌ AI 分析失败: {analyze_response.text}")
                    
            except Exception as e:
                print(f"AI 分析请求异常: {str(e)}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(f"响应内容: {response.text}")
        
except Exception as e:
    print(f"请求异常: {str(e)}")