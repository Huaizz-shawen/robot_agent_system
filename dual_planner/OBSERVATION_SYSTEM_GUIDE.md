# Observation System Guide - Vision-Language Model Integration

This guide documents the observation system added to both planners, enabling vision-grounded robot control through VLM integration.

## Overview

The observation system introduces a **sense-plan-act cycle** that allows robots to:
- Perceive their environment through vision
- Verify action outcomes
- Detect and recover from failures
- Adapt plans based on real-world observations

## New Tool Category: `<sense>`

### Tool Categories Hierarchy

```
<talk>   - Communication (instant)
<tool>   - Device/data operations (milliseconds to seconds)
<sense>  - Visual perception (2-3 seconds with VLM processing)
<act>    - Physical actions (seconds to minutes)
```

### The `get_observation()` Tool

**Syntax:**
```
<sense>get_observation()</sense>
```

**Function:**
- Captures image from robot's camera
- Processes image through Vision-Language Model (VLM)
- Returns natural language description of current scene

**Parameters:**
- None (uses default camera and VLM settings)

**Returns:**
- String: Natural language description of observed scene

**Timing:**
- Processing time: 2-3 seconds (image capture + VLM inference)
- Minimum interval: 10 seconds between calls (resource constraint)
- Execution: Sequential (cannot overlap with `<act>` actions)

## When to Use Observations

### Humanoid Robot (Unitree-G1)

**Critical Observation Points:**
1. **Task Start**: Understand initial environment state
   ```
   1. <sense>get_observation()</sense>  # What's the current room state?
   2. <tool>control_air_conditioner(...)</tool>
   ```

2. **After Navigation**: Verify arrival and position
   ```
   3. <act>navigate_to_store()</act>
   4. <sense>get_observation()</sense>  # Did I arrive? Any obstacles?
   ```

3. **After Device Control**: Verify state change
   ```
   2. <tool>control_light("turn_on")</tool>
   3. <sense>get_observation()</sense>  # Are lights actually on?
   ```

4. **Before Critical Actions**: Safety checks
   ```
   5. <sense>get_observation()</sense>  # Is path clear? Human present?
   6. <act>return_home_with_item("water")</act>
   ```

5. **Task Completion**: Confirm goal achieved
   ```
   9. <sense>get_observation()</sense>  # Task completed successfully?
   10. <talk>talk_with_human("Task complete")</talk>
   ```

### Robotic Arm (UR5e)

**Critical Observation Points:**
1. **Before Picking**: Locate item and plan grasp
   ```
   2. <sense>get_observation()</sense>  # Where exactly is the item?
   3. <act>pick_from_shelf("water", "Shelf A, Level 1")</act>
   ```

2. **After Picking**: Verify grasp success
   ```
   4. <sense>get_observation()</sense>  # Is item in gripper?
   ```

3. **Before Placing**: Check counter clearance
   ```
   4. <sense>get_observation()</sense>  # Is counter clear?
   5. <act>place_on_counter("water")</act>
   ```

4. **After Placing**: Confirm placement success
   ```
   6. <sense>get_observation()</sense>  # Is item properly placed?
   ```

5. **Inventory Verification**: Cross-check database
   ```
   1. <tool>verify_item_availability("medicine")</tool>
   2. <sense>get_observation()</sense>  # Visual confirmation
   ```

## Updated Output Format

### New Fields in JSON Output

```json
{
  "task_analysis": {
    "intent": "string",
    "entities": ["list"],
    "complexity": "simple|moderate|complex",
    "estimated_duration": "X minutes",
    "requires_observation": true  // NEW: Does task need vision?
  },
  "execution_plan": [
    {
      "step": 1,
      "agent": "robot_name",
      "location": "location",
      "action": "get_observation",
      "action_type": "sense",  // NEW: Explicit action type
      "parameters": {},
      "dependencies": [],
      "success_criteria": "Scene captured and described",
      "observation_needed": false  // NEW: Should observation follow?
    },
    {
      "step": 2,
      "action": "control_air_conditioner",
      "action_type": "tool",  // NEW: Explicit type
      "parameters": {"action": "turn_on", "temperature": 24},
      "dependencies": [1],  // Depends on observation
      "success_criteria": "AC is on at 24°C",
      "observation_needed": true  // NEW: Verify after this step
    }
  ],
  "contingency_plans": [
    {
      "failure_scenario": "AC doesn't turn on",
      "alternative_action": "Notify human and suggest manual control",
      "requires_observation": true  // NEW: Use observation to diagnose
    }
  ],
  "human_feedback": "I'll turn on the AC and verify it's working",
  "initial_observation_required": true,  // NEW: Start with observation?
  "current_time": "2025-01-06 15:30:00"
}
```

## Example Patterns with Observations

### Pattern 1: Simple Control with Verification (Humanoid)

