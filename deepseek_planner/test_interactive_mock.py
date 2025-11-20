# test_interactive_mock.py

"""
Test the interactive planner with mock API responses
(for testing when API is not available)
"""

import json
from humanoid_planner_interactive import HumanoidRobotPlannerInteractive, TaskSession

# Mock the API request method
def mock_api_request(self, messages):
    """Mock API response with proper interactive format"""

    # Get the user message to determine context
    user_content = messages[-1]['content']

    # Check if this is first step or continuation
    if "This is the first step" in user_content:
        # First step response
        mock_response = {
            "task_understanding": {
                "original_request": "I need some water",
                "current_goal": "Get water for the user",
                "progress_summary": "Starting task, no steps completed yet"
            },
            "next_step": {
                "step_number": 1,
                "agent": "Unitree-G1 humanoid_robot",
                "location": "home",
                "action": "get_observation",
                "action_type": "sense",
                "parameters": {},
                "rationale": "Check current room state and verify where water sources are available",
                "expected_outcome": "Understanding of current environment and available water sources",
                "estimated_duration": "2-3 seconds"
            },
            "task_status": {
                "is_complete": False,
                "completion_percentage": 10,
                "remaining_steps_estimate": "6-8 more steps needed"
            },
            "human_feedback_request": {
                "question": "Should I observe the room to check for water sources?",
                "options": ["proceed", "modify", "cancel"],
                "waiting_for": "permission to observe the environment"
            },
            "contingency_note": "If observation shows water is already available nearby, can skip store trip"
        }
    elif "Steps completed so far (1)" in user_content:
        # Second step response (after first observation)
        mock_response = {
            "task_understanding": {
                "original_request": "I need some water",
                "current_goal": "Inform user and prepare to get water",
                "progress_summary": "Observed room - no water nearby, will need to get from store"
            },
            "next_step": {
                "step_number": 2,
                "agent": "Unitree-G1 humanoid_robot",
                "location": "home",
                "action": "talk_with_human",
                "action_type": "talk",
                "parameters": {
                    "message": "I don't see any water nearby. I'll go to the store to get water for you."
                },
                "rationale": "Inform user of my plan before leaving for the store",
                "expected_outcome": "User is aware of my plan and can provide feedback",
                "estimated_duration": "1 second"
            },
            "task_status": {
                "is_complete": False,
                "completion_percentage": 25,
                "remaining_steps_estimate": "5-6 more steps needed"
            },
            "human_feedback_request": {
                "question": "Should I tell you my plan to get water from the store?",
                "options": ["proceed", "modify", "cancel"],
                "waiting_for": "permission to communicate plan"
            },
            "contingency_note": "If user cancels, ask for clarification on alternatives"
        }
    elif "Steps completed so far (2)" in user_content:
        # Third step response (after talking)
        mock_response = {
            "task_understanding": {
                "original_request": "I need some water",
                "current_goal": "Navigate to store to get water",
                "progress_summary": "User has been informed and approved the plan"
            },
            "next_step": {
                "step_number": 3,
                "agent": "Unitree-G1 humanoid_robot",
                "location": "in_transit",
                "action": "navigate_to_store",
                "action_type": "act",
                "parameters": {},
                "rationale": "User approved the plan, now moving to store location",
                "expected_outcome": "Arrival at store, ready to request water",
                "estimated_duration": "30 seconds"
            },
            "task_status": {
                "is_complete": False,
                "completion_percentage": 40,
                "remaining_steps_estimate": "4-5 more steps needed"
            },
            "human_feedback_request": {
                "question": "Should I navigate to the store now?",
                "options": ["proceed", "modify", "cancel"],
                "waiting_for": "permission to move to store"
            },
            "contingency_note": "If navigation fails or path is blocked, will report to user"
        }
    else:
        # Default completion response
        mock_response = {
            "task_understanding": {
                "original_request": "I need some water",
                "current_goal": "Task complete",
                "progress_summary": "Successfully completed all steps"
            },
            "next_step": {
                "step_number": 4,
                "agent": "Unitree-G1 humanoid_robot",
                "location": "home",
                "action": "talk_with_human",
                "action_type": "talk",
                "parameters": {
                    "message": "Here is your water!"
                },
                "rationale": "Confirm delivery to user",
                "expected_outcome": "User receives water and acknowledgment",
                "estimated_duration": "1 second"
            },
            "task_status": {
                "is_complete": True,
                "completion_percentage": 100,
                "remaining_steps_estimate": "0 steps - task complete"
            },
            "human_feedback_request": {
                "question": "Should I deliver the water to you?",
                "options": ["proceed"],
                "waiting_for": "final confirmation"
            },
            "contingency_note": "None - task completing"
        }

    # Format as API response
    return {
        'choices': [{
            'message': {
                'content': json.dumps(mock_response, indent=2)
            }
        }]
    }


