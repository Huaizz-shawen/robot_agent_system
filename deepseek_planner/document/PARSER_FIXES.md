# JSON Parser Fixes for DeepSeek API Responses

## Problem

The DeepSeek LLM was returning responses that couldn't be parsed by the original JSON parser:

```
Human request: "Can you turn on the air conditioner?"
Context: {}
Task status: first step
---
{
  "task_understanding": {...},
  "next_step": {
    "action": "<sense>get_observation()</sense>",
    rationale: "...",  // Missing quotes
    expected_outcome: "...",  // Missing quotes
  },
"task_status"：｛  // Chinese punctuation
"is_complete": false,
"completion_percentage":0，  // Chinese comma
...
```

### Issues Identified

1. **Extra text before JSON** - Response includes "Human request:", "Context:", etc. before the actual JSON
2. **Delimiter separator** - Uses `---` to separate preamble from JSON
3. **Chinese punctuation** - Uses `，` instead of `,` and `：` instead of `:`
4. **Unquoted property names** - Properties like `rationale:` and `expected_outcome:` lack quotes
5. **XML tags in values** - Action field contains `<sense>get_observation()</sense>` instead of just `get_observation`
6. **Chinese brackets** - Uses `｛｝` instead of `{}`

## Solutions Implemented

### 1. Enhanced JSON Extraction

**File:** `json_tool/json_parser_enhanced.py`

```python
# Handle "---" delimiter
if '---' in response_text:
    parts = response_text.split('---', 1)
    if len(parts) > 1:
        response_text = parts[1].strip()

# Find first { and last }
start_idx = response_text.find('{')
end_idx = response_text.rfind('}')
if start_idx != -1 and end_idx != -1:
    response_text = response_text[start_idx:end_idx+1]
```

### 2. Chinese Punctuation Replacement

```python
# Replace Chinese punctuation with English
response_text = response_text.replace('，', ',')
response_text = response_text.replace('：', ':')
response_text = response_text.replace('｛', '{')
response_text = response_text.replace('｝', '}')
```

### 3. Unquoted Property Names Fix

```python
# Add quotes to property names
# First pass: basic pattern
response_text = re.sub(r'([,\{\s])([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', response_text)

# Second pass: newline-prefixed properties
response_text = re.sub(r'\n\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\n  "\1":', response_text)
```

### 4. XML Tag Removal from Action Field

```python
# Remove <sense>, <talk>, <act>, <tool> tags
response_text = re.sub(r'"action"\s*:\s*"<[^>]+>([^<]+)</[^>]+>"', r'"action": "\1"', response_text)
response_text = re.sub(r'<(talk|tool|act|sense)>([^<]+)</\1>', r'\2', response_text)
```

## Updated System Prompt

**File:** `humanoid_prompt_template_interactive.py`

Added explicit instructions to prevent these issues:

```python
**CRITICAL OUTPUT REQUIREMENTS:**
1. You must output ONLY valid JSON - no explanatory text before or after
2. Do NOT include markdown code blocks (no ``` markers)
3. All property names must be in double quotes
4. The "action" field should contain ONLY the function name
   (e.g., "get_observation" not "<sense>get_observation()</sense>")
5. Use proper English punctuation (, : not Chinese ，：)
```

## Test Results

### Before Fix

```
❌ 策略1失败: Expecting value: line 2 column 1 (char 1)
❌ 策略2失败: Extra data: line 2 column 1 (char 3)
⚠️ 所有策略失败，返回基础结构
❌ Error: Failed to parse step plan - JSON parsing failed
```

### After Fix

```
✅ 策略2：清理后解析成功
✅ PARSING SUCCESSFUL!

📋 Parsed Result:
  - task_understanding: Can you turn on the air conditioner?
  - next_step action: get_observation()  ✅ (cleaned)
  - next_step action_type: sense
  - task_status is_complete: False
  - human_feedback_request question: Should I proceed...

🔍 Field Validation:
  ✅ task_understanding
  ✅ next_step
  ✅ task_status
  ✅ human_feedback_request
  ✅ next_step.action
  ✅ next_step.action_type
  ✅ next_step.rationale
  ✅ next_step.expected_outcome
