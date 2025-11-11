# example_usage.py

import os
import sys
from qwenapi_planner import QwenMultiAgentPlanner

def check_environment():
    """检查环境配置"""
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("❌ Error: DASHSCOPE_API_KEY environment variable not set.")
        print("Please set it using:")
        print("  export DASHSCOPE_API_KEY='your-api-key'")
        print("Or create a .env file with:")
        print("  DASHSCOPE_API_KEY=your-api-key")
        return False
    return True

def quick_example():
    """快速使用示例"""
    if not check_environment():
        return
    
    try:
        print("🚀 Quick Example - Testing Air Conditioner Control")
        print("-" * 50)
        
        planner = QwenMultiAgentPlanner(model_name="qwen2.5-14b-instruct")
        
        # 测试简单请求（带调试）
        result = planner.plan_task("I'm feeling a bit cold, I might be getting sick", debug=True)
        planner.execute_plan(result)
        
    except Exception as e:
        print(f"❌ Quick example failed: {str(e)}")
        import traceback
        traceback.print_exc()

def debug_json_parsing():
    """专门测试JSON解析功能"""
    if not check_environment():
        return
        
    try:
        print("🔍 Debug JSON Parsing")
        print("-" * 50)
        
        planner = QwenMultiAgentPlanner()
        
        # 获取原始响应
        raw_response = planner.plan_task("turn on the light", return_raw=True)
        print(f"Raw response:\n{raw_response}\n")
        print("="*50)
        
        # 测试清理函数
        from system_prompt_template import clean_json_response
        cleaned = clean_json_response(raw_response)
        print(f"Cleaned response:\n{cleaned}\n")
        print("="*50)
        
        # 尝试解析
        import json
        try:
            parsed = json.loads(cleaned)
            print("✅ JSON parsing successful!")
            print(f"Parsed keys: {list(parsed.keys())}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            
    except Exception as e:
        print(f"❌ Debug test failed: {str(e)}")

def test_multiple_requests():
    """测试多个请求"""
    if not check_environment():
        return
        
    requests = [
        "turn on the air conditioner",
        "i want to buy some water from the store",
        "turn off the light",
        "prepare a reading environment"
    ]
    
    try:
        print("📋 Testing Multiple Requests")
        print("-" * 50)
        
        planner = QwenMultiAgentPlanner()
        
        for i, request in enumerate(requests, 1):
            print(f"\n[{i}/{len(requests)}] Testing: {request}")
            result = planner.plan_task(request)
            
            if "error" not in result:
                print(f"✅ Success - Intent: {result['task_analysis']['intent']}")
            else:
                print(f"❌ Failed: {result['error']}")
        
    except Exception as e:
        print(f"❌ Multiple requests test failed: {str(e)}")

if __name__ == "__main__":
    # 根据命令行参数选择运行模式
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "quick":
            quick_example()
        elif mode == "debug":
            debug_json_parsing()
        elif mode == "multi":
            test_multiple_requests()
        else:
            print("Available modes: quick, debug, multi")
    else:
        # 默认运行快速示例
        quick_example()