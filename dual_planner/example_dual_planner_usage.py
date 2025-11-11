# example_dual_planner_usage.py

"""
Example usage of the dual planner system:
- Planner 1: HumanoidRobotPlanner (Unitree-G1) for home environment control
- Planner 2: RoboticArmPlanner (UR5e) for store inventory management

This demonstrates how to use both planners independently and in coordination.
"""

import os
import sys
from humanoid_planner import HumanoidRobotPlanner
from arm_planner import RoboticArmPlanner

def check_environment():
    """检查环境变量是否配置"""
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("❌ Error: DASHSCOPE_API_KEY environment variable not set.")
        print("\nPlease set it using one of these methods:")
        print("  1. export DASHSCOPE_API_KEY='your-api-key'")
        print("  2. source apikey.bash")
        print("  3. Set it in your shell profile (~/.bashrc or ~/.zshrc)")
        return False
    return True

def demo_humanoid_only():
    """演示人形机器人独立工作 - 仅处理家庭环境控制"""
    print("\n" + "="*70)
    print("DEMO 1: Humanoid Robot Only - Home Environment Control")
    print("="*70)

    try:
        humanoid = HumanoidRobotPlanner()

        # 测试场景1: 空调控制
        print("\n--- Scenario 1: AC Control ---")
        request1 = "I'm feeling cold, turn on the AC to 26 degrees"
        print(f"Human Request: {request1}")
        plan1 = humanoid.plan_task(request1)
        humanoid.execute_plan(plan1)

        # 测试场景2: 照明控制
        print("\n--- Scenario 2: Lighting Control ---")
        request2 = "The room is too dark, turn on the lights"
        print(f"Human Request: {request2}")
        plan2 = humanoid.plan_task(request2)
        humanoid.execute_plan(plan2)

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def demo_arm_only():
    """演示机械臂独立工作 - 仅处理店铺库存管理"""
    print("\n" + "="*70)
    print("DEMO 2: Robotic Arm Only - Store Inventory Management")
    print("="*70)

    try:
        arm = RoboticArmPlanner()

        # 测试场景1: 单个物品检索
        print("\n--- Scenario 1: Single Item Retrieval ---")
        request1 = "Get water for the customer"
        print(f"Request from Humanoid: {request1}")
        plan1 = arm.plan_task(request1)
        arm.execute_plan(plan1)

        # 测试场景2: 多个物品检索
        print("\n--- Scenario 2: Multiple Items ---")
        request2 = "Prepare snacks and water for pickup"
        print(f"Request from Humanoid: {request2}")
        plan2 = arm.plan_task(request2)
        arm.execute_plan(plan2)

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def demo_coordinated_task():
    """演示两个规划器协同工作 - 完整的跨房间任务"""
    print("\n" + "="*70)
    print("DEMO 3: Coordinated Task - Humanoid + Robotic Arm")
    print("="*70)

    try:
        humanoid = HumanoidRobotPlanner()
        arm = RoboticArmPlanner()

        # 人类请求：需要从店铺获取物品
        print("\n--- Complete Task: Get Item from Store ---")
        human_request = "I'm thirsty, can you get me some water from the store?"
        print(f"Human Request: {human_request}")

        # 步骤1: 人形机器人规划任务
        print("\n[Step 1] Humanoid Robot Planning...")
        humanoid_plan = humanoid.plan_task(human_request)
        humanoid.execute_plan(humanoid_plan)

        # 步骤2: 人形机器人到达店铺后，向机械臂发送请求
        print("\n[Step 2] Humanoid arrives at store, requesting items...")
        arm_request = "Get water for pickup"
        print(f"Humanoid → Arm: {arm_request}")

        # 步骤3: 机械臂规划并执行物品检索
        print("\n[Step 3] Robotic Arm Planning...")
        arm_plan = arm.plan_task(arm_request)
        arm.execute_plan(arm_plan)

        # 步骤4: 总结协同任务
        print("\n[Step 4] Task Completion Summary")
        print("✅ Humanoid: Navigated to store, waiting for item")
        print("✅ Arm: Retrieved water, placed on counter")
        print("✅ Humanoid: Can now return home with water")
        print("✅ Task completed successfully!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def demo_complex_scenario():
    """演示复杂场景 - 环境设置 + 多物品获取"""
    print("\n" + "="*70)
    print("DEMO 4: Complex Scenario - Environment + Multiple Items")
    print("="*70)

    try:
        humanoid = HumanoidRobotPlanner()
        arm = RoboticArmPlanner()

        # 复杂请求：准备舒适的阅读环境并获取零食
        print("\n--- Complex Request: Reading Environment + Snacks ---")
        human_request = "Prepare a comfortable reading environment and get me some snacks and water"
        print(f"Human Request: {human_request}")

        # 人形机器人处理环境控制和物品获取协调
        print("\n[Phase 1] Humanoid Robot: Environment Setup + Store Trip Planning")
        humanoid_plan = humanoid.plan_task(human_request)
        humanoid.execute_plan(humanoid_plan)

        # 机械臂处理物品检索
        print("\n[Phase 2] Robotic Arm: Multiple Items Retrieval")
        arm_request = "Prepare snacks and water for pickup"
        arm_plan = arm.plan_task(arm_request)
        arm.execute_plan(arm_plan)

        print("\n[Phase 3] Task Completion")
        print("✅ Environment: Lights and AC adjusted for reading")
        print("✅ Items: Snacks and water retrieved and ready")
        print("✅ Humanoid: Returns home with items")
        print("✅ Complex task completed!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def run_all_tests():
    """运行所有规划器的测试用例"""
    print("\n" + "="*70)
    print("RUNNING ALL TEST CASES")
    print("="*70)

    try:
        print("\n🤖 HUMANOID ROBOT TESTS")
        humanoid = HumanoidRobotPlanner()
        humanoid.run_tests()

        print("\n\n🦾 ROBOTIC ARM TESTS")
        arm = RoboticArmPlanner()
        arm.run_tests()

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def interactive_mode():
    """交互式模式 - 用户可以选择使用哪个规划器"""
    print("\n" + "="*70)
    print("INTERACTIVE MODE - Dual Planner System")
    print("="*70)

    try:
        humanoid = HumanoidRobotPlanner()
        arm = RoboticArmPlanner()

        print("\nAvailable Commands:")
        print("  h <request>  - Send request to Humanoid Robot")
        print("  a <request>  - Send request to Robotic Arm")
        print("  c <request>  - Coordinated task (both planners)")
        print("  test         - Run all test cases")
        print("  quit / q     - Exit")

        while True:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'q']:
                print("👋 Goodbye!")
                break

            elif user_input.lower() == 'test':
                run_all_tests()

            elif user_input.startswith('h '):
                request = user_input[2:].strip()
                print(f"\n🤖 Humanoid Robot Processing: {request}")
                plan = humanoid.plan_task(request)
                humanoid.execute_plan(plan)

            elif user_input.startswith('a '):
                request = user_input[2:].strip()
                print(f"\n🦾 Robotic Arm Processing: {request}")
                plan = arm.plan_task(request)
                arm.execute_plan(plan)

            elif user_input.startswith('c '):
                request = user_input[2:].strip()
                print(f"\n🤝 Coordinated Task: {request}")
                print("\n[Humanoid Robot Planning...]")
                h_plan = humanoid.plan_task(request)
                humanoid.execute_plan(h_plan)

                # 如果任务涉及物品获取，也让机械臂规划
                if any(item in request.lower() for item in ['water', 'snacks', 'fruit', 'medicine', 'get', 'buy', 'fetch']):
                    print("\n[Robotic Arm Planning...]")
                    a_plan = arm.plan_task(f"Prepare items for: {request}")
                    arm.execute_plan(a_plan)

            else:
                print("❌ Invalid command. Use 'h', 'a', 'c', 'test', or 'quit'")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """主函数 - 提供多种演示模式"""
    print("="*70)
    print("🤖 DUAL PLANNER SYSTEM - Humanoid Robot + Robotic Arm")
    print("="*70)

    # 检查环境
    if not check_environment():
        return

    # 显示菜单
    print("\nSelect Demo Mode:")
    print("  1. Humanoid Robot Only (Home Control)")
    print("  2. Robotic Arm Only (Store Management)")
    print("  3. Coordinated Task (Simple)")
    print("  4. Complex Scenario (Environment + Items)")
    print("  5. Run All Tests")
    print("  6. Interactive Mode")
    print("  q. Quit")

    choice = input("\nEnter your choice (1-6 or q): ").strip()

    if choice == '1':
        demo_humanoid_only()
    elif choice == '2':
        demo_arm_only()
    elif choice == '3':
        demo_coordinated_task()
    elif choice == '4':
        demo_complex_scenario()
    elif choice == '5':
        run_all_tests()
    elif choice == '6':
        interactive_mode()
    elif choice.lower() == 'q':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
