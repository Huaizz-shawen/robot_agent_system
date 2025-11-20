#!/usr/bin/env python3
# interactive_planner_usage.py

"""
Usage Example: Interactive Humanoid Robot Planner
Demonstrates the closed-loop, single-step planning system
"""

import os
from humanoid_planner_interactive import InteractiveHumanoidPlanner


def example_simple_task():
    """
    Example 1: Simple device control task
    Task: "I'm feeling cold"
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Device Control (AC)")
    print("="*70)

    # Initialize planner
    planner = InteractiveHumanoidPlanner()

    # Start task
    task_request = "I'm feeling cold"
    step_plan = planner.start_new_task(task_request)

    # Simulate interactive loop
    feedback_sequence = [
        "Observation: Living room visible. Human is sitting on couch. AC is currently off. Room appears dim.",
        "AC turned on successfully, temperature set to 24°C",
        "Human says: 'Thank you, that's perfect!'"
    ]

    for feedback in feedback_sequence:
        if planner.is_task_complete:
            break

        # Execute step (in real system, this would be actual robot execution)
        feedback_request = planner.execute_step_and_wait(step_plan)
        print(f"❓ System asks: {feedback_request}")

        # Provide feedback
        print(f"📥 Providing feedback: {feedback}")
        step_plan = planner.provide_feedback(feedback)

    # Show summary
    print("\n📊 TASK SUMMARY:")
    summary = planner.get_task_summary()
    print(f"  Steps executed: {summary['steps_executed']}")
    print(f"  Task complete: {summary['is_complete']}")
    print(f"  Duration: {summary['duration_seconds']:.2f} seconds")


def example_item_retrieval():
    """
    Example 2: Item retrieval from store
    Task: "I need some water"
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Item Retrieval from Store")
    print("="*70)

    # Initialize planner
    planner = InteractiveHumanoidPlanner()

    # Start task
    task_request = "I need some water"
    step_plan = planner.start_new_task(task_request)

    # Simulate interactive loop with feedback
    feedback_sequence = [
        "Human is in living room, no water visible nearby",
        "Human says: 'Okay, thank you'",
        "Navigation successful - arrived at store",
        "Store robot says: 'Water request received, preparing now'",
        "Waiting... (30 seconds elapsed)",
        "Observation: Water bottle is on the counter, ready for pickup",
        "Successfully picked up water, returning home",
        "Navigation successful - arrived back home",
        "Human says: 'Thank you so much!' and takes the water"
    ]

    for feedback in feedback_sequence:
        if planner.is_task_complete:
            break

        # Execute step
        feedback_request = planner.execute_step_and_wait(step_plan)
        print(f"❓ System asks: {feedback_request}")

        # Provide feedback
        print(f"📥 Providing feedback: {feedback}")
        step_plan = planner.provide_feedback(feedback)

    # Show summary
    print("\n📊 TASK SUMMARY:")
    summary = planner.get_task_summary()
    print(f"  Steps executed: {summary['steps_executed']}")
    print(f"  Task complete: {summary['is_complete']}")
    print(f"  Duration: {summary['duration_seconds']:.2f} seconds")


