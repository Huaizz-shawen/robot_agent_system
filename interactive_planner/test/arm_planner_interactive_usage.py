#!/usr/bin/env python3
# arm_planner_interactive_usage.py

"""
Example usage of Interactive Arm Planner
Demonstrates closed-loop control with step-by-step execution
"""

import os
from arm_planner_interactive import InteractiveArmPlanner


def example_water_retrieval():
    """
    Example: Water retrieval task with simulated feedback
    Demonstrates the closed-loop interactive flow
    """
    print("="*70)
    print("EXAMPLE: Water Retrieval Task (Interactive Mode)")
    print("="*70)

    # Check for API key
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("⚠️  DASHSCOPE_API_KEY not set. This is a simulation.")
        print("Set the API key to run with actual LLM planning.\n")
        return

    # Initialize planner
    planner = InteractiveArmPlanner()

    # Start task
    print("\n🎬 Starting task: 'Get water for the customer'\n")
    step_plan = planner.start_new_task("Get water for the customer")

    # Simulated feedback loop
    simulated_feedbacks = [
        "Water is available in stock (10 units remaining)",
        "Observation: Shelf A is visible. Level 1 has water bottles. Level 2 has snack boxes. Counter is clear.",
        "Pick operation complete. Water bottle is in gripper.",
        "Observation: Water bottle is securely held in gripper. Gripper pressure is stable.",
        "Water bottle is now on the counter.",
        "Observation: Water bottle is upright and stable on counter. Counter area is clear for pickup.",
        "Inventory updated. Water stock: 9 units remaining.",
        "Humanoid robot acknowledged: 'Thank you, I'll pick it up now.'"
    ]

    feedback_idx = 0

    while not planner.is_task_complete and "error" not in step_plan:
        # Execute current step
        feedback_request = planner.execute_step_and_wait(step_plan)
        print(f"❓ {feedback_request}")

        # Provide simulated feedback
        if feedback_idx < len(simulated_feedbacks):
            feedback = simulated_feedbacks[feedback_idx]
            print(f"\n[Simulated Feedback]: {feedback}\n")
            feedback_idx += 1

            # Plan next step
            step_plan = planner.provide_feedback(feedback)
        else:
            print("⚠️  No more simulated feedback available")
            break

    # Show final summary
    print("\n" + "="*70)
    print("TASK SUMMARY")
    print("="*70)
    summary = planner.get_task_summary()
    print(f"Total steps executed: {summary['steps_executed']}")
    print(f"Task complete: {summary['is_complete']}")
    print(f"Duration: {summary['duration_seconds']:.2f} seconds")
    print("="*70)


def example_out_of_stock():
    """
    Example: Handling out-of-stock scenario
    """
    print("\n" + "="*70)
    print("EXAMPLE: Out-of-Stock Handling (Interactive Mode)")
    print("="*70)

    if not os.getenv("DASHSCOPE_API_KEY"):
        print("⚠️  DASHSCOPE_API_KEY not set. Skipping this example.")
        return

    planner = InteractiveArmPlanner()

    print("\n🎬 Starting task: 'Get medicine'\n")
    step_plan = planner.start_new_task("Get medicine")

    # Simulated feedback for out-of-stock scenario
    simulated_feedbacks = [
        "Medicine is out of stock (0 units)",
        "Observation: Shelf C, Level 1 is empty. No medicine bottles visible.",
        "Humanoid acknowledged the message."
    ]

    feedback_idx = 0

    while not planner.is_task_complete and "error" not in step_plan:
        feedback_request = planner.execute_step_and_wait(step_plan)
        print(f"❓ {feedback_request}")

        if feedback_idx < len(simulated_feedbacks):
            feedback = simulated_feedbacks[feedback_idx]
            print(f"\n[Simulated Feedback]: {feedback}\n")
            feedback_idx += 1

            step_plan = planner.provide_feedback(feedback)
        else:
            break

    summary = planner.get_task_summary()
    print(f"\n✅ Task handled: {summary['is_complete']}")
    print(f"Steps executed: {summary['steps_executed']}")


def demonstrate_interactive_flow():
    """
    Demonstrates the interactive closed-loop control flow
    """
    print("="*70)
    print("INTERACTIVE ARM PLANNER - CLOSED-LOOP CONTROL DEMONSTRATION")
    print("="*70)
    print()
    print("This planner follows the closed-loop control pattern:")
    print()
    print("  ┌─────────────────────────────────────────────┐")
    print("  │  1. Initial Request from Humanoid           │")
    print("  └──────────────┬──────────────────────────────┘")
    print("                 │")
    print("                 ▼")
    print("  ┌─────────────────────────────────────────────┐")
    print("  │  2. Plan SINGLE Next Step                   │")
    print("  │     - Send context + history to LLM         │")
    print("  │     - Get ONE action to execute             │")
    print("  └──────────────┬──────────────────────────────┘")
    print("                 │")
    print("                 ▼")
    print("  ┌─────────────────────────────────────────────┐")
    print("  │  3. Execute That Step                       │")
    print("  │     - Perform the action                    │")
    print("  │     - Display what was done                 │")
    print("  └──────────────┬──────────────────────────────┘")
    print("                 │")
    print("                 ▼")
    print("  ┌─────────────────────────────────────────────┐")
    print("  │  4. Wait for Environment Feedback           │")
    print("  │     - Pause execution                       │")
    print("  │     - Get observation/confirmation          │")
    print("  └──────────────┬──────────────────────────────┘")
    print("                 │")
    print("                 ▼")
    print("  ┌─────────────────────────────────────────────┐")
    print("  │  5. Update Context with Feedback            │")
    print("  │     - Add to conversation history           │")
    print("  │     - Check if task is complete             │")
    print("  └──────────────┬──────────────────────────────┘")
    print("                 │")
    print("                 ▼")
    print("           [Loop back to step 2]")
    print()
    print("="*70)
    print()

    # Run examples if API key is available
    if os.getenv("DASHSCOPE_API_KEY"):
        example_water_retrieval()
        example_out_of_stock()
    else:
        print("ℹ️  Set DASHSCOPE_API_KEY environment variable to run live examples")
        print("Example: export DASHSCOPE_API_KEY='your-api-key-here'")


if __name__ == "__main__":
    demonstrate_interactive_flow()
