# humanoid_planner_interactive.py

"""
Interactive Humanoid Robot Planner
Implements closed-loop, single-step planning with human feedback
"""

import os
import json
from datetime import datetime
from openai import OpenAI
from humanoid_prompt_template_interactive import (
    get_humanoid_interactive_system_prompt,
    get_humanoid_interactive_qwen_config,
    validate_interactive_response,
    clean_json_response,
    list_available_models
)
from humanoid_executor import HumanoidExecutor


class InteractiveHumanoidPlanner:
    """
    Interactive Unitree-G1 Humanoid Robot Planner

    This planner operates in closed-loop mode:
    1. Plan ONE step based on current context + history
    2. Execute that step
    3. Wait for human feedback/observation
    4. Update context with feedback
    5. Repeat until task complete
    """

    def __init__(self, api_key=None, model_name=None, simulation_mode=True, verbose=True):
        """
        Initialize interactive humanoid planner

        Args:
            api_key: DASHSCOPE API key
            model_name: Qwen model name to use
            simulation_mode: If True, simulate execution; if False, use real hardware
            verbose: Print detailed execution logs
        """
        # Get API key
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not found. Please provide api_key parameter or set DASHSCOPE_API_KEY environment variable."
            )

        # Get configuration
        self.config = get_humanoid_interactive_qwen_config(model_name)

        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.config["base_url"]
        )

        self.system_prompt = get_humanoid_interactive_system_prompt()

        # Initialize executor
        self.executor = HumanoidExecutor(simulation_mode=simulation_mode, verbose=verbose)

        # Conversation state
        self.reset_conversation()

        print(f"✅ Initialized InteractiveHumanoidPlanner with model: {self.config['model']}")

    def reset_conversation(self):
        """Reset conversation state for a new task"""
        self.original_request = None
        self.conversation_history = []  # List of dicts with 'role' and 'content'
        self.execution_history = []  # List of executed steps
        self.step_count = 0
        self.is_task_complete = False
        self.task_start_time = None

    def start_new_task(self, human_request):
        """
        Start a new task from human request

        Args:
            human_request: Natural language request from human

        Returns:
            dict: First step to execute
        """
        self.reset_conversation()
        self.original_request = human_request
        self.task_start_time = datetime.now()

        print("\n" + "="*70)
        print("🤖 NEW TASK STARTED")
        print("="*70)
        print(f"📝 Request: {human_request}")
        print(f"🕐 Started at: {self.task_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")

        # Get first step
        return self.plan_next_step()

    def plan_next_step(self):
        """
        Plan the next single step based on current context and history

        Returns:
            dict: Next step plan with metadata
        """
        if self.is_task_complete:
            print("⚠️ Task is already complete. No next step to plan.")
            return None

        # Build context message for LLM
        context_message = self._build_context_message()

        # Prepare messages for API call
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context_message}
        ]

        # Add conversation history (previous planning rounds)
        for hist_msg in self.conversation_history:
            messages.append(hist_msg)

        # Call LLM API
        try:
            request_params = {
                "model": self.config["model"],
                "messages": messages,
                "max_tokens": self.config["max_tokens"],
                "temperature": self.config["temperature"]
            }

            if "extra_body" in self.config:
                request_params["extra_body"] = self.config["extra_body"]

            response = self.client.chat.completions.create(**request_params)
            response_text = response.choices[0].message.content

            # Parse response
            step_plan = self._parse_step_plan(response_text)

            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })

            # Check if task is complete (next_step is null)
            if step_plan.get("next_step") is None:
                self.is_task_complete = True
                print("\n" + "="*70)
                print("✅ TASK COMPLETE")
                print("="*70)
                if "task_summary" in step_plan:
                    summary = step_plan["task_summary"]
                    print(f"📊 Total steps: {summary.get('total_steps_executed', 'N/A')}")
                    print(f"🎯 Success: {summary.get('success', 'N/A')}")
                    print(f"📝 Final state: {summary.get('final_state', 'N/A')}")
                print("="*70 + "\n")
                return step_plan

            # Display step plan
            self._display_step_plan(step_plan)

            return step_plan

        except Exception as e:
            error_msg = f"Failed to plan next step: {str(e)}"
            print(f"❌ Error: {error_msg}")
            return {"error": error_msg}

    def provide_feedback(self, feedback):
        """
        Provide feedback/observation after executing a step

        Args:
            feedback: Human observation or feedback about the executed step

        Returns:
            dict: Next step plan, or None if task is complete
        """
        if self.is_task_complete:
            print("ℹ️ Task is complete. Feedback noted but no further steps needed.")
            return None

        print(f"\n💬 Feedback received: {feedback}\n")

        # Add feedback to conversation history
        feedback_message = f"[FEEDBACK/OBSERVATION]: {feedback}"
        self.conversation_history.append({
            "role": "user",
            "content": feedback_message
        })

        # Plan next step with updated context
        return self.plan_next_step()

    def execute_step_and_wait(self, step_plan):
        """
        Execute a step using the executor and wait for feedback

        Args:
            step_plan: The step plan from plan_next_step()

        Returns:
            str: Feedback from execution (auto-generated from executor result)
        """
        if "error" in step_plan:
            return "Error in plan. Please check the error message."

        if step_plan.get("next_step") is None:
            return "Task is complete. No execution needed."

        next_step = step_plan.get("next_step")
        if not next_step:
            return "No next step to execute."

        # Record in execution history
        self.execution_history.append({
            "step_number": next_step.get("step_number"),
            "action": next_step.get("action"),
            "parameters": next_step.get("parameters"),
            "timestamp": datetime.now().isoformat()
        })

        self.step_count += 1

        # Display execution header
        print("\n" + "="*70)
        print(f"⚡ EXECUTING STEP {next_step.get('step_number')}...")
        print(f"🎯 Action: {next_step.get('action')}")
        print(f"📦 Parameters: {json.dumps(next_step.get('parameters', {}), indent=2)}")
        print("="*70 + "\n")

        # Execute action using executor
        action_type = next_step.get("action_type")
        action_name = next_step.get("action")
        parameters = next_step.get("parameters", {})

        execution_result = self.executor.execute_action(action_type, action_name, parameters)

        # Add execution result to history
        self.execution_history[-1]["execution_result"] = execution_result.to_dict()

        # Return execution feedback
        feedback = execution_result.get_feedback_message()

        print(f"\n{'='*70}")
        print(f"📊 EXECUTION RESULT:")
        print(f"{'='*70}")
        print(f"Status: {'✅ SUCCESS' if execution_result.success else '❌ FAILED'}")
        print(f"Feedback: {feedback}")
        print(f"{'='*70}\n")

        return feedback

    def get_task_summary(self):
        """Get summary of current task state"""
        duration = None
        if self.task_start_time:
            duration = (datetime.now() - self.task_start_time).total_seconds()

        return {
            "original_request": self.original_request,
            "steps_executed": self.step_count,
            "is_complete": self.is_task_complete,
            "duration_seconds": duration,
            "execution_history": self.execution_history
        }

    def _build_context_message(self):
        """Build context message for LLM based on current state"""
        context_parts = []

        # Original request
        context_parts.append(f"[ORIGINAL REQUEST]: {self.original_request}")

        # Execution history summary
        if self.execution_history:
            context_parts.append(f"\n[STEPS EXECUTED SO FAR]: {len(self.execution_history)}")
            for exec_step in self.execution_history[-3:]:  # Last 3 steps for context
                context_parts.append(
                    f"  - Step {exec_step['step_number']}: {exec_step['action']} "
                    f"with {exec_step['parameters']}"
                )
        else:
            context_parts.append("\n[STEPS EXECUTED SO FAR]: None (this is the first step)")

        # Current status
        context_parts.append(f"\n[CURRENT STATUS]: Planning next step (step #{self.step_count + 1})")

        # Instruction
        context_parts.append(
            "\n[INSTRUCTION]: Based on the above context and any feedback in the conversation history, "
            "plan the NEXT SINGLE STEP to execute. Return your response in the specified JSON format."
        )

        return "\n".join(context_parts)

    def _parse_step_plan(self, response_text):
        """Parse LLM response into step plan"""
        cleaned_text = clean_json_response(response_text)

        is_valid, message = validate_interactive_response(response_text)
        if not is_valid:
            print(f"⚠️ Warning: {message}")

        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {str(e)}")
            return {
                "error": f"JSON parsing failed: {str(e)}",
                "raw_response": response_text[:500]
            }

    def _display_step_plan(self, step_plan):
        """Display step plan in a readable format"""
        print("\n" + "="*70)
        print("NEXT STEP PLAN")
        print("="*70 + "\n")

        # Analysis
        analysis = step_plan.get("current_step_analysis", {})
        print(f"\n🔍 ANALYSIS:")
        print(f"  Progress: {analysis.get('task_progress', 'N/A')}")
        print(f"  Situation: {analysis.get('current_situation', 'N/A')}")
        print(f"  Reasoning: {analysis.get('next_action_reasoning', 'N/A')}")

        # Next step details
        next_step = step_plan.get("next_step", {})
        if next_step:
            print(f"\n⚡ NEXT STEP #{next_step.get('step_number', '?')}:")
            print(f"  Action: {next_step.get('action', 'N/A')}")
            print(f"  Type: {next_step.get('action_type', 'N/A')}")
            print(f"  Location: {next_step.get('location', 'N/A')}")
            print(f"  Parameters: {json.dumps(next_step.get('parameters', {}), indent=4)}")
            print(f"  Expected Outcome: {next_step.get('expected_outcome', 'N/A')}")

        # Feedback request
        print(f"\n💬 FEEDBACK REQUEST:")
        print(f"  {step_plan.get('feedback_request', 'N/A')}")

        # Contingency
        contingency = step_plan.get("contingency", {})
        if contingency:
            print(f"\n🚨 CONTINGENCY PLAN:")
            print(f"  If fails: {contingency.get('if_step_fails', 'N/A')}")
            print(f"  Alternative: {contingency.get('alternative_approach', 'N/A')}")

        print("="*70 + "\n")

    def switch_model(self, model_name):
        """Switch to a different model"""
        old_model = self.config['model']
        self.config = get_humanoid_interactive_qwen_config(model_name)
        print(f"🔄 Switched model from {old_model} to {self.config['model']}")

    def switch_execution_mode(self, simulation_mode):
        """Switch between simulation and real hardware mode"""
        self.executor.switch_mode(simulation_mode)

    def get_execution_statistics(self):
        """Get executor statistics"""
        return self.executor.get_statistics()