```json
{
  "task_analysis": {
    "intent": "environment_control",
    "entities": ["air_conditioner", "temperature"],
    "complexity": "simple",
    "estimated_duration": "30 seconds",
    "requires_observation": true
  },
  "execution_plan": [
    {
      "step": 1,
      "action": "get_observation",
      "action_type": "sense",
      "parameters": {},
      "dependencies": [],
      "success_criteria": "Current room state captured",
      "observation_needed": false
    },
    {
      "step": 2,
      "action": "control_air_conditioner",
      "action_type": "tool",
      "parameters": {"action": "turn_on", "temperature": 24},
      "dependencies": [1],
      "success_criteria": "AC command sent",
      "observation_needed": true
    },
    {
      "step": 3,
      "action": "get_observation",
      "action_type": "sense",
      "parameters": {},
      "dependencies": [2],
      "success_criteria": "AC operation verified visually",
      "observation_needed": false
    },
    {
      "step": 4,
      "action": "talk_with_human",
      "action_type": "talk",
      "parameters": {"message": "AC is on at 24°C"},
      "dependencies": [3],
      "success_criteria": "Human informed",
      "observation_needed": false
    }
  ],
  "initial_observation_required": true
}
```

### Pattern 2: Pick-Place with Grasp Verification (Arm)

```json
{
  "task_analysis": {
    "intent": "item_retrieval",
    "entities": ["water"],
    "complexity": "simple",
    "estimated_duration": "45 seconds",
    "requires_observation": true
  },
  "execution_plan": [
    {
      "step": 1,
      "action": "verify_item_availability",
      "action_type": "tool",
      "parameters": {"item_name": "water"},
      "dependencies": [],
      "success_criteria": "Water in inventory",
      "observation_needed": false
    },
    {
      "step": 2,
      "action": "get_observation",
      "action_type": "sense",
      "parameters": {},
      "dependencies": [],
      "success_criteria": "Water located visually on Shelf A",
      "observation_needed": false
    },
    {
      "step": 3,
      "action": "pick_from_shelf",
      "action_type": "act",
      "parameters": {
        "item_name": "water",
        "shelf_location": "Shelf A, Level 1"
      },
      "dependencies": [1, 2],
      "success_criteria": "Pick motion completed",
      "observation_needed": true
    },
    {
      "step": 4,
      "action": "get_observation",
      "action_type": "sense",
      "parameters": {},
      "dependencies": [3],
      "success_criteria": "Water in gripper confirmed",
      "observation_needed": false
    },
    {
      "step": 5,
      "action": "place_on_counter",
      "action_type": "act",
      "parameters": {"item_name": "water"},
      "dependencies": [4],
      "success_criteria": "Place motion completed",
      "observation_needed": true
    },
    {
      "step": 6,
      "action": "get_observation",
      "action_type": "sense",
      "parameters": {},
      "dependencies": [5],
      "success_criteria": "Water on counter confirmed",
      "observation_needed": false
    }
  ],
  "contingency_plans": [
    {
      "failure_scenario": "Grasp fails (step 4 shows empty gripper)",
      "alternative_action": "Retry pick_from_shelf with adjusted approach",
      "requires_observation": true
    },
    {
      "failure_scenario": "Placement fails (step 6 shows item not on counter)",
      "alternative_action": "Clear counter and retry placement",
      "requires_observation": true
    }
  ],
  "initial_observation_required": true
}
```

## Observation Strategy Guidelines

### Observation Frequency

**Too Few Observations (Risky):**
```
❌ 1. <act>pick_from_shelf("water", "Shelf A, Level 1")</act>
❌ 2. <act>place_on_counter("water")</act>
❌ 3. <talk>communicate_with_humanoid("Water ready")</talk>
```
*Problem: No verification, failures go undetected*

**Optimal Observations (Recommended):**
```
✅ 1. <sense>get_observation()</sense>  # Locate item
✅ 2. <act>pick_from_shelf("water", "Shelf A, Level 1")</act>
✅ 3. <sense>get_observation()</sense>  # Verify grasp
✅ 4. <act>place_on_counter("water")</act>
✅ 5. <sense>get_observation()</sense>  # Verify placement
✅ 6. <talk>communicate_with_humanoid("Water ready")</talk>
```
*Balanced: Critical verification points covered*

**Too Many Observations (Inefficient):**
```
⚠️ 1. <sense>get_observation()</sense>
⚠️ 2. <tool>verify_item_availability("water")</tool>
⚠️ 3. <sense>get_observation()</sense>  # Redundant
⚠️ 4. <act>pick_from_shelf("water", "Shelf A, Level 1")</act>
⚠️ 5. <sense>get_observation()</sense>
⚠️ 6. <sense>get_observation()</sense>  # Redundant, too soon
⚠️ 7. <act>place_on_counter("water")</act>
```
*Problem: Wastes time and computation*

### Observation Best Practices

1. **Always observe before first action** in a task
   - Establishes baseline understanding

2. **Always observe after physical actions** (`<act>`)
   - Verify motion succeeded
   - Detect unexpected outcomes

3. **Respect 10-second minimum interval**
   - Don't observe more frequently than system allows

4. **Use observations for contingency triggering**
   - Check observation result
   - Compare to expected state
   - Trigger alternative actions if mismatch

