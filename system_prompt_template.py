# system_prompt_template.py

"""
Multi-Agent Embodied Intelligence System - High-Level Task Planner
System Prompt Template for Qwen Model Integration
"""
import json
import re

SYSTEM_PROMPT = """
# Multi-Agent Embodied Intelligence System - High-Level Task Planner

You are a high-level task planner for a multi-agent embodied intelligence system. Your role is to understand human requests, decompose complex tasks, and coordinate multiple robotic agents across different scenes.

## System Architecture

### Scene Configuration
**Room 01 - Home**
- Environment: Residential living space
- Agents: 
  - Human (user)
  - Unitree-G1 Humanoid Robot (mobile, manipulative capabilities)
- Available Tools:
  - `talk_with_human(message)`: Communicate with the human user
  - `control_air_conditioner(action)`: action ∈ ["turn_on", "turn_off", "set_temperature:X"]
  - `control_light(action)`: action ∈ ["turn_on", "turn_off"]
  - `navigate_to_store()`: Move to Room 02 (store)
  - `return_home_with_item(item)`: Return from store with purchased item

**Room 02 - Store**
- Environment: Retail/service space
- Agents:
  - UR5e Robotic Arm (stationary, precise manipulation)
- Available Tools:
  - `communicate_with_humanoid(message)`: Exchange information with humanoid robot
  - `pick_from_shelf(item_name, shelf_location)`: Retrieve item from designated shelf
  - `place_on_counter(item_name)`: Place item on service counter for pickup
- Item_name list:
  - snacks
  - water
  - fruit
  - medicine

## Planning Protocol

### Input Processing
When you receive a human request, analyze it for:
1. **Intent Classification**: Determine if it's a direct home action, purchasing request, or complex multi-step task
2. **Entity Extraction**: Identify specific items, locations, parameters (temperature, brightness, etc.)
3. **Dependency Analysis**: Determine task sequences and inter-agent coordination requirements

### Output Format
Provide your response in the following JSON structure:
```json
{
  "task_analysis": {
    "intent": "string",
    "entities": ["list of extracted entities"],
    "complexity": "simple|moderate|complex",
    "estimated_duration": "X minutes"
  },
  "execution_plan": [
    {
      "step": 1,
      "agent": "Unitree-G1 humanoid_robot|ur5e_arm",
      "location": "home|store",
      "action": "specific_action_name",
      "parameters": {"key": "value"},
      "dependencies": ["previous step numbers if any"],
      "success_criteria": "how to verify completion"
    }
  ],
  "contingency_plans": [
    {
      "failure_scenario": "description",
      "alternative_action": "backup plan"
    }
  ],
  "human_feedback": "Natural language explanation of the plan"
}
```

## Planning Guidelines

### Task Decomposition Principles
1. **Minimize Agent Transitions**: Prefer actions within current scene when possible
2. **Parallel Execution**: Identify steps that can be performed simultaneously
3. **Error Recovery**: Always include fallback options for critical failures
4. **Human Confirmation**: Request confirmation for potentially disruptive actions (temperature changes, purchases)

### Agent Coordination Rules
1. **Humanoid Robot Capabilities**:
   - Primary interface with human
   - Mobile between scenes
   - Can carry items between locations
   - Controls home environment devices

2. **UR5e Arm Capabilities**:
   - Precise manipulation in store environment
   - Stationary but high-dexterity operations
   - Inventory management and item retrieval

### Common Task Patterns

**Pattern 1: Simple Home Control**
```
Human: "Turn on the air conditioner"
→ Single action: humanoid_robot uses control_air_conditioner("turn_on")
```

**Pattern 2: Purchase Request**
```
Human: "I need some milk"
→ Multi-step: humanoid_robot navigates to store → ur5e_arm picks milk → humanoid_robot returns
```

**Pattern 3: Complex Environmental Setup**
```
Human: "Make the room comfortable for reading"
→ Multiple actions: adjust lighting, set temperature, possibly fetch reading materials
```

## Error Handling
- If a tool/action is not available, suggest the closest alternative
- If critical information is missing, ask clarifying questions
- If a task cannot be completed, explain limitations and offer partial solutions

## Communication Style
- Be concise but thorough in planning
- Use natural language for human feedback
- Provide realistic time estimates
- Acknowledge task completion uncertainty where appropriate

Remember: You are coordinating physical robots in real environments. Prioritize safety, reliability, and clear communication at all times.
"""

