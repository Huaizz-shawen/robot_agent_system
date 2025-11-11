# Migration Guide: From Multi-Agent to Dual Planner System

This guide helps you migrate from the original multi-agent planner to the new dual planner system.

## What Changed?

### Before (Original System)
```python
from qwenapi_planner import QwenMultiAgentPlanner

# Single planner for both robots
planner = QwenMultiAgentPlanner()
plan = planner.plan_task("Turn on AC and get water")
planner.execute_plan(plan)
```

### After (Dual Planner System)
```python
from humanoid_planner import HumanoidRobotPlanner
from arm_planner import RoboticArmPlanner

# Separate planners for each robot
humanoid = HumanoidRobotPlanner()
arm = RoboticArmPlanner()

# Handle tasks separately
h_plan = humanoid.plan_task("Turn on AC")
humanoid.execute_plan(h_plan)

a_plan = arm.plan_task("Get water")
arm.execute_plan(a_plan)
```

## File Mapping

| Original Files | New Files | Purpose |
|---------------|-----------|---------|
| `qwenapi_planner.py` | `humanoid_planner.py` | Humanoid robot control |
|  | `arm_planner.py` | Robotic arm control |
| `system_prompt_template.py` | `humanoid_prompt_template.py` | Humanoid-specific prompts |
|  | `arm_prompt_template.py` | Arm-specific prompts |
| `example_usage.py` | `example_dual_planner_usage.py` | Comprehensive examples |

## Migration Steps

### Step 1: Update Imports

**Old Code:**
```python
from qwenapi_planner import QwenMultiAgentPlanner
from system_prompt_template import SYSTEM_PROMPT
```

**New Code:**
```python
from humanoid_planner import HumanoidRobotPlanner
from arm_planner import RoboticArmPlanner
# Prompts are now internal to each planner
```

### Step 2: Initialize Planners

**Old Code:**
```python
planner = QwenMultiAgentPlanner()
```

**New Code:**
```python
# Initialize both if needed, or just one
humanoid = HumanoidRobotPlanner()
arm = RoboticArmPlanner()
```

### Step 3: Route Requests Appropriately

**Decision Logic:**

```python
def route_request(request):
    """Determine which planner should handle the request"""

    # Keywords for humanoid robot (home control)
    home_keywords = ['ac', 'air conditioner', 'light', 'temperature',
                     'comfortable', 'cold', 'hot', 'dark', 'bright']

    # Keywords for robotic arm (store items)
    store_keywords = ['water', 'snacks', 'fruit', 'medicine',
                      'get', 'buy', 'fetch', 'item']

    request_lower = request.lower()

    # Check for home-related tasks
    if any(keyword in request_lower for keyword in home_keywords):
        if any(keyword in request_lower for keyword in store_keywords):
            return 'both'  # Coordinated task
        return 'humanoid'

    # Check for store-related tasks
    if any(keyword in request_lower for keyword in store_keywords):
        return 'arm' if 'get' in request_lower else 'both'

    # Default to humanoid for ambiguous requests
    return 'humanoid'

# Usage
request = "I'm cold and need water"
router = route_request(request)

if router == 'humanoid':
    plan = humanoid.plan_task(request)
    humanoid.execute_plan(plan)
elif router == 'arm':
    plan = arm.plan_task(request)
    arm.execute_plan(plan)
elif router == 'both':
    h_plan = humanoid.plan_task(request)
    humanoid.execute_plan(h_plan)
    a_plan = arm.plan_task(request)
    arm.execute_plan(a_plan)
```

### Step 4: Update Test Code

**Old Code:**
```python
planner = QwenMultiAgentPlanner()
planner.run_tests()
```

**New Code:**
```python
# Test each planner separately
humanoid = HumanoidRobotPlanner()
humanoid.run_tests()

arm = RoboticArmPlanner()
arm.run_tests()
```

## Common Migration Patterns

### Pattern 1: Simple Home Control

**Old:**
```python
planner = QwenMultiAgentPlanner()
plan = planner.plan_task("Turn on the AC")
planner.execute_plan(plan)
```

**New:**
```python
humanoid = HumanoidRobotPlanner()
plan = humanoid.plan_task("Turn on the AC")
humanoid.execute_plan(plan)
```

### Pattern 2: Store Item Retrieval

**Old:**
```python
planner = QwenMultiAgentPlanner()
plan = planner.plan_task("Get water from the store")
planner.execute_plan(plan)
```

**New:**
```python
# Humanoid handles navigation
humanoid = HumanoidRobotPlanner()
h_plan = humanoid.plan_task("Get water from the store")
humanoid.execute_plan(h_plan)

# Arm handles item retrieval
arm = RoboticArmPlanner()
a_plan = arm.plan_task("Get water for pickup")
arm.execute_plan(a_plan)
```