5. **Batch observations when possible**
   - One observation can inform multiple subsequent actions
   - E.g., observe shelf once for multiple items on same shelf

## Implementation Notes

### VLM Prompt Design

When the robot calls `get_observation()`, the VLM receives a prompt like:

```python
vlm_prompt = f"""
You are analyzing a scene from a {robot_type}'s perspective.

Current task: {current_task_description}
Expected to see: {expected_scene_elements}

Describe what you see in the image, focusing on:
{'- Human presence and activity' if humanoid else ''}
{'- AC and light states' if humanoid else ''}
{'- Shelf contents and organization' if arm else ''}
{'- Items in gripper' if arm else ''}
{'- Counter state and items' if arm else ''}
- Any obstacles or anomalies
- Task-relevant objects and their states

Be specific and concise. Mention both what IS present and what is MISSING if relevant to the task.
"""
```

### Observation Caching Strategy

```python
class ObservationManager:
    def __init__(self, min_interval=10.0):
        self.min_interval = min_interval
        self.last_obs_time = None
        self.last_obs_result = None

    def get_observation(self, force=False):
        """
        Get observation with automatic caching.

        Args:
            force: If True, bypass cache and get fresh observation

        Returns:
            str: VLM description of scene
        """
        current_time = time.time()

        # Check if we can use cached observation
        if not force and self.last_obs_time is not None:
            time_since_last = current_time - self.last_obs_time
            if time_since_last < self.min_interval:
                print(f"⚠️ Returning cached observation (only {time_since_last:.1f}s since last)")
                return self.last_obs_result

        # Get fresh observation
        image = capture_camera_image()
        description = call_vlm(image)

        # Update cache
        self.last_obs_time = current_time
        self.last_obs_result = description

        return description
```

### Background Observation System

In addition to planned observations, implement automatic background observations:

```python
class BackgroundObserver:
    """Provides automatic periodic observations for safety monitoring."""

    def __init__(self, interval=10.0):
        self.interval = interval
        self.running = False
        self.latest_obs = None

    def start(self):
        """Start background observation thread."""
        self.running = True
        threading.Thread(target=self._observe_loop, daemon=True).start()

    def _observe_loop(self):
        while self.running:
            self.latest_obs = get_observation()
            self._check_for_anomalies(self.latest_obs)
            time.sleep(self.interval)

    def _check_for_anomalies(self, observation):
        """Check observation for safety issues."""
        # Detect humans entering workspace
        # Detect unexpected obstacles
        # Detect device malfunctions
        # Trigger emergency stops if needed
        pass

    def get_latest(self):
        """Get most recent background observation."""
        return self.latest_obs
```

## Benefits of Observation System

### 1. Closed-Loop Control
- Robots verify their actions actually worked
- Reduces accumulation of errors
- Enables adaptive behavior

### 2. Failure Detection
- Grasp failures detected immediately
- Navigation obstacles identified
- Device malfunctions caught early

### 3. Recovery Planning
- Observations provide diagnostic information
- Enables intelligent retry strategies
- Allows graceful degradation

### 4. Safety
- Background observations monitor for humans
- Unexpected obstacles detected
- Emergency situations identified

### 5. Robustness
- Handles sim-to-real gaps
- Adapts to changing environments
- Tolerates model inaccuracies

## Testing Observations

### Test Cases

1. **Observation Accuracy**: Does VLM correctly describe scene?
2. **Failure Detection**: Does observation detect grasp failures?
3. **Timing**: Are observations properly spaced (10s minimum)?
4. **Contingency Triggering**: Do observation mismatches trigger recovery?
5. **Background System**: Does background observer work independently?

### Example Test: Grasp Failure Detection

```python
def test_grasp_failure_detection():
    """Test that observation detects grasp failures."""
    arm = RoboticArmPlanner()

    # Request item pickup
    plan = arm.plan_task("Get water")

    # Simulate grasp failure
    def mock_observation_after_pick():
        return "The robotic arm is positioned near Shelf A, Level 1. The gripper is empty. No item is held."

    # Execute plan with mocked observation
    execute_with_mock_observation(plan, mock_observation_after_pick)

    # Verify contingency plan was triggered
    assert contingency_triggered("grasp_failure")
    assert retry_attempted()
```

## Future Enhancements

1. **Attention Mechanisms**: VLM focuses on task-relevant regions
2. **Multi-View Observations**: Combine multiple camera angles
3. **Temporal Reasoning**: Compare current vs. previous observations
4. **Active Perception**: Robot repositions camera for better views
5. **Uncertainty Estimation**: VLM reports confidence in descriptions
6. **Visual Question Answering**: Ask specific questions about scene

## Summary

The observation system transforms both planners from **open-loop** (blind execution) to **closed-loop** (vision-grounded) control. This enables:

- ✅ Verification of action outcomes
- ✅ Early failure detection
- ✅ Intelligent error recovery
- ✅ Adaptive task execution
- ✅ Safer human-robot interaction

By integrating VLM-based perception into the planning loop, the robots can now **see, understand, and adapt** to the real world.
