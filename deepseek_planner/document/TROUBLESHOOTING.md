# Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: "Failed to resolve 'dsv3.sii.edu.cn'"

**Error Message:**
```
❌ Connection failed: API request failed: HTTPConnectionPool(host='dsv3.sii.edu.cn', port=80):
Max retries exceeded with url: /v1/chat/completions
(Caused by NameResolutionError: Failed to resolve 'dsv3.sii.edu.cn')
```

**Cause:** The DeepSeek API endpoint `http://dsv3.sii.edu.cn` is not accessible from your current network. This is likely an internal/local API endpoint that requires:
- VPN connection
- Internal network access
- Specific DNS configuration

**Solutions:**

#### Option 1: Use Mock Testing (Recommended for Testing)
Test the functionality without requiring API access:

```bash
python test_interactive_mock.py
```

This demonstrates how the interactive planner works with simulated API responses.

#### Option 2: Configure Network Access
If you have access to the DeepSeek API:
1. Connect to VPN (if required)
2. Ensure DNS can resolve `dsv3.sii.edu.cn`
3. Test connection: `ping dsv3.sii.edu.cn`

#### Option 3: Use Alternative API Endpoint
If you have access to a different DeepSeek API or compatible endpoint:

```python
from humanoid_planner_interactive import HumanoidRobotPlannerInteractive

planner = HumanoidRobotPlannerInteractive(
    base_url="https://api.deepseek.com/v1/chat/completions",  # Your endpoint
    model_name="deepseek-chat"  # Your model name
)
```

#### Option 4: Use OpenAI-Compatible API
The planner can work with any OpenAI-compatible chat completion API:

```python
planner = HumanoidRobotPlannerInteractive(
    base_url="https://api.openai.com/v1/chat/completions",
    model_name="gpt-4"
)

# Add API key to headers
planner.headers["Authorization"] = "Bearer YOUR_API_KEY"
```

---

### Issue 2: "Failed to parse step plan"

**Error Message:**
```
❌ Error: Failed to parse step plan - JSON parsed but missing 'next_step' field
```

**Cause:** The LLM response doesn't match the expected JSON format for interactive mode.

**Solutions:**

#### Check the Raw Response
Enable debug mode to see what the LLM is returning:

```python
step_plan = planner.start_task("I need water", "session_1", debug=True)
```

This will print:
- The raw API response
- JSON parsing attempts
- What fields were found

#### Verify the System Prompt
Ensure you're using the interactive prompt:

```python
from humanoid_prompt_template_interactive import get_humanoid_interactive_system_prompt

planner.system_prompt = get_humanoid_interactive_system_prompt()
```

#### Check Expected Format
The LLM should return JSON with this structure:

```json
{
  "task_understanding": {...},
  "next_step": {
    "step_number": 1,
    "action": "get_observation",
    "action_type": "sense",
    ...
  },
  "task_status": {...},
  "human_feedback_request": {...}
}
```

If the LLM returns the **old format** (with `execution_plan` array), you may be using the wrong system prompt.

---

### Issue 3: Session Not Found

**Error Message:**
```
❌ Error: Session session_001 not found
```

**Cause:** Trying to use `plan_next_step()` before calling `start_task()`.

**Solution:**
Always start with `start_task()`:

```python
# Wrong
step = planner.plan_next_step("new_session")  # ❌ Session doesn't exist

# Correct
step = planner.start_task("Get water", "new_session")  # ✅ Creates session
step = planner.plan_next_step("new_session")           # ✅ Now it works
```

---

### Issue 4: Task Already Complete

**Error Message:**
```
{"message": "Task already complete", "total_steps": 5}
```

**Cause:** Trying to plan next step after task is marked complete.

**Solution:**
Check task status before planning:

```python
info = planner.get_session_info(session_id)
if info['is_complete']:
    print("Task is done!")
else:
    step = planner.plan_next_step(session_id)
```

---

## Testing Without API Access

