#!/usr/bin/env python3
# humanoid_usage_example.py

"""
Example: Using Interactive Humanoid Planner with Executor
Demonstrates automated closed-loop planning and execution
"""

import os
from humanoid_planner_interactive import InteractiveHumanoidPlanner


def example_automated_task():
    """
    Example 1: Fully automated task execution
    The planner plans steps, executor executes them, and feedback is automatic
    """
    print("="*70)
    print("EXAMPLE 1: Automated Task - 'I'm feeling cold'")
    print("="*70 + "\n")

    # Check API key
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("⚠️  Please set DASHSCOPE_API_KEY environment variable")
        return

    # Initialize planner in simulation mode
    planner = InteractiveHumanoidPlanner(
        simulation_mode=True,  # Use simulation for testing
        verbose=True           # Show detailed logs
    )

    # Start task - this will automatically plan and execute all steps
    task_request = "I'm feeling cold"
    current_plan = planner.start_new_task(task_request)

    # Automatic execution loop
    while current_plan and "error" not in current_plan and not planner.is_task_complete:
        # Execute step and get feedback from executor
        execution_feedback = planner.execute_step_and_wait(current_plan)

        # Provide feedback to planner for next step
        current_plan = planner.provide_feedback(execution_feedback)

    # Show task summary
    print("\n" + "="*70)
    print("TASK COMPLETED - SUMMARY")
    print("="*70)
    summary = planner.get_task_summary()
    print(f"Total steps executed: {summary['steps_executed']}")
    print(f"Duration: {summary['duration_seconds']:.2f} seconds")
    print(f"Success: {summary['is_complete']}")

    # Show execution statistics
    stats = planner.get_execution_statistics()
    print(f"\nExecution Statistics:")
    print(f"  Total executions: {stats['total_executions']}")
    print(f"  Success rate: {stats['success_rate']*100:.1f}%")


def example_programmatic_control():
    """
    Example 2: Programmatic control with custom logic
    """
    print("\n\n" + "="*70)
    print("EXAMPLE 2: Programmatic Control - Item Retrieval")
    print("="*70 + "\n")

    if not os.getenv("DASHSCOPE_API_KEY"):
        print("⚠️  Please set DASHSCOPE_API_KEY environment variable")
        return

    planner = InteractiveHumanoidPlanner(simulation_mode=True, verbose=False)

    # Start task
    task_request = "I need some water"
    current_plan = planner.start_new_task(task_request)

    step_count = 0
    max_steps = 10  # Safety limit

    while current_plan and not planner.is_task_complete and step_count < max_steps:
        step_count += 1

        # Execute step
        feedback = planner.execute_step_and_wait(current_plan)

        # Custom logic: check if navigation failed
        if "error" in feedback.lower() or "fail" in feedback.lower():
            print(f"\n⚠️  Step {step_count} encountered issue: {feedback}")
            # Could add custom recovery logic here

        # Get next step
        current_plan = planner.provide_feedback(feedback)

    print(f"\n✅ Task completed in {step_count} steps")


def example_real_hardware_preparation():
    """
    Example 3: Preparing for real hardware execution
    Shows how to structure code for real Unitree-G1 deployment
    """
    print("\n\n" + "="*70)
    print("EXAMPLE 3: Real Hardware Preparation")
    print("="*70 + "\n")

    print("When you're ready to deploy on real Unitree-G1:")
    print("\n1. Implement hardware interfaces in humanoid_executor.py:")
    print("   - _initialize_hardware(): Connect to robot controller")
    print("   - _execute_act(): Real navigation/manipulation APIs")
    print("   - _execute_sense(): Real camera + VLM integration")
    print("   - _execute_tool(): Smart home device APIs")
    print("\n2. Initialize planner with simulation_mode=False:")
    print("   planner = InteractiveHumanoidPlanner(simulation_mode=False)")
    print("\n3. Add safety checks before real execution:")
    print("   - Emergency stop mechanisms")
    print("   - Collision detection")
    print("   - Battery monitoring")
    print("   - Human safety zones")
    print("\n4. Test thoroughly in simulation before hardware deployment!")


def example_switching_modes():
    """
    Example 4: Switching between simulation and real hardware
    """
    print("\n\n" + "="*70)
    print("EXAMPLE 4: Switching Execution Modes")
    print("="*70 + "\n")

    if not os.getenv("DASHSCOPE_API_KEY"):
        print("⚠️  Please set DASHSCOPE_API_KEY environment variable")
        return

    planner = InteractiveHumanoidPlanner(simulation_mode=True, verbose=True)

    print("\n🎮 Starting in SIMULATION mode...")
    print(f"Current mode: {'SIM' if planner.executor.simulation_mode else 'REAL'}\n")

    # You can switch modes dynamically
    # planner.switch_execution_mode(simulation_mode=False)
    # print(f"Switched to: {'SIM' if planner.executor.simulation_mode else 'REAL'}")

    print("Note: Switch to real hardware mode only when:")
    print("  ✓ All hardware APIs are implemented")
    print("  ✓ Safety systems are in place")
    print("  ✓ Testing environment is prepared")
    print("  ✓ Emergency stop is accessible")


if __name__ == "__main__":
    print("🤖 Interactive Humanoid Planner - Usage Examples\n")

    # Run examples
    example_automated_task()
    example_programmatic_control()
    example_real_hardware_preparation()
    example_switching_modes()

    print("\n\n" + "="*70)
    print("Examples Complete!")
    print("="*70)
    print("\nTo run the interactive CLI, use:")
    print("  python humanoid_planner_interactive.py")
    print("\nFor real hardware deployment:")
    print("  1. Implement TODO sections in humanoid_executor.py")
    print("  2. Test with simulation_mode=True first")
    print("  3. Deploy with simulation_mode=False on real robot")
