# Interactive Closed-Loop Humanoid Robot Planner

## Overview

This is a **closed-loop interactive planner** for the Unitree-G1 humanoid robot that generates **ONE step at a time** and waits for human feedback/permission before continuing.

### Key Difference from Original Planner

| Aspect | Original (Open-Loop) | New (Closed-Loop) |
|--------|---------------------|-------------------|
| **Planning** | Generates ALL steps upfront | Generates ONE step at a time |
| **Human Interaction** | Only at start and end | After EVERY step |
| **Adaptability** | Fixed plan, hard to modify | Adapts based on execution results |
| **Feedback Loop** | Open-loop (no intermediate feedback) | Closed-loop (continuous feedback) |
| **Use Case** | Autonomous execution | Human-supervised execution |

## Architecture

### Files Created

```
deepseek_planner/
├── humanoid_prompt_template_interactive.py    # New prompt for single-step planning
├── humanoid_planner_interactive.py            # Interactive planner class
├── interactive_planner_usage.py               # Usage examples
└── README_INTERACTIVE.md                       # This file
```

### Key Components

#### 1. **TaskSession Class**
Maintains state for a single task across multiple planning iterations:
- Original request
- Step history with execution results
- Current step number
- Completion status

```python
session = TaskSession("I need some water")
session.add_step(step_plan, execution_result)
context = session.get_context_summary()  # For LLM
```

#### 2. **HumanoidRobotPlannerInteractive Class**
Main planner that generates one step at a time:

```python
planner = HumanoidRobotPlannerInteractive()

# Start new task
step_plan = planner.start_task("Turn on the AC", session_id)

# Execute step
result = planner.execute_step(session_id, step_plan, execution_result)

# Get next step
next_step = planner.plan_next_step(session_id)
```

#### 3. **Interactive Execution Loop**
Automated loop with human-in-the-loop:

```python
planner.interactive_execution_loop(
    human_request="I'm cold",
    auto_approve=False,  # Manual approval required
    debug=False
)
```

## How It Works

### Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                      CLOSED-LOOP CYCLE                       │
└─────────────────────────────────────────────────────────────┘

1. User submits request: "I need water"
                ↓
2. Planner generates ONLY Step 1:
   {
     "next_step": {
       "action": "talk_with_human",
       "rationale": "Inform user I'll get water",
       ...
     },
     "human_feedback_request": {
       "question": "Should I proceed?",
       "options": ["proceed", "modify", "cancel"]
     }
   }
                ↓
3. ⏸️  WAIT for human approval
   Human choices:
   - "proceed" → Execute step
   - "modify" → Adjust plan
   - "cancel" → Abort task
                ↓
4. Execute Step 1
   Result: "Message delivered to human"
                ↓
5. Update session history with result
                ↓
6. Planner generates Step 2 (using Step 1 result):
   {
     "next_step": {
       "action": "navigate_to_store",
       "rationale": "User approved, now going to store",
       ...
     },
     "task_understanding": {
       "progress_summary": "Informed user, ready to navigate"
     }
   }
                ↓
7. ⏸️  WAIT for human approval
                ↓
8. Execute Step 2...
                ↓
9. Repeat until task complete
```

### JSON Response Format

The new planner outputs a different JSON structure focused on a single step:

```json
{
  "task_understanding": {
    "original_request": "I need water",
    "current_goal": "Get water from store for user",
    "progress_summary": "Starting task, no steps completed yet"
  },
  "next_step": {
    "step_number": 1,
    "agent": "Unitree-G1 humanoid_robot",
    "location": "home",
    "action": "talk_with_human",
    "action_type": "talk",
    "parameters": {
      "message": "I'll get water from the store for you"
    },
    "rationale": "Inform user of my plan before taking action",
    "expected_outcome": "User is aware and can provide feedback",
    "estimated_duration": "1 second"
  },
  "task_status": {
    "is_complete": false,
    "completion_percentage": 10,
    "remaining_steps_estimate": "5-7 more steps needed"
  },
  "human_feedback_request": {
    "question": "Should I proceed to inform you about getting water?",
    "options": ["proceed", "modify", "cancel"],
    "waiting_for": "permission to execute this step"
  },
  "contingency_note": "If user says no, ask for clarification"
}
```

## Usage Examples

### Example 1: Manual Step-by-Step

```python
from humanoid_planner_interactive import HumanoidRobotPlannerInteractive

planner = HumanoidRobotPlannerInteractive()

# Start task
session_id = "my_task"
step_plan = planner.start_task("I'm feeling cold", session_id)

print(f"Next action: {step_plan['next_step']['action']}")
# Output: get_observation

# Wait for human approval...
user_input = input("Approve? (y/n): ")

if user_input == 'y':
    # Execute step
    result = planner.execute_step(
        session_id,
        step_plan,
        execution_result="Temperature is 28°C, AC is off"
    )

    # Get next step
    step_plan = planner.plan_next_step(session_id)
    print(f"Next action: {step_plan['next_step']['action']}")
    # Output: control_air_conditioner (based on observation)
```

### Example 2: Auto-Approval Mode (Testing)

```python
planner = HumanoidRobotPlannerInteractive()

# Run with automatic approval for testing
planner.interactive_execution_loop(
    human_request="Turn on the lights",
    auto_approve=True,  # No manual intervention
    debug=False
)
```

### Example 3: Interactive Mode (Human-in-the-Loop)

```python
planner = HumanoidRobotPlannerInteractive()

# Run with manual approval at each step
planner.interactive_execution_loop(
    human_request="Get me some snacks",
    auto_approve=False,  # Requires human approval
    debug=False
)