### Mock Testing
Use the mock test script to verify functionality:

```bash
python test_interactive_mock.py
```

**What it does:**
- Simulates LLM responses
- Demonstrates step-by-step planning
- Shows human-in-the-loop workflow
- No API connection required

### Manual JSON Testing
Create your own test responses:

```python
from humanoid_planner_interactive import HumanoidRobotPlannerInteractive
import json

planner = HumanoidRobotPlannerInteractive()

# Mock the API method
def mock_response(messages):
    return {
        'choices': [{
            'message': {
                'content': json.dumps({
                    "task_understanding": {
                        "original_request": "test",
                        "current_goal": "test goal",
                        "progress_summary": "testing"
                    },
                    "next_step": {
                        "step_number": 1,
                        "action": "test_action",
                        "action_type": "talk",
                        "rationale": "testing",
                        "expected_outcome": "test outcome",
                        "estimated_duration": "1s"
                    },
                    "task_status": {
                        "is_complete": False,
                        "completion_percentage": 10,
                        "remaining_steps_estimate": "5 steps"
                    },
                    "human_feedback_request": {
                        "question": "Proceed?",
                        "options": ["yes"],
                        "waiting_for": "approval"
                    }
                })
            }
        }]
    }

planner._make_api_request = mock_response

# Now test
step = planner.start_task("test", "session_1")
print(f"Action: {step['next_step']['action']}")
```

---

## Debugging Checklist

When something goes wrong, check:

1. **API Connection**
   ```python
   planner.test_connection()  # Should return True
   ```

2. **Session Exists**
   ```python
   planner.get_session_info(session_id)  # Should not error
   ```

3. **System Prompt**
   ```python
   print(len(planner.system_prompt))  # Should be ~9000+ chars for interactive
   ```

4. **Response Format**
   ```python
   # Enable debug to see raw responses
   planner.start_task("test", "s1", debug=True)
   ```

5. **Model Configuration**
   ```python
   print(planner.config)  # Check temperature, max_tokens, etc.
   ```

---

## Network Configuration

### If Using Internal DeepSeek Endpoint

**Check DNS:**
```bash
nslookup dsv3.sii.edu.cn
```

**Check Connectivity:**
```bash
ping dsv3.sii.edu.cn
```

**Test API Manually:**
```bash
curl -X POST http://dsv3.sii.edu.cn/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v3-ep","messages":[{"role":"user","content":"hello"}]}'
```

### If Behind Proxy

Configure proxy in the planner:

```python
import requests

planner = HumanoidRobotPlannerInteractive()

# Add proxy configuration
session = requests.Session()
session.proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'https://proxy.example.com:8080'
}

# Would need to modify planner to use session instead of requests.post
```

---

## Getting Help

If issues persist:

1. **Check the raw response:**
   ```python
   step = planner.start_task("test", "s1", debug=True)
   ```

2. **Test with mock first:**
   ```bash
   python test_interactive_mock.py
   ```

3. **Verify API endpoint:**
   - Can you access it from a browser?
   - Does it require authentication?
   - Is it the correct URL?

4. **Check system prompt:**
   - Using interactive prompt?
   - Using old prompt by mistake?

5. **Review logs:**
   - Enable debug mode
   - Check error messages
   - Verify JSON structure

---

## Quick Fixes

### Can't Access API
→ Use `test_interactive_mock.py`

### JSON Parse Error
→ Enable `debug=True` and check format

### Session Not Found
→ Call `start_task()` first

### Task Complete
→ Check `is_complete` before planning

### Wrong Response Format
→ Verify using interactive prompt, not original prompt

---

## Summary

The interactive planner requires:
1. ✅ Accessible DeepSeek API endpoint (or mock)
2. ✅ Correct system prompt (interactive version)
3. ✅ Proper session management
4. ✅ Expected JSON response format

**For testing without API access:** Use `test_interactive_mock.py`

**For production use:** Ensure network access to DeepSeek API or configure alternative endpoint.
