# humanoid_planner_interactive.py

"""
Interactive Closed-Loop Humanoid Robot Planner
Generates ONE step at a time, waits for human feedback before continuing
"""

import os
import json
import sys
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from humanoid_prompt_template_interactive import (
    get_humanoid_interactive_system_prompt,
    get_humanoid_interactive_test_cases
)
from json_tool.json_parser_enhanced import (
    parse_json_with_fallback,
)


class TaskSession:
    """
    Maintains state for a single task across multiple planning iterations
    """
    def __init__(self, original_request: str):
        self.original_request = original_request
        self.step_history = []
        self.current_step_number = 0
        self.is_complete = False
        self.created_at = datetime.now()

    def add_step(self, step_plan: Dict, execution_result: Optional[str] = None):
        """Add a completed step to history"""
        self.current_step_number += 1
        self.step_history.append({
            "step_number": self.current_step_number,
            "plan": step_plan,
            "execution_result": execution_result,
            "timestamp": datetime.now().isoformat()
        })

    def get_context_summary(self) -> str:
        """Generate a context summary for the LLM"""
        if not self.step_history:
            return "This is the first step. No previous actions have been taken."

        summary = f"Original request: {self.original_request}\n\n"
        summary += f"Steps completed so far ({len(self.step_history)}):\n"

        for i, step in enumerate(self.step_history, 1):
            plan = step['plan']
            result = step['execution_result']
            summary += f"\nStep {i}:\n"
            summary += f"  Action: {plan.get('action', 'unknown')}\n"
            summary += f"  Type: {plan.get('action_type', 'unknown')}\n"
            if plan.get('parameters'):
                summary += f"  Parameters: {plan.get('parameters')}\n"
            if result:
                summary += f"  Result: {result}\n"

        summary += f"\nCurrent state: Ready for step {self.current_step_number + 1}"
        return summary


