# test_debug.py

"""
DeepSeek API 调试测试脚本
用于诊断JSON解析问题
"""
import os
import sys
import json
import requests
# 添加父目录到路径（如果需要从子目录导入）
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from json_tool.json_parser_enhanced import (
    clean_json_response_enhanced,
    parse_json_with_fallback,
    validate_robot_response
)
from humanoid_prompt_template import get_humanoid_system_prompt

def test_direct_api_call():
    """直接测试API调用，查看原始响应"""
    print("="*60)
    print("📝 直接API调用测试")
    print("="*60)
    
    url = "http://dsv3.sii.edu.cn/v1/chat/completions"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # 获取系统提示词
    system_prompt = get_humanoid_system_prompt()
    
    # 测试请求
    test_request = "请帮我从冰箱拿一瓶水"
    
    request_data = {
        "model": "deepseek-v3-ep",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": test_request}
        ],
        "max_tokens": 2000,
        "temperature": 0.5,
        "top_p": 0.95,
        "presence_penalty": 1.03,
        "frequency_penalty": 1.0,
        "stream": False
    }
    
    print(f"请求: {test_request}")
    print("-"*40)
    
    try:
        # 发送请求
        print("发送请求到API...")
        response = requests.post(url, headers=headers, json=request_data, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            response_json = response.json()
            
            # 提取内容
            if 'choices' in response_json and len(response_json['choices']) > 0:
                content = response_json['choices'][0]['message']['content']
                
                print("\n📄 原始响应内容:")
                print("-"*40)
                print(content[:1000])  # 只显示前1000个字符
                if len(content) > 1000:
                    print(f"... (总共 {len(content)} 个字符)")
                print("-"*40)
                
                # 保存原始响应
                with open('raw_response.txt', 'w', encoding='utf-8') as f:
                    f.write(content)
                print("✅ 原始响应已保存到 raw_response.txt")
                
                # 测试JSON解析
                print("\n🔧 测试JSON解析:")
                print("-"*40)
                
                # 使用增强解析
                result, success = parse_json_with_fallback(content, debug=True)
                
                if success:
                    print("\n✅ 解析成功!")
                    print(f"任务意图: {result.get('task_analysis', {}).get('intent', 'N/A')}")
                    print(f"复杂度: {result.get('task_analysis', {}).get('complexity', 'N/A')}")
                    print(f"步骤数: {len(result.get('execution_plan', []))}")
                    
                    # 保存解析后的JSON
                    with open('parsed_response.json', 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    print("✅ 解析结果已保存到 parsed_response.json")
                else:
                    print("\n❌ 解析失败")
                    print(f"错误: {result.get('error', 'Unknown error')}")
                
                # 验证响应结构
                if success:
                    is_valid, validation_msg = validate_robot_response(result)
                    print(f"\n📋 响应验证: {'✅ 通过' if is_valid else '❌ 失败'}")
                    print(f"   {validation_msg}")
                
            else:
                print("❌ 响应格式无效：没有找到choices字段")
                print(f"响应内容: {response_json}")
        else:
            print(f"❌ API请求失败")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

def test_json_cleaning():
    """测试JSON清理功能"""
    print("\n" + "="*60)
    print("🧹 JSON清理功能测试")
    print("="*60)
    
    # 测试各种格式问题的JSON
    test_cases = [
        # 缺少引号的属性名
        '{task_analysis: {"intent": "fetch"}}',
        
        # 末尾多余的逗号
        '{"task": "test", "status": "ok",}',
        
        # Python风格的布尔值
        '{"success": True, "error": False}',
        
        # 单引号
        "{'task': 'test', 'status': 'ok'}",
        
        # 包含注释
        '{"task": "test" // this is a comment\n}',
        
        # 缺少逗号
        '{"task": "test"\n"status": "ok"}',
    ]
    
    for i, test_json in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}:")
        print(f"原始: {test_json}")
        
        cleaned = clean_json_response_enhanced(test_json)
        print(f"清理后: {cleaned}")
        
        try:
            parsed = json.loads(cleaned)
            print(f"✅ 解析成功: {parsed}")
        except json.JSONDecodeError as e:
            print(f"❌ 解析失败: {e}")

def main():
    """主函数"""
    print("🔍 DeepSeek API 调试测试")
    print("="*60)
    
    # 1. 测试直接API调用
    test_direct_api_call()
    
    # 2. 测试JSON清理功能
    test_json_cleaning()
    
    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)

if __name__ == "__main__":
    main()