# Console output:
# ───────────────────────────────────────────────────────────
# 📋 STEP 1 PLAN
# ───────────────────────────────────────────────────────────
# 🎯 Goal: Get snacks from store for user
# 🤖 Next Action: talk_with_human
# 💭 Rationale: Inform user before leaving
# ❓ Should I proceed with this action?
#
# 👤 Your decision [proceed/modify/cancel/quit]:
```

## Benefits of Closed-Loop Planning

### 1. **Human Oversight**
- Human can approve/reject each step
- Prevents autonomous errors from cascading
- Safety critical for physical robots

### 2. **Adaptive Planning**
- Planner uses actual execution results
- Can adjust if environment changes
- Handles unexpected outcomes gracefully

### 3. **Transparency**
- User sees reasoning for each step
- Progress tracking at granular level
- Clear understanding of robot's intent

### 4. **Flexibility**
- User can modify plan mid-execution
- Easy to cancel without disrupting full plan
- Supports dynamic user preferences

### 5. **Better Context Awareness**
```python
# Example: Planner adapts based on previous results

# Step 1: get_observation()
# Result: "AC is already on at 24°C"

# Step 2: Planner sees AC is already on
# Action: talk_with_human("AC is already on at 24°C")
# Instead of: control_air_conditioner (would be redundant)
```

## Comparison with Original Planner

### Original `humanoid_planner_deepseek.py`

```python
# Old approach
planner = HumanoidRobotPlannerDeepSeek()
plan = planner.plan_task("Get me water")

# Output: Complete plan with ALL steps
{
  "execution_plan": [
    {"step": 1, "action": "talk_with_human", ...},
    {"step": 2, "action": "get_observation", ...},
    {"step": 3, "action": "navigate_to_store", ...},
    {"step": 4, "action": "request_item_from_store", ...},
    # ... all 10 steps generated upfront
  ]
}

# Execute all steps without intermediate feedback
planner.execute_plan(plan)
```

### New `humanoid_planner_interactive.py`

```python
# New approach
planner = HumanoidRobotPlannerInteractive()

# Generate ONE step
step = planner.start_task("Get me water", "session_1")

# Output: Only next step
{
  "next_step": {
    "step_number": 1,
    "action": "talk_with_human",
    ...
  },
  "human_feedback_request": {...}
}

# Execute with human approval
result = planner.execute_step("session_1", step, execution_result)

# Generate step 2 (based on step 1 result)
step = planner.plan_next_step("session_1")

# Continue with human-in-the-loop
```

## Running the Examples

### Quick Start

```bash
# Run interactive planner
python humanoid_planner_interactive.py

# Commands:
# - Type your request: "I need water"
# - 'demo': Run auto-approval demo
# - 'quit': Exit
```

### Usage Examples

```bash
# Run usage examples
python interactive_planner_usage.py

# Options:
# 1. Manual step-by-step execution
# 2. Auto-approval mode (demo)
# 3. Advanced session management
# 4. User modification workflow
# 5. Comparison: Open-loop vs Closed-loop
# 6. Run all examples
```

## Configuration

The interactive planner uses the same DeepSeek API configuration:

```python
planner = HumanoidRobotPlannerInteractive(
    base_url="http://dsv3.sii.edu.cn/v1/chat/completions",
    model_name="deepseek-v3-ep"
)

# Adjust parameters
planner.config["temperature"] = 0.5  # Balance creativity/precision
planner.config["max_tokens"] = 1500  # Reduced for single-step
```

## API Methods

### Core Methods

| Method | Description |
|--------|-------------|
| `start_task(request, session_id)` | Start new task, get first step |
| `plan_next_step(session_id)` | Generate next step based on history |
| `execute_step(session_id, step_plan, result)` | Record step execution |
| `interactive_execution_loop(request, auto_approve)` | Full interactive loop |
| `get_session_info(session_id)` | Get session status |
| `test_connection()` | Test API connectivity |

### Session Management

```python
# Start multiple tasks
planner.start_task("Get water", "task_1")
planner.start_task("Turn on AC", "task_2")

# Get info
info = planner.get_session_info("task_1")
print(info["steps_completed"])  # 3

# Sessions are independent
planner.plan_next_step("task_1")  # Step 4 for task 1
planner.plan_next_step("task_2")  # Step 1 for task 2
```

## Testing

The system includes simulation for step execution:

```python
def _simulate_execution(self, step: Dict) -> str:
    """Simulate step execution (for demo purposes)"""
    action = step.get('action')

    simulations = {
        "get_observation": "Living room, AC off, temp 26°C",
        "control_air_conditioner": "AC turned on at 24°C",
        "navigate_to_store": "Arrived at store",
        # ... etc
    }

    return simulations.get(action, f"{action} executed")
```

Replace with actual robot execution in production.

## Future Enhancements

1. **Re-planning**: Implement plan modification based on user feedback
2. **Async Support**: Add async version for concurrent sessions
3. **Real Execution**: Replace simulation with actual robot control
4. **Observation Integration**: Connect to real VLM for scene understanding
5. **Voice Interface**: Add speech input/output for natural interaction
6. **Multi-modal Feedback**: Support gesture/touch feedback from user

## Summary

This closed-loop interactive planner transforms the robot from an **autonomous agent** into a **collaborative assistant** that:

- ✅ Plans one step at a time
- ✅ Waits for human permission before each action
- ✅ Adapts based on execution results
- ✅ Provides transparency into decision-making
- ✅ Allows human intervention at any point

Perfect for scenarios where **safety**, **oversight**, and **adaptability** are critical.