class HumanoidRobotPlannerInteractive:
    """
    Unitree-G1 Humanoid Robot Planner - Interactive Closed-Loop Version
    Generates ONE step at a time, waits for human feedback before continuing
    """

    def __init__(self, base_url: str = None, model_name: str = None):
        """
        Initialize interactive humanoid robot planner

        Args:
            base_url: DeepSeek API base URL
            model_name: Model name to use
        """
        # API configuration
        self.base_url = base_url or "http://dsv3.sii.edu.cn/v1/chat/completions"
        self.model = model_name or "deepseek-v3-ep"

        # DeepSeek API config parameters
        self.config = {
            "model": self.model,
            "max_tokens": 1500,  # Reduced since we're only generating one step
            "temperature": 0.6,
            "top_p": 0.95,
            "presence_penalty": 1.03,
            "frequency_penalty": 1.0,
            "stream": False
        }

        # Request headers
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        self.system_prompt = get_humanoid_interactive_system_prompt()

        # Active task sessions
        self.active_sessions: Dict[str, TaskSession] = {}

        print(f"✅ Initialized Interactive HumanoidRobotPlanner")
        print(f"   Model: {self.model}")
        print(f"   Mode: Closed-loop (one step at a time)")
        print(f"   API endpoint: {self.base_url}")

    def _make_api_request(self, messages: List[Dict]) -> Dict:
        """Send API request to DeepSeek service"""
        request_data = {
            "model": self.config["model"],
            "messages": messages,
            "max_tokens": self.config["max_tokens"],
            "temperature": self.config["temperature"],
            "top_p": self.config["top_p"],
            "presence_penalty": self.config["presence_penalty"],
            "frequency_penalty": self.config["frequency_penalty"],
            "stream": False
        }

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=request_data,
                timeout=300
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def start_task(self, human_request: str, session_id: str = None, debug: bool = False) -> Dict:
        """
        Start a new task and get the first step

        Args:
            human_request: Human's natural language request
            session_id: Optional session ID (auto-generated if not provided)
            debug: Show debug information

        Returns:
            dict: Next step plan
        """
        # Generate session ID if not provided
        if session_id is None:
            session_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create new task session
        session = TaskSession(human_request)
        self.active_sessions[session_id] = session

        if debug:
            print(f"\n🆕 Starting new task session: {session_id}")
            print(f"   Request: {human_request}")

        # Get first step
        return self.plan_next_step(session_id, debug=debug)

    def plan_next_step(self, session_id: str, debug: bool = False) -> Dict:
        """
        Plan the next single step for an ongoing task

        Args:
            session_id: Task session identifier
            debug: Show debug information

        Returns:
            dict: Next step plan with feedback request
        """
        # Get session
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": f"Session {session_id} not found. Use start_task() first."}

        if session.is_complete:
            return {
                "message": "Task already complete",
                "session_id": session_id,
                "total_steps": len(session.step_history)
            }

        try:
            # Build context-aware prompt
            context = session.get_context_summary()

            user_message = f"""
{context}

Please generate the NEXT SINGLE STEP only.
Remember: Output ONE step, not a complete plan.
"""

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ]

            if debug:
                print(f"\n📤 Requesting next step for session: {session_id}")
                print(f"   Context: {len(session.step_history)} steps completed")

            # Call DeepSeek API
            response = self._make_api_request(messages)

            # Extract response content
            if 'choices' in response and len(response['choices']) > 0:
                response_text = response['choices'][0]['message']['content']
            else:
                raise Exception("Invalid API response format")

            if debug:
                print(f"\n📥 Raw API response:\n{response_text}\n{'='*50}")

            # Parse response
            result, success = parse_json_with_fallback(response_text, debug=debug)

            if success and "next_step" in result:
                # Add session info to result
                result["session_id"] = session_id
                result["step_number"] = session.current_step_number + 1
                return result
            else:
                error_msg = "Failed to parse step plan"
                if success:
                    error_msg += f" - JSON parsed but missing 'next_step' field. Found keys: {list(result.keys())}"
                else:
                    error_msg += " - JSON parsing failed"
                return {"error": error_msg, "raw_response": response_text[:500], "parsed_result": result if success else None}

        except Exception as e:
            return {"error": f"Planning failed: {str(e)}"}

    def execute_step(self, session_id: str, step_plan: Dict,
                     execution_result: str = None, user_feedback: str = "approved") -> Dict:
        """
        Record step execution and result (simulation for now)

        Args:
            session_id: Task session identifier
            step_plan: The step plan that was executed
            execution_result: Result from executing the step (simulated or real)
            user_feedback: User's feedback (approved/modified/cancelled)

        Returns:
            dict: Execution confirmation
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": f"Session {session_id} not found"}

        # Check if task is marked complete
        task_status = step_plan.get('task_status', {})
        if task_status.get('is_complete', False):
            session.is_complete = True

        # Simulate execution result if not provided
        if execution_result is None:
            next_step = step_plan.get('next_step', {})
            action = next_step.get('action', 'unknown')
            execution_result = f"✅ {action} executed successfully (simulated)"

        # Add to history
        session.add_step(step_plan.get('next_step', {}), execution_result)

        return {
            "status": "executed",
            "session_id": session_id,
            "step_number": session.current_step_number,
            "user_feedback": user_feedback,
            "execution_result": execution_result,
            "task_complete": session.is_complete
        }

    def interactive_execution_loop(self, human_request: str, auto_approve: bool = False,
                                   debug: bool = False):
        """
        Run interactive execution loop with human-in-the-loop

        Args:
            human_request: Initial human request
            auto_approve: If True, automatically approve all steps (for testing)
            debug: Show debug information
        """
        print("\n" + "="*70)
        print("🤖 INTERACTIVE HUMANOID ROBOT PLANNER - CLOSED-LOOP MODE")
        print("="*70)
        print(f"📝 Task: {human_request}")
        print(f"🔄 Mode: {'Auto-approve (testing)' if auto_approve else 'Manual approval'}")
        print("="*70)

        # Start task
        session_id = f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        step_plan = self.start_task(human_request, session_id, debug=debug)

        step_count = 0
        max_steps = 20  # Safety limit

        while step_count < max_steps:
            step_count += 1

            # Check for errors
            if "error" in step_plan:
                print(f"\n❌ Error: {step_plan['error']}")
                break

            # Check if task complete
            if step_plan.get('message') == "Task already complete":
                print(f"\n✅ Task completed in {step_plan.get('total_steps', 0)} steps!")
                break

            # Display next step
            self._display_step_plan(step_plan, step_count)

            # Get human feedback
            if not auto_approve:
                user_input = input("\n👤 Your decision [proceed/modify/cancel/quit]: ").strip().lower()

                if user_input in ['quit', 'q', 'cancel', 'c']:
                    print("🛑 Task cancelled by user")
                    break
                elif user_input in ['modify', 'm']:
                    modification = input("   How should I modify this step? ")
                    print(f"   (Modification noted: {modification})")
                    print("   ⚠️  Re-planning with modification not yet implemented")
                    print("   Proceeding with original plan...")

                # Default to proceed
                user_feedback = "approved"
            else:
                user_feedback = "auto-approved"
                print(f"\n🤖 Auto-approving step {step_count}")

            # Simulate execution
            execution_result = self._simulate_execution(step_plan.get('next_step', {}))

            # Record execution
            exec_result = self.execute_step(session_id, step_plan, execution_result, user_feedback)

            print(f"\n{'='*70}")
            print(f"✅ Step {step_count} executed")
            print(f"📊 Result: {execution_result}")

            # Check if complete
            if exec_result.get('task_complete'):
                print(f"\n🎉 TASK COMPLETE! Total steps: {exec_result['step_number']}")
                break

            print(f"{'='*70}")
            print("⏸️  Waiting for next step planning...")

            # Plan next step
            step_plan = self.plan_next_step(session_id, debug=debug)

        if step_count >= max_steps:
            print(f"\n⚠️  Reached maximum step limit ({max_steps})")

        # Show summary
        self._display_session_summary(session_id)

    def _display_step_plan(self, step_plan: Dict, step_count: int):
        """Display a step plan in a formatted way"""
        print(f"\n{'─'*70}")
        print(f"📋 STEP {step_count} PLAN")
        print(f"{'─'*70}")

        # Task understanding
        understanding = step_plan.get('task_understanding', {})
        print(f"🎯 Goal: {understanding.get('current_goal', 'N/A')}")
        print(f"📈 Progress: {understanding.get('progress_summary', 'N/A')}")

        # Next step details
        next_step = step_plan.get('next_step', {})
        print(f"\n🤖 Next Action:")
        print(f"   Type: {next_step.get('action_type', 'N/A')}")
        print(f"   Action: {next_step.get('action', 'N/A')}")
        if next_step.get('parameters'):
            print(f"   Parameters: {next_step.get('parameters')}")
        print(f"   Location: {next_step.get('location', 'N/A')}")
        print(f"   Duration: {next_step.get('estimated_duration', 'N/A')}")

        print(f"\n💭 Rationale: {next_step.get('rationale', 'N/A')}")
        print(f"🎯 Expected Outcome: {next_step.get('expected_outcome', 'N/A')}")

        # Task status
        status = step_plan.get('task_status', {})
        print(f"\n📊 Progress: {status.get('completion_percentage', 0)}%")
        print(f"⏭️  Remaining: {status.get('remaining_steps_estimate', 'Unknown')}")

        # Contingency
        contingency = step_plan.get('contingency_note', '')
        if contingency:
            print(f"\n⚠️  Contingency: {contingency}")

        # Feedback request
        feedback_req = step_plan.get('human_feedback_request', {})
        question = feedback_req.get('question', 'Should I proceed?')
        print(f"\n❓ {question}")

    def _simulate_execution(self, step: Dict) -> str:
        """Simulate step execution (for demo purposes)"""
        action = step.get('action', 'unknown')
        action_type = step.get('action_type', 'unknown')

        simulations = {
            "get_observation": "Current scene: Living room, AC is off, temperature 26°C, user is sitting on sofa",
            "talk_with_human": "Message delivered to human",
            "control_air_conditioner": "AC turned on, set to specified temperature",
            "control_light": "Lights toggled successfully",
            "navigate_to_store": "Arrived at store location",
            "request_item_from_store": "Item request sent to store robot",
            "wait_for_item": "Waited for specified duration, item is ready",
            "return_home_with_item": "Returned home successfully with item"
        }

        return simulations.get(action, f"✅ {action} executed successfully (simulated)")

    def _display_session_summary(self, session_id: str):
        """Display summary of completed session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return

        print(f"\n{'='*70}")
        print("📊 SESSION SUMMARY")
        print(f"{'='*70}")
        print(f"Original Request: {session.original_request}")
        print(f"Total Steps: {len(session.step_history)}")
        print(f"Status: {'✅ Complete' if session.is_complete else '⏸️  Incomplete'}")
        print(f"\nStep History:")

        for i, step in enumerate(session.step_history, 1):
            plan = step['plan']
            print(f"\n  {i}. {plan.get('action', 'unknown')} ({plan.get('action_type', 'unknown')})")
            print(f"     Result: {step['execution_result']}")

        print(f"\n{'='*70}")

    def get_session_info(self, session_id: str) -> Dict:
        """Get information about a task session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": f"Session {session_id} not found"}

        return {
            "session_id": session_id,
            "original_request": session.original_request,
            "steps_completed": len(session.step_history),
            "current_step": session.current_step_number,
            "is_complete": session.is_complete,
            "created_at": session.created_at.isoformat()
        }

    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            print(f"Testing connection to {self.base_url}...")
            response = self._make_api_request([
                {"role": "user", "content": "Hello"}
            ])
            if 'choices' in response:
                print("✅ Connection successful!")
                return True
            else:
                print("❌ Connection failed: Invalid response format")
                return False
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False


def main():
    """Main interactive demo"""
    print("🤖 Interactive Humanoid Robot Planner - Closed-Loop Edition")
    print("="*70)

    try:
        # Initialize planner
        planner = HumanoidRobotPlannerInteractive()

        # Test connection
        if not planner.test_connection():
            print("⚠️  Warning: Could not connect to DeepSeek API")
            return

        print(f"\n📋 Interactive Mode Commands:")
        print("  - Type your task request to start interactive planning")
        print("  - 'demo': Run a demo with auto-approval")
        print("  - 'quit' or 'q': Exit")

        while True:
            user_input = input(f"\n🤖 Interactive Planner > ").strip()

            if user_input.lower() in ['quit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'demo':
                # Run demo with auto-approval
                planner.interactive_execution_loop(
                    "I'm feeling cold, turn on the AC",
                    auto_approve=True,
                    debug=False
                )
            elif user_input:
                # Run interactive mode with human approval
                planner.interactive_execution_loop(
                    user_input,
                    auto_approve=False,
                    debug=False
                )

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
