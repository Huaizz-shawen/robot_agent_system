# Dual Planner System - Humanoid Robot & Robotic Arm

This repository contains a specialized dual-planner system that separates control between a humanoid robot (Unitree-G1) and a robotic arm (UR5e), each with their own dedicated task planner.

## Overview

The system has been refactored from a single multi-agent planner into two specialized planners:

1. **Planner 1: Humanoid Robot Planner** (`HumanoidRobotPlanner`)
   - Controls: Unitree-G1 humanoid robot
   - Environment: Home (Room 01)
   - Capabilities: Environment control (AC, lights), navigation, item retrieval coordination

2. **Planner 2: Robotic Arm Planner** (`RoboticArmPlanner`)
   - Controls: UR5e robotic arm
   - Environment: Store (Room 02)
   - Capabilities: Item picking, inventory management, precise manipulation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Human User                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Natural Language       │
        │     Request             │
        └────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐      ┌──────────────────┐
│ PLANNER 1        │      │ PLANNER 2        │
│ Humanoid Robot   │◄────►│ Robotic Arm      │
│ (Unitree-G1)     │      │ (UR5e)           │
└──────────────────┘      └──────────────────┘
        │                         │
        ▼                         ▼
┌──────────────────┐      ┌──────────────────┐
│ Room 01 - Home   │      │ Room 02 - Store  │
│ - AC Control     │      │ - Item Shelves   │
│ - Light Control  │      │ - Inventory      │
│ - Human Interface│      │ - Service Counter│
└──────────────────┘      └──────────────────┘
```

## File Structure

### Core Files

#### Humanoid Robot Planner
- `humanoid_planner.py` - Main planner class for humanoid robot
- `humanoid_prompt_template.py` - System prompt and configuration for home tasks

#### Robotic Arm Planner
- `arm_planner.py` - Main planner class for robotic arm
- `arm_prompt_template.py` - System prompt and configuration for store tasks

#### Examples and Usage
- `example_dual_planner_usage.py` - Comprehensive examples and demos
- `README_DUAL_PLANNER.md` - This documentation file

#### Legacy Files (Original Multi-Agent System)
- `qwenapi_planner.py` - Original unified planner
- `system_prompt_template.py` - Original system prompt
- `example_usage.py` - Original example usage

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `openai>=1.0.0`
- `python-dotenv`

### 2. Set API Key

Set your DashScope API key:

```bash
export DASHSCOPE_API_KEY='your-api-key-here'
```

Or use the provided script:

```bash
source apikey.bash
```

### 3. Verify Setup

```bash
python humanoid_planner.py  # Test humanoid robot planner
python arm_planner.py        # Test robotic arm planner
```

## Usage

### Quick Start

Run the comprehensive demo:

```bash
python example_dual_planner_usage.py
```

This provides 6 different modes:
1. **Humanoid Robot Only** - Home environment control demos
2. **Robotic Arm Only** - Store inventory management demos
3. **Coordinated Task** - Simple cross-room task
4. **Complex Scenario** - Environment setup + item retrieval
5. **Run All Tests** - Execute test suites for both planners
6. **Interactive Mode** - Manual control of both planners

### Using Individual Planners

#### Humanoid Robot Planner

```python
from humanoid_planner import HumanoidRobotPlanner

# Initialize
humanoid = HumanoidRobotPlanner()

# Plan a task
plan = humanoid.plan_task("Turn on the AC to 24 degrees")

# Execute (simulation)
humanoid.execute_plan(plan)
```

**Example Tasks:**
- "I'm feeling cold, turn on the AC"
- "Make the room comfortable for reading"
- "Get me some water from the store"
- "Turn off the lights"

#### Robotic Arm Planner

```python
from arm_planner import RoboticArmPlanner

# Initialize
arm = RoboticArmPlanner()

# Plan a task
plan = arm.plan_task("Get water and snacks for pickup")

# Execute (simulation)
arm.execute_plan(plan)
```

**Example Tasks:**
- "Get water for the customer"
- "Prepare snacks and fruit for pickup"
- "Check if medicine is available"
- "Organize Shelf A"

### Coordinated Tasks

For tasks requiring both robots:

```python
from humanoid_planner import HumanoidRobotPlanner
from arm_planner import RoboticArmPlanner

# Initialize both planners
humanoid = HumanoidRobotPlanner()
arm = RoboticArmPlanner()

# Human makes a request
human_request = "I need water from the store"

# Step 1: Humanoid plans navigation and retrieval
humanoid_plan = humanoid.plan_task(human_request)
humanoid.execute_plan(humanoid_plan)

# Step 2: Arm prepares the item
arm_request = "Get water for pickup"
arm_plan = arm.plan_task(arm_request)
arm.execute_plan(arm_plan)