def main():
    """Main function for interactive testing"""
    print("🤖 Interactive Humanoid Robot (Unitree-G1) Task Planner")
    print("="*70)

    # Check API key
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("⚠️  Warning: DASHSCOPE_API_KEY environment variable not set.")
        print("Please set it using: export DASHSCOPE_API_KEY='your-api-key'")
        return

    try:
        # Initialize planner
        planner = InteractiveHumanoidPlanner()

        print(f"\n📋 INTERACTIVE MODE - Commands:")
        print("  - Start a task: Type your request in natural language")
        print("  - 'models' or 'm': List available models")
        print("  - 'switch <model>': Switch to different model")
        print("  - 'mode sim': Switch to simulation mode")
        print("  - 'mode real': Switch to real hardware mode")
        print("  - 'stats': Show execution statistics")
        print("  - 'status' or 's': Show current task status")
        print("  - 'reset' or 'r': Reset and start new task")
        print("  - 'quit' or 'q': Exit")
        print("="*70)
        print(f"🎮 Execution Mode: {'SIMULATION' if planner.executor.simulation_mode else 'REAL HARDWARE'}")
        print("="*70)

        current_step_plan = None

        while True:
            # Determine prompt
            if current_step_plan is None:
                prompt = f"\n🤖 [{planner.config['model']}] Enter task request > "
            elif planner.is_task_complete:
                prompt = f"\n🤖 [{planner.config['model']}] Task complete. Enter new task or command > "
                current_step_plan = None
            else:
                prompt = f"\n💬 Provide feedback for step {planner.step_count} > "

            user_input = input(prompt).strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ['quit', 'q']:
                print("👋 Goodbye!")
                break

            elif user_input.lower() in ['models', 'm']:
                list_available_models()
                continue

            elif user_input.lower().startswith('switch '):
                model_name = user_input[7:].strip()
                planner.switch_model(model_name)
                continue

            elif user_input.lower() == 'mode sim':
                planner.switch_execution_mode(simulation_mode=True)
                continue

            elif user_input.lower() == 'mode real':
                planner.switch_execution_mode(simulation_mode=False)
                continue

            elif user_input.lower() == 'stats':
                stats = planner.get_execution_statistics()
                print("\n📊 EXECUTION STATISTICS:")
                print(json.dumps(stats, indent=2))
                continue

            elif user_input.lower() in ['status', 's']:
                summary = planner.get_task_summary()
                print("\n📊 TASK STATUS:")
                print(json.dumps(summary, indent=2))
                continue

            elif user_input.lower() in ['reset', 'r']:
                planner.reset_conversation()
                current_step_plan = None
                print("🔄 Conversation reset. Ready for new task.")
                continue

            # Handle task flow
            if current_step_plan is None or planner.is_task_complete:
                # Start new task
                current_step_plan = planner.start_new_task(user_input)

                # Execute steps automatically until task complete
                while current_step_plan and "error" not in current_step_plan and not planner.is_task_complete:
                    # Execute step and get automatic feedback
                    execution_feedback = planner.execute_step_and_wait(current_step_plan)

                    # Automatically provide feedback to planner for next step
                    current_step_plan = planner.provide_feedback(execution_feedback)

                if planner.is_task_complete:
                    current_step_plan = None
            else:
                # User provided manual feedback/override
                current_step_plan = planner.provide_feedback(user_input)

                # Continue automatic execution
                while current_step_plan and "error" not in current_step_plan and not planner.is_task_complete:
                    # Execute step and get automatic feedback
                    execution_feedback = planner.execute_step_and_wait(current_step_plan)

                    # Automatically provide feedback to planner for next step
                    current_step_plan = planner.provide_feedback(execution_feedback)

                if planner.is_task_complete:
                    current_step_plan = None

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
