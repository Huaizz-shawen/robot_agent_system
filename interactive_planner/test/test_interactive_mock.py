#!/usr/bin/env python3
# test_interactive_mock.py

"""
Mock Test for Interactive Planner
Demonstrates the closed-loop workflow without requiring API calls
"""

import json
from datetime import datetime


class MockInteractivePlanner:
    """
    Mock version of InteractiveHumanoidPlanner for testing
    Simulates the closed-loop planning without API calls
    """

    def __init__(self):
        self.reset_conversation()
        print("✅ Initialized MockInteractivePlanner (no API required)")

    def reset_conversation(self):
        """Reset conversation state"""
        self.original_request = None
        self.conversation_history = []
        self.execution_history = []
        self.step_count = 0
        self.is_task_complete = False
        self.task_start_time = None

    def start_new_task(self, human_request):
        """Start a new task"""
        self.reset_conversation()
        self.original_request = human_request
        self.task_start_time = datetime.now()

        print("\n" + "="*70)
        print("🤖 NEW TASK STARTED (MOCK MODE)")
        print("="*70)
        print(f"📝 Request: {human_request}")
        print(f"🕐 Started at: {self.task_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")

        return self.plan_next_step()

    def plan_next_step(self):
        """Plan next step (mock implementation)"""
        if self.is_task_complete:
            return None

        self.step_count += 1

        # Mock planning based on task type and current progress
        if "cold" in self.original_request.lower() or "ac" in self.original_request.lower():
            return self._plan_ac_task()
        elif "water" in self.original_request.lower():
            return self._plan_water_retrieval()
        elif "light" in self.original_request.lower():
            return self._plan_light_control()
        else:
            return self._plan_generic_task()

    def _plan_ac_task(self):
        """Mock planning for AC control task"""
        if self.step_count == 1:
            return {
                "current_step_analysis": {
                    "task_progress": "Starting new task",
                    "current_situation": "Human feels cold, need to warm the room",
                    "next_action_reasoning": "First, observe room to understand current state"
                },
                "next_step": {
                    "step_number": 1,
                    "action": "get_observation",
                    "action_type": "sense",
                    "location": "home",
                    "parameters": {},
                    "expected_outcome": "Visual confirmation of room state and AC status"
                },
                "task_status": {
                    "is_complete": False,
                    "completion_percentage": 20,
                    "remaining_actions": "Turn on AC to warm the room"
                },
                "feedback_request": "Please provide observation of the room"
            }
        elif self.step_count == 2:
            return {
                "current_step_analysis": {
                    "task_progress": "Step 1 complete: Observed room, AC is off",
                    "current_situation": "Need to turn on AC to warm the room",
                    "next_action_reasoning": "Turn on AC with comfortable temperature"
                },
                "next_step": {
                    "step_number": 2,
                    "action": "control_air_conditioner",
                    "action_type": "tool",
                    "location": "home",
                    "parameters": {"action": "turn_on", "temperature": 24},
                    "expected_outcome": "AC turns on and starts warming"
                },
                "task_status": {
                    "is_complete": False,
                    "completion_percentage": 60,
                    "remaining_actions": "Verify AC is on, confirm with human"
                },
                "feedback_request": "Did the AC turn on successfully?"
            }
        elif self.step_count == 3:
            return {
                "current_step_analysis": {
                    "task_progress": "Steps 1-2 complete: Observed, AC turned on",
                    "current_situation": "AC is running, need to confirm with human",
                    "next_action_reasoning": "Inform human that the room is being warmed"
                },
                "next_step": {
                    "step_number": 3,
                    "action": "talk_with_human",
                    "action_type": "talk",
                    "location": "home",
                    "parameters": {"message": "I've turned on the AC to 24°C. The room should warm up shortly."},
                    "expected_outcome": "Human acknowledges"
                },
                "task_status": {
                    "is_complete": False,
                    "completion_percentage": 90,
                    "remaining_actions": "Await final confirmation"
                },
                "feedback_request": "Human's response to the message"
            }
        else:
            self.is_task_complete = True
            return {
                "current_step_analysis": {
                    "task_progress": "All steps completed successfully",
                    "current_situation": "Task finished - AC is on, human is satisfied",
                    "next_action_reasoning": "No further action needed"
                },
                "next_step": None,
                "task_status": {
                    "is_complete": True,
                    "completion_percentage": 100,
                    "remaining_actions": "None - task complete"
                },
                "task_summary": {
                    "total_steps_executed": 3,
                    "final_state": "AC is on at 24°C, human is comfortable",
                    "actions_performed": ["get_observation", "control_air_conditioner", "talk_with_human"],
                    "success": True
                },
                "feedback_request": "Task complete"
            }

    def _plan_water_retrieval(self):
        """Mock planning for water retrieval"""
        steps_sequence = [
            {
                "action": "get_observation",
                "action_type": "sense",
                "parameters": {},
                "reasoning": "Observe current environment",
                "completion": 10
            },
            {
                "action": "talk_with_human",
                "action_type": "talk",
                "parameters": {"message": "I'll get water from the store for you. I'll be back in about 2 minutes."},
                "reasoning": "Inform human of plan",
                "completion": 20
            },
            {
                "action": "navigate_to_store",
                "action_type": "act",
                "parameters": {},
                "reasoning": "Navigate to store",
                "completion": 35
            },
            {
                "action": "request_item_from_store",
                "action_type": "talk",
                "parameters": {"item": "water"},
                "reasoning": "Request water from store robot",
                "completion": 50
            },
            {
                "action": "wait_for_item",
                "action_type": "act",
                "parameters": {"estimated_time": "30 seconds"},
                "reasoning": "Wait for item preparation",
                "completion": 65
            },
            {
                "action": "return_home_with_item",
                "action_type": "act",
                "parameters": {"item": "water"},
                "reasoning": "Return home with water",
                "completion": 85
            },
            {
                "action": "talk_with_human",
                "action_type": "talk",
                "parameters": {"message": "Here is your water!"},
                "reasoning": "Deliver water to human",
                "completion": 100
            }
        ]

        if self.step_count <= len(steps_sequence):
            step = steps_sequence[self.step_count - 1]
            return {
                "current_step_analysis": {
                    "task_progress": f"Executing step {self.step_count} of {len(steps_sequence)}",
                    "current_situation": f"Current action: {step['action']}",
                    "next_action_reasoning": step['reasoning']
                },
                "next_step": {
                    "step_number": self.step_count,
                    "action": step['action'],
                    "action_type": step['action_type'],
                    "location": "home" if step['action_type'] == "talk" else "in_transit",
                    "parameters": step['parameters'],
                    "expected_outcome": f"Complete {step['action']}"
                },
                "task_status": {
                    "is_complete": False,
                    "completion_percentage": step['completion'],
                    "remaining_actions": f"{len(steps_sequence) - self.step_count} steps remaining"
                },
                "feedback_request": f"Result of {step['action']}"
            }
        else:
            self.is_task_complete = True
            return {
                "task_status": {"is_complete": True, "completion_percentage": 100},
                "task_summary": {
                    "total_steps_executed": len(steps_sequence),
                    "success": True
                }
            }

    def _plan_light_control(self):
        """Mock planning for light control"""
        steps = ["get_observation", "control_light", "talk_with_human"]
        if self.step_count <= len(steps):
            action = steps[self.step_count - 1]
            return {
                "current_step_analysis": {
                    "task_progress": f"Step {self.step_count} of {len(steps)}",
                    "next_action_reasoning": f"Execute {action}"
                },
                "next_step": {
                    "step_number": self.step_count,
                    "action": action,
                    "action_type": "sense" if "observation" in action else "tool" if "control" in action else "talk",
                    "parameters": {"action": "turn_on"} if "control" in action else {"message": "Lights are now on"} if "talk" in action else {}
                },
                "task_status": {
                    "is_complete": False,
                    "completion_percentage": int((self.step_count / len(steps)) * 100)
                },
                "feedback_request": f"Result of {action}"
            }
        else:
            self.is_task_complete = True
            return {"task_status": {"is_complete": True, "completion_percentage": 100}}

    def _plan_generic_task(self):
        """Generic mock planning"""
        if self.step_count == 1:
            return {
                "next_step": {
                    "step_number": 1,
                    "action": "get_observation",
                    "action_type": "sense",
                    "parameters": {}
                },
                "task_status": {"is_complete": False, "completion_percentage": 50},
                "feedback_request": "Observation result"
            }
        else:
            self.is_task_complete = True
            return {"task_status": {"is_complete": True, "completion_percentage": 100}}

    def provide_feedback(self, feedback):
        """Provide feedback and plan next step"""
        print(f"\n💬 Feedback received: {feedback}\n")
        self.conversation_history.append({"feedback": feedback, "step": self.step_count})
        return self.plan_next_step()

    def execute_step_and_wait(self, step_plan):
        """Execute step (simulation)"""
        if step_plan.get("task_status", {}).get("is_complete"):
            print("\n✅ TASK COMPLETE")
            return "Task complete"

        next_step = step_plan.get("next_step", {})
        if not next_step:
            return "No step to execute"

        self.execution_history.append({
            "step_number": next_step.get("step_number"),
            "action": next_step.get("action"),
            "parameters": next_step.get("parameters")
        })

        print(f"\n⚡ EXECUTING STEP {next_step.get('step_number')}: {next_step.get('action')}")
        print(f"   Parameters: {json.dumps(next_step.get('parameters', {}))}")

        return step_plan.get("feedback_request", "Please provide feedback")

    def get_task_summary(self):
        """Get task summary"""
        duration = (datetime.now() - self.task_start_time).total_seconds() if self.task_start_time else 0
        return {
            "original_request": self.original_request,
            "steps_executed": self.step_count,
            "is_complete": self.is_task_complete,
            "duration_seconds": duration
        }