def example_error_recovery():
    """
    Example 3: Error recovery scenario
    Task: "Go to the store and get snacks"
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Error Recovery (Navigation Blocked)")
    print("="*70)

    # Initialize planner
    planner = InteractiveHumanoidPlanner()

    # Start task
    task_request = "Go to the store and get snacks"
    step_plan = planner.start_new_task(task_request)

    # Simulate with an error and recovery
    feedback_sequence = [
        "Observation: Human is present in living room",
        "Human says: 'Okay, please be careful'",
        "Navigation FAILED - obstacle detected in hallway",  # ERROR!
        "Human says: 'I moved the obstacle, you can try again now'",
        "Navigation successful - arrived at store (second attempt)",
        "Store robot says: 'Snacks request received'",
        "Waiting... (30 seconds)",
        "Observation: Snacks are on counter",
        "Picked up snacks, returning home",
        "Arrived back home",
        "Human says: 'Great, thanks!' and takes the snacks"
    ]

    for feedback in feedback_sequence:
        if planner.is_task_complete:
            break

        # Execute step
        feedback_request = planner.execute_step_and_wait(step_plan)
        print(f"❓ System asks: {feedback_request}")

        # Provide feedback
        print(f"📥 Providing feedback: {feedback}")
        step_plan = planner.provide_feedback(feedback)

    # Show summary
    print("\n📊 TASK SUMMARY:")
    summary = planner.get_task_summary()
    print(f"  Steps executed: {summary['steps_executed']}")
    print(f"  Task complete: {summary['is_complete']}")
    print(f"  Duration: {summary['duration_seconds']:.2f} seconds")


def example_programmatic_usage():
    """
    Example 4: How to integrate the planner into your own code
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Programmatic Usage Pattern")
    print("="*70)

    # Initialize planner
    planner = InteractiveHumanoidPlanner()

    # Start a task
    task_request = "Turn on the lights"
    current_step = planner.start_new_task(task_request)

    # Main loop: execute -> get feedback -> plan next
    while not planner.is_task_complete:
        # Check for errors
        if "error" in current_step:
            print(f"Error occurred: {current_step['error']}")
            break

        # Display step to execute
        next_action = current_step.get("next_step", {})
        print(f"\n🎯 Next Action: {next_action.get('action')}")
        print(f"📦 Parameters: {next_action.get('parameters')}")

        # Execute step (call your robot control functions here)
        feedback_request = planner.execute_step_and_wait(current_step)

        # Get feedback from your sensors/user
        # In real implementation, this would be:
        # - Sensor readings
        # - Vision system output
        # - User voice input
        # - Success/failure indicators from actuators
        print(f"\n❓ {feedback_request}")

        # Simulated feedback for this example
        if next_action.get('action') == 'get_observation':
            feedback = "Observation: Room lights are currently off"
        elif next_action.get('action') == 'control_light':
            feedback = "Lights turned on successfully"
        elif next_action.get('action') == 'talk_with_human':
            feedback = "Human acknowledged the message"
        else:
            feedback = "Action completed successfully"

        print(f"📥 Feedback: {feedback}")

        # Provide feedback and get next step
        current_step = planner.provide_feedback(feedback)

    print("\n✅ Task completed!")
    print(planner.get_task_summary())


def demonstrate_all_examples():
    """Run all examples"""
    # Check API key
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("⚠️  Warning: DASHSCOPE_API_KEY environment variable not set.")
        print("Please set it using: export DASHSCOPE_API_KEY='your-api-key'")
        print("\nRunning with mock mode (no actual API calls)...")
        print("Set the API key to see real planner behavior.\n")
        return

    print("\n" + "🤖"*35)
    print("INTERACTIVE HUMANOID PLANNER - USAGE EXAMPLES")
    print("🤖"*35)

    try:
        # Run examples
        example_simple_task()
        input("\n⏸️  Press Enter to continue to next example...")

        example_item_retrieval()
        input("\n⏸️  Press Enter to continue to next example...")

        example_error_recovery()
        input("\n⏸️  Press Enter to continue to next example...")

        example_programmatic_usage()

        print("\n" + "✅"*35)
        print("ALL EXAMPLES COMPLETED")
        print("✅"*35)

    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        example_name = sys.argv[1].lower()
        if example_name == "simple":
            example_simple_task()
        elif example_name == "retrieval":
            example_item_retrieval()
        elif example_name == "error":
            example_error_recovery()
        elif example_name == "programmatic":
            example_programmatic_usage()
        else:
            print(f"Unknown example: {example_name}")
            print("Available examples: simple, retrieval, error, programmatic")
    else:
        demonstrate_all_examples()
