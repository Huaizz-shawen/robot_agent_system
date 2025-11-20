# Quick Start Guide: Interactive Closed-Loop Planner

## What's New?

The original planner generated **ALL steps at once** (open-loop).

The new interactive planner generates **ONE step at a time** and waits for your approval (closed-loop).

## 5-Minute Quick Start

### 1. Run the Interactive Demo

```bash
cd /media/user/B29202FA9202C2B91/robot_agent_system/deepseek_planner
python humanoid_planner_interactive.py
```

**Try these commands:**
```
🤖 Interactive Planner > demo
# Runs auto-approval demo - watch it plan step-by-step

🤖 Interactive Planner > I'm feeling cold
# Manual mode - you approve each step

🤖 Interactive Planner > quit
```

### 2. See Usage Examples

```bash
python interactive_planner_usage.py
```

**Select:**
- Option 5 - See the comparison between old and new approach
- Option 2 - Run an auto-approval demo
- Option 1 - Try manual step-by-step control

### 3. Use in Your Code

```python
from humanoid_planner_interactive import HumanoidRobotPlannerInteractive

# Initialize
planner = HumanoidRobotPlannerInteractive()

# Start a task
session_id = "task_001"
step_plan = planner.start_task("Turn on the AC", session_id)

# See what it wants to do
print(f"Next action: {step_plan['next_step']['action']}")
print(f"Rationale: {step_plan['next_step']['rationale']}")

# Approve and execute
result = planner.execute_step(
    session_id,
    step_plan,
    execution_result="AC turned on successfully"
)

# Get next step
next_step = planner.plan_next_step(session_id)
print(f"Next action: {next_step['next_step']['action']}")
```

## Visual Comparison

### OLD (Open-Loop):
```
You: "I need water"
  ↓
Robot: [Plans all 10 steps immediately]
  Step 1: observe
  Step 2: talk
  Step 3: navigate
  ...
  Step 10: deliver
  ↓
[Executes all automatically]
  ↓
Done
```

### NEW (Closed-Loop):
```
You: "I need water"
  ↓
Robot: "Step 1: I want to observe the room"
  ↓
You: "OK, proceed"
  ↓
Robot: [Executes Step 1] "I see you on the sofa"
  ↓
Robot: "Step 2: I'll tell you I'm getting water"
  ↓
You: "OK, proceed"
  ↓
Robot: [Executes Step 2] "I told you my plan"
  ↓
Robot: "Step 3: I'll navigate to the store"
  ↓
You: "Wait! I found water here!"
  ↓
Robot: "Step 4: Great! No need to go to store"
  ↓
Done (adapted based on your feedback!)
```

## Key Features

### 1. Step-by-Step Planning
- Robot plans ONE step
- Explains WHY it wants to do it
- Waits for your approval
- Executes
- Plans NEXT step based on result

### 2. Human-in-the-Loop
At each step, you can:
- **Proceed** - Execute as planned
- **Modify** - Change the plan
- **Cancel** - Stop the task

### 3. Context-Aware
Robot uses results from previous steps:
```
Step 1: observe() → "AC is already on"
Step 2: tell_human("AC is on")
        [NOT turn_on_AC - would be wrong!]
```

### 4. Adaptive
If something changes mid-task:
```
Step 3: navigate_to_store()
User: "Wait, I found water here!"
Step 4: celebrate("Great!")
        [Skips remaining 6 steps - adapted to new situation]
```

## When to Use Which Planner?

### Use Original (Open-Loop) When:
- ✅ You want full autonomy
- ✅ Task is predictable
- ✅ Speed is critical
- ✅ Don't need oversight

**Example:** Scheduled cleaning task

```python
from humanoid_planner_deepseek import HumanoidRobotPlannerDeepSeek
planner = HumanoidRobotPlannerDeepSeek()
plan = planner.plan_task("Clean the room")
planner.execute_plan(plan)  # Runs autonomously
```

### Use New (Closed-Loop) When:
- ✅ Safety is critical
- ✅ Need human oversight
- ✅ Environment is dynamic
- ✅ Want to supervise each action

**Example:** Assisting a user at home