# Step 3: Coordination complete!
print("✅ Task completed!")
```

## Planner Capabilities

### Humanoid Robot (Unitree-G1)

**Location:** Home (Room 01)

**Available Actions:**
- `talk_with_human(message)` - Communicate with user
- `control_air_conditioner(action, temperature)` - Control AC
  - Actions: "turn_on", "turn_off"
  - Temperature: 16-30°C
- `control_light(action, brightness)` - Control lights
  - Actions: "turn_on", "turn_off"
  - Brightness: 0-100%
- `navigate_to_store()` - Move to store
- `return_home_with_item(item)` - Return with item
- `wait_for_item(estimated_time)` - Wait for item preparation

**Specializations:**
- Home environment control
- Human interaction
- Cross-room navigation
- Item transportation

### Robotic Arm (UR5e)

**Location:** Store (Room 02)

**Available Actions:**
- `communicate_with_humanoid(message)` - Inter-robot communication
- `pick_from_shelf(item_name, shelf_location)` - Retrieve items
  - Available items: snacks, water, fruit, medicine
- `place_on_counter(item_name)` - Place item for pickup
- `verify_item_availability(item_name)` - Check stock
- `update_inventory(item_name, action)` - Update inventory
  - Actions: "decrement", "increment"
- `organize_shelf(shelf_location)` - Organize items

**Specializations:**
- Precise manipulation
- Inventory management
- Multi-item coordination
- Stock tracking

## Inventory Database

**Shelf A:**
- Level 1: water (stock: 10)
- Level 2: snacks (stock: 15)

**Shelf B:**
- Level 1: (empty)
- Level 2: fruit (stock: 8)

**Shelf C:**
- Level 1: medicine (stock: 5)
- Level 2: (empty)

## Running Tests

### Test Individual Planners

```python
# Test humanoid robot
humanoid = HumanoidRobotPlanner()
humanoid.run_tests()

# Test robotic arm
arm = RoboticArmPlanner()
arm.run_tests()
```

### Test Cases Included

**Humanoid Robot Tests:**
1. Simple AC control
2. Light control
3. Item retrieval from store
4. Environment setup for reading
5. Multiple items retrieval

**Robotic Arm Tests:**
1. Single item retrieval
2. Multiple items
3. Inventory check
4. Complex order preparation
5. Shelf organization + item prep

## Configuration

### Model Selection

Both planners support multiple Qwen models:

```python
# Available models
models = [
    "qwen-turbo",           # Fast, simple tasks
    "qwen-plus",            # Balanced (default)
    "qwen-max",             # Most powerful
    "qwen2.5-72b-instruct", # Open source
    "qwen2.5-32b-instruct", # Medium open source
    "qwen2.5-14b-instruct"  # Lightweight open source
]

# Switch models
planner = HumanoidRobotPlanner(model_name="qwen-max")
# or
planner.switch_model("qwen-turbo")
```

### Debug Mode

Enable debug output to see raw API responses:

```python
plan = planner.plan_task(request, debug=True)
```

### Streaming Mode

Use streaming for real-time response:

```python
plan = planner.plan_task(request, stream=True)
```

## Output Format

Both planners return structured JSON plans:

```json
{
  "task_analysis": {
    "intent": "home_environment_control",
    "entities": ["air_conditioner", "temperature"],
    "complexity": "simple",
    "estimated_duration": "1 minute"
  },
  "execution_plan": [
    {
      "step": 1,
      "agent": "Unitree-G1 humanoid_robot",
      "location": "home",
      "action": "control_air_conditioner",
      "parameters": {"action": "turn_on", "temperature": 24},
      "dependencies": [],
      "success_criteria": "AC is running at 24°C"
    }
  ],
  "contingency_plans": [
    {
      "failure_scenario": "AC does not respond",
      "alternative_action": "Report error to human"
    }
  ],
  "human_feedback": "I'll turn on the AC to 24°C for you"
}
```

## Interactive Mode Commands

When running `example_dual_planner_usage.py` in interactive mode:

```
h <request>  - Send request to Humanoid Robot
a <request>  - Send request to Robotic Arm
c <request>  - Coordinated task (both planners)
test         - Run all test cases
quit / q     - Exit
```

**Examples:**
```
> h Turn on the AC to 25 degrees
> a Get water and snacks
> c I need fruit and a comfortable environment
> test
> q
```

## Advantages of Dual Planner Design

1. **Specialization**: Each planner is optimized for its specific robot and environment
2. **Clarity**: Clearer separation of concerns and responsibilities
3. **Scalability**: Easier to add new capabilities to individual robots
4. **Maintainability**: Simpler to update and debug individual planners
5. **Testing**: Can test each planner independently
6. **Performance**: More focused prompts lead to better LLM responses

## Comparison with Original System

| Aspect | Original (Multi-Agent) | New (Dual Planner) |
|--------|------------------------|-------------------|
| Planners | 1 unified planner | 2 specialized planners |
| System Prompts | 1 shared prompt | 2 focused prompts |
| Complexity | Higher (handles both) | Lower (focused) |
| Testing | Combined tests | Separate test suites |
| Coordination | Implicit | Explicit |
| Extensibility | Harder to extend | Easier to extend |

## Troubleshooting

### API Key Issues

```
Error: API key not found
```

**Solution:** Set the `DASHSCOPE_API_KEY` environment variable:
```bash
export DASHSCOPE_API_KEY='your-key-here'
```

### Import Errors

```
ModuleNotFoundError: No module named 'openai'
```

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### JSON Parsing Errors

If you see JSON parsing warnings, the system will automatically attempt to clean and extract JSON from markdown-wrapped responses.

### Model Not Found

```
Error: Model 'xyz' not found
```

**Solution:** Use one of the supported models. List available models:
```python
from humanoid_prompt_template import list_available_models
list_available_models()
```

## Contributing

To add new capabilities:

1. **For Humanoid Robot:**
   - Add action to `humanoid_prompt_template.py`
   - Update test cases if needed

2. **For Robotic Arm:**
   - Add action to `arm_prompt_template.py`
   - Update inventory or shelf configuration
   - Update test cases if needed

## License

This project uses the Qwen LLM via Alibaba's DashScope API. Please refer to Alibaba's terms of service for API usage.

## Support

For issues or questions:
1. Check this README
2. Review example files
3. Test with debug mode enabled
4. Verify API key and model configuration
