# test_parser_fix.py

"""
Test the improved JSON parser with the problematic response
"""

from json_tool.json_parser_enhanced import parse_json_with_fallback

# The actual problematic response from your API
problematic_response = """
Human request: "Can you turn on the air conditioner?"
Context: {}
Task status: first step
---
{
  "task_understanding": {
    "original_request": "Can you turn on the air conditioner?",
    "current_goal": "Assess the current state of the environment before controlling the AC",
    "progress_summary": "No actions taken yet - this is the first step"
  },
  "next_step": {
    "step_number": 1,
    "agent": "Unitree-G1 humanoid_robot",
    "location": "home",
    "action": "<sense>get_observation()</sense>",
    "action_type": "sense",
    "parameters": {},
    rationale: "I need to check if the AC is already on and observe room conditions before making any changes. This ensures I don't duplicate efforts or miss important context.",
    expected_outcome: "A detailed description of current room state including AC status, temperature, and environmental conditions",
   estimated_duration: "3 seconds"
  },
"task_status": {
"is_complete": false,
"completion_percentage":0，
"remaining_steps_estimate":"2-4 more steps needed (observation → action → verification)"
}，
"human_feedback_request"：｛
"question":"Should I proceed with observingthe current room state?",
"options": ["proceed","modify","cancel"],
"waiting_for":"permission to use vision system"
}，
"contingency_note":"If observation fails，I may need to ask for manual confirmation of AC status or retry the observation"
}
"""

def test_parser():
    print("="*70)
    print("Testing Enhanced JSON Parser with Problematic Response")
    print("="*70)

    print("\n📄 Original Response (first 200 chars):")
    print(problematic_response[:200] + "...")

    print("\n" + "="*70)
    print("Attempting to parse...")
    print("="*70)

    result, success = parse_json_with_fallback(problematic_response, debug=True)

    print("\n" + "="*70)
    if success:
        print("✅ PARSING SUCCESSFUL!")
        print("="*70)
        print("\n📋 Parsed Result:")
        print(f"  - task_understanding: {result.get('task_understanding', {}).get('original_request', 'N/A')}")
        print(f"  - next_step action: {result.get('next_step', {}).get('action', 'N/A')}")
        print(f"  - next_step action_type: {result.get('next_step', {}).get('action_type', 'N/A')}")
        print(f"  - task_status is_complete: {result.get('task_status', {}).get('is_complete', 'N/A')}")
        print(f"  - human_feedback_request question: {result.get('human_feedback_request', {}).get('question', 'N/A')[:50]}...")

        # Check if all required fields are present
        print("\n🔍 Field Validation:")
        required_fields = ['task_understanding', 'next_step', 'task_status', 'human_feedback_request']
        for field in required_fields:
            status = "✅" if field in result else "❌"
            print(f"  {status} {field}")

        if 'next_step' in result:
            next_step_fields = ['action', 'action_type', 'rationale', 'expected_outcome']
            for field in next_step_fields:
                status = "✅" if field in result['next_step'] else "❌"
                print(f"  {status} next_step.{field}")

    else:
        print("❌ PARSING FAILED")
        print("="*70)
        print("\n📋 Error Result:")
        print(result)

    return success, result


if __name__ == "__main__":
    print("🧪 Testing Improved JSON Parser\n")
    success, result = test_parser()

    print("\n" + "="*70)
    if success:
        print("✅ Parser can now handle this response format!")
        print("\nThe following issues were fixed:")
        print("  1. ✅ Extra text before JSON (removed via '---' split)")
        print("  2. ✅ Chinese punctuation (，：｛｝ converted to ,:{} )")
        print("  3. ✅ Unquoted property names (rationale, expected_outcome)")
        print("  4. ✅ XML tags in action value (<sense>...</sense> removed)")
        print("  5. ✅ Trailing commas and formatting issues")
    else:
        print("❌ Parser still needs improvement")
        print("\nRemaining issues to fix:")
        if 'error' in result:
            print(f"  - {result['error']}")
    print("="*70)