```python
from humanoid_planner_interactive import HumanoidRobotPlannerInteractive
planner = HumanoidRobotPlannerInteractive()
planner.interactive_execution_loop("Help me relax")  # Step-by-step with approval
```

## File Reference

| File | Purpose |
|------|---------|
| `humanoid_planner_interactive.py` | Main closed-loop planner |
| `humanoid_prompt_template_interactive.py` | LLM prompts for single-step |
| `interactive_planner_usage.py` | Usage examples |
| `README_INTERACTIVE.md` | Full documentation |
| `COMPARISON.md` | Detailed comparison |
| `CHANGES_SUMMARY.md` | Summary of changes |
| `QUICKSTART_INTERACTIVE.md` | This guide |

## Common Use Cases

### Use Case 1: Interactive Home Assistant
```python
planner.interactive_execution_loop(
    "Make the room comfortable",
    auto_approve=False  # Manual approval
)
```

### Use Case 2: Testing/Demo
```python
planner.interactive_execution_loop(
    "Get me some snacks",
    auto_approve=True  # Auto-approve for demo
)
```

### Use Case 3: Programmatic Control
```python
session_id = "my_session"

# Step 1
step = planner.start_task("Turn on lights", session_id)
user_approval = get_user_input(step)
if user_approval:
    planner.execute_step(session_id, step, result)

# Step 2
step = planner.plan_next_step(session_id)
user_approval = get_user_input(step)
if user_approval:
    planner.execute_step(session_id, step, result)

# ... continue
```

### Use Case 4: Multiple Concurrent Tasks
```python
# Start task 1
planner.start_task("Get water", "task_1")

# Start task 2
planner.start_task("Turn on AC", "task_2")

# Work on task 1
step = planner.plan_next_step("task_1")

# Work on task 2
step = planner.plan_next_step("task_2")

# Tasks are independent!
```

## API Cheat Sheet

```python
# Initialize
planner = HumanoidRobotPlannerInteractive()

# Test connection
planner.test_connection()

# Start new task
step = planner.start_task(request, session_id)

# Execute step
result = planner.execute_step(session_id, step, execution_result)

# Plan next step
step = planner.plan_next_step(session_id)

# Get session info
info = planner.get_session_info(session_id)

# Run interactive loop
planner.interactive_execution_loop(request, auto_approve=False)
```

## JSON Response Structure

```json
{
  "next_step": {
    "action": "get_observation",
    "action_type": "sense",
    "rationale": "Check room state first",
    "expected_outcome": "Know current conditions"
  },
  "task_status": {
    "is_complete": false,
    "completion_percentage": 20
  },
  "human_feedback_request": {
    "question": "Should I proceed?",
    "options": ["proceed", "modify", "cancel"]
  }
}
```

## Troubleshooting

### Issue: "Session not found"
**Solution:** Use `start_task()` first, then `plan_next_step()`

```python
# Wrong
planner.plan_next_step("new_session")  # ❌ Session doesn't exist

# Correct
planner.start_task("...", "new_session")  # ✅ Creates session
planner.plan_next_step("new_session")     # ✅ Works now
```

### Issue: "Task already complete"
**Solution:** Start a new task

```python
# Check status first
info = planner.get_session_info(session_id)
if info['is_complete']:
    # Start new task
    planner.start_task("New request", "new_session")
```

### Issue: API connection failed
**Solution:** Check DeepSeek API configuration

```python
# Test connection
if not planner.test_connection():
    print("Check base_url and network")
```

## Next Steps

1. **Read the docs:** `README_INTERACTIVE.md` for full details
2. **See comparison:** `COMPARISON.md` to understand differences
3. **Try examples:** `interactive_planner_usage.py` for working code
4. **Integrate:** Use in your own robot control system

## Summary

The interactive closed-loop planner gives you:
- ✅ **Safety** - Human approval for every action
- ✅ **Transparency** - See reasoning for each step
- ✅ **Adaptability** - Adjusts based on results
- ✅ **Control** - Approve/modify/cancel anytime

Perfect for home assistant robots where safety and user control are critical!

---

**Quick Links:**
- Original planner: `humanoid_planner_deepseek.py`
- New planner: `humanoid_planner_interactive.py`
- Examples: `interactive_planner_usage.py`
- Full docs: `README_INTERACTIVE.md`
