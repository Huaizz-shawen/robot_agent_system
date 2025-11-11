# example_usage.py

"""
DeepSeek API Humanoid Robot Planner 使用示例
"""


from humanoid_planner_deepseek import HumanoidRobotPlannerDeepSeek
from deepseek_config import list_available_presets

def example_sync_usage():
    """同步版本使用示例"""
    print("="*60)
    print("📌 同步版本示例")
    print("="*60)
    
    # 创建规划器实例
    planner = HumanoidRobotPlannerDeepSeek()
    
    # 测试连接
    if not planner.test_connection():
        print("无法连接到API")
        return
    
    # 示例任务请求
    test_requests = [
        "I feel cold, i might be sick."
    ]
    
    print("\n🔄 request processing...")
    for i, request in enumerate(test_requests, 1):
        print(f"\ntask {i}: {request}")
        print("-" * 40)
        
        # 生成计划
        plan = planner.plan_task(request)
        
        if "error" not in plan:
            # 显示任务分析
            analysis = plan['task_analysis']
            print(f"✅ task intent: {analysis['intent']}")
            print(f"   complexity: {analysis['complexity']}")
            print(f"   estimated duration: {analysis['estimated_duration']}")
            print(f"   involved steps: {len(plan['execution_plan'])} steps")
        else:
            print(f"❌ error: {plan['error']}")

def main():
    """主函数"""
    print("🤖 DeepSeek API Humanoid Robot Planner 使用示例")
    print("="*60)
    
    # 显示可用预设
    # list_available_presets()
    
    # 运行同步示例
    try:
        example_sync_usage()
    except Exception as e:
        print(f"同步版本错误: {str(e)}")
    
    print("✅ 所有示例运行完成")
    print("="*60)

if __name__ == "__main__":
    main()