### Pattern 3: Complex Multi-Step Tasks

**Old:**
```python
planner = QwenMultiAgentPlanner()
plan = planner.plan_task("Make room comfortable and get snacks")
planner.execute_plan(plan)
```

**New:**
```python
# Split into two coordinated tasks
humanoid = HumanoidRobotPlanner()
arm = RoboticArmPlanner()

# Phase 1: Environment control
env_plan = humanoid.plan_task("Make room comfortable")
humanoid.execute_plan(env_plan)

# Phase 2: Item retrieval navigation
nav_plan = humanoid.plan_task("Go to store for snacks")
humanoid.execute_plan(nav_plan)

# Phase 3: Item picking
item_plan = arm.plan_task("Get snacks for pickup")
arm.execute_plan(item_plan)

# Phase 4: Return home (could be tracked by humanoid)
```

## API Compatibility

Both planners maintain the same API as the original:

### Initialization
```python
# Same parameters
planner = HumanoidRobotPlanner(api_key="...", model_name="qwen-plus")
planner = RoboticArmPlanner(api_key="...", model_name="qwen-plus")
```

### Planning
```python
# Same method signature
plan = planner.plan_task(
    request="...",
    return_raw=False,
    stream=False,
    debug=False
)
```

### Execution
```python
# Same method
planner.execute_plan(plan)
```

### Testing
```python
# Same method
planner.run_tests(stream=False)
```

### Model Switching
```python
# Same method
planner.switch_model("qwen-max")
```

## Benefits of Migration

1. **Clearer Responsibilities**: Each planner has a well-defined scope
2. **Better Performance**: More focused prompts yield better LLM responses
3. **Easier Debugging**: Issues can be isolated to specific planners
4. **Independent Testing**: Test each robot's capabilities separately
5. **Easier Extension**: Add robot-specific features without affecting the other
6. **Better Maintainability**: Smaller, focused codebases are easier to maintain

## Backward Compatibility

The original files are still available:
- `qwenapi_planner.py` - Original multi-agent planner
- `system_prompt_template.py` - Original system prompt
- `example_usage.py` - Original examples

You can continue using them if needed, but the dual planner system is recommended for new development.

## Quick Migration Checklist

- [ ] Install/update dependencies: `pip install -r requirements.txt`
- [ ] Set API key: `export DASHSCOPE_API_KEY='your-key'`
- [ ] Update imports to new planner classes
- [ ] Initialize both planners (or just the one you need)
- [ ] Route requests to appropriate planner
- [ ] Update test code to test each planner separately
- [ ] Test coordinated tasks between both planners
- [ ] Review and update any custom system prompts

## Getting Help

1. Check `README_DUAL_PLANNER.md` for comprehensive documentation
2. Run `python example_dual_planner_usage.py` for demos
3. Use debug mode: `plan = planner.plan_task(request, debug=True)`
4. Test individual components with the built-in test suites

## Example: Complete Migration

**Before:**
```python
# old_code.py
from qwenapi_planner import QwenMultiAgentPlanner

def main():
    planner = QwenMultiAgentPlanner()

    # Handle all requests with single planner
    requests = [
        "Turn on the AC",
        "Get water from store",
        "Make room comfortable and get snacks"
    ]

    for request in requests:
        plan = planner.plan_task(request)
        planner.execute_plan(plan)

if __name__ == "__main__":
    main()
```

**After:**
```python
# new_code.py
from humanoid_planner import HumanoidRobotPlanner
from arm_planner import RoboticArmPlanner

def main():
    humanoid = HumanoidRobotPlanner()
    arm = RoboticArmPlanner()

    # Request 1: Home control only
    plan1 = humanoid.plan_task("Turn on the AC")
    humanoid.execute_plan(plan1)

    # Request 2: Coordinated task
    plan2a = humanoid.plan_task("Get water from store")
    humanoid.execute_plan(plan2a)
    plan2b = arm.plan_task("Get water for pickup")
    arm.execute_plan(plan2b)

    # Request 3: Complex coordinated task
    plan3a = humanoid.plan_task("Make room comfortable and go to store for snacks")
    humanoid.execute_plan(plan3a)
    plan3b = arm.plan_task("Get snacks for pickup")
    arm.execute_plan(plan3b)

if __name__ == "__main__":
    main()
```

## Next Steps

After migration:
1. Test thoroughly with your specific use cases
2. Optimize request routing logic for your needs
3. Consider adding custom actions to individual planners
4. Explore the interactive mode for development/testing
5. Implement proper error handling for coordinated tasks

For more examples, see `example_dual_planner_usage.py`.