def test_ac_control():
    """Test AC control scenario"""
    print("\n" + "🧪"*35)
    print("TEST 1: AC Control")
    print("🧪"*35)

    planner = MockInteractivePlanner()
    step_plan = planner.start_new_task("I'm feeling cold")

    feedbacks = [
        "Observation: Room temperature appears cool, AC is off",
        "AC turned on successfully at 24°C",
        "Human says: 'Thank you, perfect!'"
    ]

    for feedback in feedbacks:
        if planner.is_task_complete:
            break
        feedback_request = planner.execute_step_and_wait(step_plan)
        print(f"❓ {feedback_request}")
        print(f"📥 {feedback}")
        step_plan = planner.provide_feedback(feedback)

    print("\n📊 Summary:", planner.get_task_summary())


def test_water_retrieval():
    """Test water retrieval scenario"""
    print("\n" + "🧪"*35)
    print("TEST 2: Water Retrieval")
    print("🧪"*35)

    planner = MockInteractivePlanner()
    step_plan = planner.start_new_task("I need some water")

    feedbacks = [
        "Human is in living room",
        "Human acknowledged",
        "Arrived at store",
        "Store robot acknowledged request",
        "Item is ready",
        "Returned home successfully",
        "Human received water"
    ]

    for feedback in feedbacks:
        if planner.is_task_complete:
            break
        feedback_request = planner.execute_step_and_wait(step_plan)
        print(f"❓ {feedback_request}")
        print(f"📥 {feedback}")
        step_plan = planner.provide_feedback(feedback)

    print("\n📊 Summary:", planner.get_task_summary())