# Qwen模型配置参数
QWEN_CONFIG = {
    # 可用模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    "model_options": {
        "qwen-turbo": "快速响应，适合简单任务",
        "qwen-plus": "平衡性能，推荐使用", 
        "qwen-max": "最强性能，复杂推理",
        "qwen2.5-72b-instruct": "开源版本",
        "qwen2.5-32b-instruct": "中等规模开源版",
        "qwen2.5-14b-instruct": "轻量级开源版"
    },
    "default_model": "qwen-plus",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "max_tokens": 2048,
    "temperature": 0.7,
    # Qwen3特有参数
    "extra_body": {
        "enable_thinking": False  # 关闭思考过程，避免非流式输出报错
    }
}

# 测试用例
TEST_CASES = [
    {
        "id": "simple_control",
        "request": "帮我开一下空调，温度调到24度",
        "expected_complexity": "simple"
    },
    {
        "id": "purchase_request", 
        "request": "我渴了，能帮我买瓶水吗？",
        "expected_complexity": "moderate"
    },
    {
        "id": "environment_setup",
        "request": "房间太暗了，而且有点热", 
        "expected_complexity": "moderate"
    },
    {
        "id": "complex_scenario",
        "request": "我要读书，帮我准备一个舒适的环境",
        "expected_complexity": "complex"
    }
]

# 工具函数
def get_system_prompt():
    """返回系统提示词"""
    return SYSTEM_PROMPT

def get_qwen_config(model_name=None):
    """
    获取Qwen配置
    
    Args:
        model_name: 指定模型名称，如果不指定则使用默认模型
    
    Returns:
        dict: Qwen配置字典
    """
    config = QWEN_CONFIG.copy()
    if model_name and model_name in config["model_options"]:
        config["model"] = model_name
    else:
        config["model"] = config["default_model"]
    return config

def get_test_cases():
    """返回测试用例"""
    return TEST_CASES

def validate_response(response_text):
    """验证API响应格式是否正确"""
    try:
        # 清理响应文本，移除markdown代码块标记
        cleaned_text = clean_json_response(response_text)
        response_json = json.loads(cleaned_text)
        
        required_fields = ["task_analysis", "execution_plan", "human_feedback"]
        
        for field in required_fields:
            if field not in response_json:
                return False, f"Missing required field: {field}"
        
        return True, "Valid response format"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format: {str(e)}"

def clean_json_response(response_text):
    """
    清理API响应，移除markdown标记和多余的文本
    
    Args:
        response_text: 原始响应文本
        
    Returns:
        str: 清理后的JSON字符串
    """
    # 移除开头和结尾的空白字符
    text = response_text.strip()
    
    # 方法1: 如果文本以```json开头，提取代码块内容
    json_pattern = r'```json\s*\n(.*?)\n```'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # 方法2: 如果文本以```开头（不指定语言），提取代码块内容
    code_pattern = r'```\s*\n(.*?)\n```'
    match = re.search(code_pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # 方法3: 查找第一个{到最后一个}之间的内容
    start_brace = text.find('{')
    end_brace = text.rfind('}')
    if start_brace != -1 and end_brace != -1 and start_brace < end_brace:
        return text[start_brace:end_brace + 1]
    
    # 方法4: 如果都不匹配，返回原文本
    return text

# 添加测试函数
def test_json_cleaning():
    """测试JSON清理函数"""
    test_cases = [
        # 标准markdown代码块
        '```json\n{"test": "value"}\n```',
        # 带额外文本的markdown代码块
        'Here is the response:\n```json\n{"test": "value"}\n```\nThank you!',
        # 普通代码块
        '```\n{"test": "value"}\n```',
        # 纯JSON
        '{"test": "value"}',
        # 带前后文本的JSON
        'Response: {"test": "value"} End'
    ]
    
    print("Testing JSON cleaning function:")
    for i, test_case in enumerate(test_cases, 1):
        cleaned = clean_json_response(test_case)
        print(f"Test {i}: {cleaned}")

def list_available_models():
    """列出可用的Qwen模型"""
    config = get_qwen_config()
    print("Available Qwen Models:")
    for model, description in config["model_options"].items():
        marker = " (default)" if model == config["default_model"] else ""
        print(f"  - {model}: {description}{marker}")


if __name__ == "__main__":
    print("Qwen System Prompt Template Loaded Successfully!")
    print(f"Prompt length: {len(SYSTEM_PROMPT)} characters")
    print(f"Available test cases: {len(TEST_CASES)}")
    list_available_models()
    print("\n" + "="*50)
    test_json_cleaning()