def test_mock_interactive():
    """Test interactive planner with mock responses"""
    print("="*70)
    print("🧪 Testing Interactive Planner with Mock Responses")
    print("="*70)

    # Create planner
    planner = HumanoidRobotPlannerInteractive()

    # Replace API request method with mock
    planner._make_api_request = lambda messages: mock_api_request(planner, messages)

    print("\n✅ Planner initialized with mock API")
    print("="*70)

    # Test task
    human_request = "I need some water"
    session_id = "mock_test_001"

    print(f"\n📝 Task: {human_request}\n")

    # Step 1
    print("🔄 Planning Step 1...")
    step_plan = planner.start_task(human_request, session_id, debug=False)

    if "error" in step_plan:
        print(f"❌ Error: {step_plan['error']}")
        return

    print(f"\n📋 Step 1 Plan:")
    print(f"   Action: {step_plan['next_step']['action']}")
    print(f"   Type: {step_plan['next_step']['action_type']}")
    print(f"   Rationale: {step_plan['next_step']['rationale']}")
    print(f"   Question: {step_plan['human_feedback_request']['question']}")

    # Simulate user approval
    print(f"\n👤 User: proceed")

    # Execute Step 1
    result = planner.execute_step(
        session_id,
        step_plan,
        execution_result="Observation: Living room, temperature 24°C, no water visible"
    )
    print(f"✅ Executed: {result['execution_result']}")

    # Step 2
    print(f"\n{'='*70}")
    print("🔄 Planning Step 2...")
    step_plan = planner.plan_next_step(session_id, debug=False)

    print(f"\n📋 Step 2 Plan:")
    print(f"   Action: {step_plan['next_step']['action']}")
    print(f"   Type: {step_plan['next_step']['action_type']}")
    print(f"   Parameters: {step_plan['next_step'].get('parameters', {})}")
    print(f"   Rationale: {step_plan['next_step']['rationale']}")
    print(f"   Question: {step_plan['human_feedback_request']['question']}")

    print(f"\n👤 User: proceed")

    # Execute Step 2
    result = planner.execute_step(
        session_id,
        step_plan,
        execution_result="User acknowledged the plan"
    )
    print(f"✅ Executed: {result['execution_result']}")

    # Step 3
    print(f"\n{'='*70}")
    print("🔄 Planning Step 3...")
    step_plan = planner.plan_next_step(session_id, debug=False)

    print(f"\n📋 Step 3 Plan:")
    print(f"   Action: {step_plan['next_step']['action']}")
    print(f"   Type: {step_plan['next_step']['action_type']}")
    print(f"   Rationale: {step_plan['next_step']['rationale']}")
    print(f"   Progress: {step_plan['task_status']['completion_percentage']}%")

    print(f"\n👤 User: proceed")

    # Execute Step 3
    result = planner.execute_step(
        session_id,
        step_plan,
        execution_result="Successfully navigated to store"
    )
    print(f"✅ Executed: {result['execution_result']}")

    # Show session summary
    print(f"\n{'='*70}")
    print("📊 Session Summary")
    print(f"{'='*70}")
    info = planner.get_session_info(session_id)
    print(f"Session ID: {info['session_id']}")
    print(f"Original Request: {info['original_request']}")
    print(f"Steps Completed: {info['steps_completed']}")
    print(f"Task Complete: {info['is_complete']}")

    print(f"\n✅ Mock test complete! The interactive planner is working correctly.")
    print(f"{'='*70}")

    return planner


def test_comparison_with_mock():
    """Show comparison between open and closed loop with mock"""
    print("\n" + "="*70)
    print("📊 Comparison: Open-Loop vs Closed-Loop (Mock Demo)")
    print("="*70)

    print("\n🔓 OLD APPROACH (Open-Loop):")
    print("   Request → Generate ALL 10 steps → Execute all → Done")
    print("   ❌ Cannot adapt if environment changes mid-execution")

    print("\n🔒 NEW APPROACH (Closed-Loop):")
    print("   Request → Step 1 → Approve → Execute → Result")
    print("           → Step 2 (using Step 1 result) → Approve → Execute")
    print("           → Step 3 (using Steps 1-2 results) → Approve → Execute")
    print("           → ... continues until complete")
    print("   ✅ Adapts based on actual execution results")
    print("   ✅ Human can intervene at any step")

    print("\n" + "="*70)


if __name__ == "__main__":
    print("🤖 Interactive Humanoid Robot Planner - Mock Testing")
    print("="*70)
    print("\nThis demonstrates the interactive planner with mock API responses")
    print("(Use this when the real DeepSeek API is not available)")
    print("="*70)

    # Run tests
    test_comparison_with_mock()
    planner = test_mock_interactive()

    print("\n💡 To test with real API:")
    print("   1. Ensure DeepSeek API endpoint is accessible")
    print("   2. Run: python humanoid_planner_interactive.py")
    print("   3. Or: python interactive_planner_usage.py")