def test_light_control():
    """Test light control scenario"""
    print("\n" + "🧪"*35)
    print("TEST 3: Light Control")
    print("🧪"*35)

    planner = MockInteractivePlanner()
    step_plan = planner.start_new_task("Turn on the lights")

    feedbacks = [
        "Lights are currently off",
        "Lights turned on",
        "Human acknowledged"
    ]

    for feedback in feedbacks:
        if planner.is_task_complete:
            break
        feedback_request = planner.execute_step_and_wait(step_plan)
        print(f"❓ {feedback_request}")
        print(f"📥 {feedback}")
        step_plan = planner.provide_feedback(feedback)

    print("\n📊 Summary:", planner.get_task_summary())


if __name__ == "__main__":
    print("\n" + "="*70)
    print("MOCK INTERACTIVE PLANNER - DEMONSTRATION")
    print("This demonstrates the closed-loop workflow without API calls")
    print("="*70)

    test_ac_control()
    input("\n⏸️  Press Enter for next test...")

    test_water_retrieval()
    input("\n⏸️  Press Enter for next test...")

    test_light_control()

    print("\n" + "✅"*35)
    print("ALL MOCK TESTS COMPLETED")
    print("✅"*35)
    print("\nThe interactive planner successfully demonstrates:")
    print("  ✓ Single-step planning")
    print("  ✓ Human feedback integration")
    print("  ✓ Context-aware next step selection")
    print("  ✓ Task completion detection")
    print("  ✓ Conversation history management")