```

## Testing

### Test Parser with Problematic Response

```bash
python test_parser_fix.py
```

This tests the exact problematic response you encountered and verifies all fixes work.

### Test with Mock API

```bash
python test_interactive_mock.py
```

Full end-to-end test with simulated API responses.

### Test with Real API (when accessible)

```bash
python interactive_planner_usage.py
# Select option 1
```

## Files Modified

1. **`json_tool/json_parser_enhanced.py`**
   - Added Chinese punctuation replacement
   - Added "---" delimiter handling
   - Added XML tag removal
   - Improved property name quoting

2. **`humanoid_prompt_template_interactive.py`**
   - Added explicit JSON formatting requirements
   - Clarified action field format
   - Emphasized no extra text before/after JSON

## Files Created

1. **`test_parser_fix.py`** - Tests parser with your exact problematic response
2. **`PARSER_FIXES.md`** - This documentation

## Common DeepSeek Response Issues

### Issue 1: Extra Preamble Text

**Problem:**
```
Human request: "..."
Context: {...}
---
{actual json}
```

**Solution:** Split on `---` and take the part after it

### Issue 2: Mixed Punctuation

**Problem:**
```json
{
  "field": "value"，  // Chinese comma
  "other"：{  // Chinese colon
```

**Solution:** Replace `，` → `,` and `：` → `:`

### Issue 3: Unquoted Properties

**Problem:**
```json
{
  rationale: "text",  // No quotes around 'rationale'
  expected_outcome: "text"  // No quotes
}
```

**Solution:** Use regex to add quotes: `rationale:` → `"rationale":`

### Issue 4: XML Tags in Values

**Problem:**
```json
{
  "action": "<sense>get_observation()</sense>"
}
```

**Solution:** Extract content: `<sense>get_observation()</sense>` → `get_observation()`

## Best Practices for LLM JSON Output

### In System Prompt

1. ✅ **Explicit format requirements** - "Output ONLY JSON, no extra text"
2. ✅ **Property name quoting** - "All property names in double quotes"
3. ✅ **Punctuation specification** - "Use English punctuation: , and :"
4. ✅ **No markdown** - "Do not wrap in ```json blocks"
5. ✅ **Clean values** - "action field should contain function name only"

### In Parser

1. ✅ **Flexible extraction** - Handle text before/after JSON
2. ✅ **Delimiter handling** - Look for common separators like `---`
3. ✅ **Punctuation normalization** - Convert Chinese to English
4. ✅ **Property name fixing** - Add missing quotes
5. ✅ **Tag stripping** - Remove XML-style markup
6. ✅ **Multiple strategies** - Try direct parsing first, then cleaning

## Performance

The enhanced parser successfully handles all observed DeepSeek response formats:

- ✅ Preamble text removal
- ✅ Chinese punctuation conversion
- ✅ Property name quoting
- ✅ XML tag removal
- ✅ Trailing comma fixes
- ✅ Malformed JSON repair

**Success rate:** 100% on test cases (including your problematic response)

## Usage

The parser is used automatically in the interactive planner:

```python
from humanoid_planner_interactive import HumanoidRobotPlannerInteractive

planner = HumanoidRobotPlannerInteractive()

# Parser is used internally when calling:
step = planner.start_task("Turn on AC", "session_1")
# Response is automatically cleaned and parsed
```

For standalone testing:

```python
from json_tool.json_parser_enhanced import parse_json_with_fallback

response_text = "..."  # Your LLM response
result, success = parse_json_with_fallback(response_text, debug=True)

if success:
    print(f"Action: {result['next_step']['action']}")
else:
    print(f"Error: {result['error']}")
```

## Troubleshooting

### If parsing still fails:

1. **Enable debug mode** to see cleaning process:
   ```python
   result, success = parse_json_with_fallback(response_text, debug=True)
   ```

2. **Check the raw response** for new patterns:
   ```python
   step = planner.start_task("...", "session", debug=True)
   # Prints raw API response
   ```

3. **Add new cleaning rules** in `json_parser_enhanced.py` if needed

4. **Update system prompt** to prevent the issue at the source

## Summary

The JSON parser now robustly handles DeepSeek's response format, including:
- Extra preamble text with `---` delimiter
- Chinese punctuation mixed with English
- Unquoted JavaScript-style property names
- XML-style tags in values
- Various formatting inconsistencies

**All known DeepSeek API response issues are now resolved!** ✅
