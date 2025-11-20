# interactive_planner_usage.py

"""
Usage examples for the Interactive Closed-Loop Humanoid Robot Planner
"""

from humanoid_planner_interactive import HumanoidRobotPlannerInteractive


def example_manual_step_by_step():
    """
    Example: Manual step-by-step execution with human approval
    """
    print("\n" + "="*70)
    print("📌 Example 1: Manual Step-by-Step Execution")
    print("="*70)

    planner = HumanoidRobotPlannerInteractive()

    # Test connection
    if not planner.test_connection():
        print("Cannot connect to API")
        return

    # Start a task
    human_request = "I need some water"
    session_id = "example_session_001"

    print(f"\n🎯 Starting task: {human_request}")
    print("-" * 70)

    # Get first step (with debug enabled to see what LLM returns)
    step_plan = planner.start_task(human_request, session_id, debug=True)

    if "error" in step_plan:
        print(f"❌ Error: {step_plan['error']}")
        if "raw_response" in step_plan:
            print(f"\n📄 Raw response preview:")
            print(step_plan['raw_response'])
        return

    print("\n📋 First step generated:")
    print(f"   Action: {step_plan['next_step']['action']}")
    print(f"   Type: {step_plan['next_step']['action_type']}")
    print(f"   Rationale: {step_plan['next_step']['rationale']}")

    # Simulate user approval
    print("\n👤 User approves step 1")

    # Execute step 1
    exec_result = planner.execute_step(
        session_id,
        step_plan,
        execution_result="User acknowledged the message"
    )
    print(f"✅ Step 1 executed: {exec_result['execution_result']}")

    # Get next step
    print("\n⏭️  Planning step 2...")
    step_plan = planner.plan_next_step(session_id)

    print("\n📋 Second step generated:")
    print(f"   Action: {step_plan['next_step']['action']}")
    print(f"   Type: {step_plan['next_step']['action_type']}")
    print(f"   Rationale: {step_plan['next_step']['rationale']}")

    print("\n✅ Example complete - showing how to do step-by-step planning")


def example_auto_approval():
    """
    Example: Automatic approval for testing/demo
    """
    print("\n" + "="*70)
    print("📌 Example 2: Auto-Approval Mode (Demo)")
    print("="*70)

    planner = HumanoidRobotPlannerInteractive()

    if not planner.test_connection():
        print("Cannot connect to API")
        return

    # Run with auto-approval
    planner.interactive_execution_loop(
        human_request="Turn on the air conditioner",
        auto_approve=True,
        debug=False
    )


def example_advanced_usage():
    """
    Example: Advanced usage with session management
    """
    print("\n" + "="*70)
    print("📌 Example 3: Advanced Session Management")
    print("="*70)

    planner = HumanoidRobotPlannerInteractive()

    if not planner.test_connection():
        print("Cannot connect to API")
        return

    # Start multiple tasks
    tasks = [
        ("task_001", "Make the room comfortable"),
        ("task_002", "Get me some snacks"),
    ]

    for session_id, request in tasks:
        print(f"\n🆕 Starting: {request} (ID: {session_id})")

        # Start task
        step_plan = planner.start_task(request, session_id)

        if "error" not in step_plan:
            next_step = step_plan['next_step']
            print(f"   First action: {next_step['action']}")

            # Get session info
            info = planner.get_session_info(session_id)
            print(f"   Session info: {info['steps_completed']} steps completed")

    print("\n✅ Advanced example complete")


def example_with_modification():
    """
    Example: Handling user modifications and feedback
    """
    print("\n" + "="*70)
    print("📌 Example 4: User Modification Workflow")
    print("="*70)

    planner = HumanoidRobotPlannerInteractive()

    if not planner.test_connection():
        print("Cannot connect to API")
        return

    session_id = "modification_demo"
    request = "I'm cold, please help"

    # Start task
    step_plan = planner.start_task(request, session_id)

    print(f"\n📋 Step 1 Plan:")
    print(f"   Action: {step_plan['next_step']['action']}")

    # User wants to modify
    print("\n👤 User: 'I want you to check the temperature first'")
    print("   (In a real implementation, this would trigger re-planning)")

    # Execute with modification note
    exec_result = planner.execute_step(
        session_id,
        step_plan,
        execution_result="Observation: Temperature is 22°C",
        user_feedback="modified - user requested temperature check"
    )

    print(f"\n✅ Executed with modification: {exec_result['user_feedback']}")

    # Continue with next step
    step_plan = planner.plan_next_step(session_id)
    print(f"\n📋 Step 2 (adapted to previous result):")
    print(f"   Action: {step_plan['next_step']['action']}")
    print(f"   Context-aware: Uses previous temperature reading")


def example_comparison():
    """
    Compare old (open-loop) vs new (closed-loop) approach
    """
    print("\n" + "="*70)
    print("📌 Comparison: Open-Loop vs Closed-Loop Planning")
    print("="*70)

    print("\n🔓 OLD APPROACH (Open-Loop):")
    print("   1. User: 'I need water'")
    print("   2. Planner generates ALL steps:")
    print("      Step 1: talk_with_human")
    print("      Step 2: get_observation")
    print("      Step 3: navigate_to_store")
    print("      Step 4: request_item")
    print("      ... (all 10 steps)")
    print("   3. Execute all steps sequentially")
    print("   4. No human feedback between steps")
    print("   ❌ Problem: Cannot adapt if something goes wrong mid-execution")

    print("\n🔒 NEW APPROACH (Closed-Loop):")
    print("   1. User: 'I need water'")
    print("   2. Planner generates ONLY Step 1:")
    print("      Step 1: talk_with_human('I'll get water')")
    print("   3. ⏸️  WAIT for human approval")
    print("   4. Execute Step 1")
    print("   5. Planner generates Step 2 (based on Step 1 result):")
    print("      Step 2: get_observation()")
    print("   6. ⏸️  WAIT for human approval")
    print("   7. Execute Step 2")
    print("   8. ... continue until task complete")
    print("   ✅ Benefit: Human can intervene, modify, or cancel at any time")
    print("   ✅ Benefit: Planner adapts based on actual execution results")


def main():
    """Run all examples"""
    print("🤖 Interactive Humanoid Robot Planner - Usage Examples")
    print("="*70)

    print("\nAvailable examples:")
    print("1. Manual step-by-step execution")
    print("2. Auto-approval mode (demo)")
    print("3. Advanced session management")
    print("4. User modification workflow")
    print("5. Comparison: Open-loop vs Closed-loop")
    print("6. Run all examples")

    choice = input("\nSelect example (1-6, or 'q' to quit): ").strip()

    if choice == '1':
        example_manual_step_by_step()
    elif choice == '2':
        example_auto_approval()
    elif choice == '3':
        example_advanced_usage()
    elif choice == '4':
        example_with_modification()
    elif choice == '5':
        example_comparison()
    elif choice == '6':
        print("\n🚀 Running all examples...")
        example_comparison()
        example_manual_step_by_step()
        # example_auto_approval()  # Commented out to avoid long execution
        example_advanced_usage()
        example_with_modification()
        print("\n✅ All examples completed!")
    elif choice.lower() in ['q', 'quit']:
        print("👋 Goodbye!")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
