# json_parser_enhanced.py

import json
import re
from typing import Dict, Any, Tuple

def clean_json_response_enhanced(response_text: str) -> str:
    """
    增强的JSON响应清理函数
    处理各种常见的JSON格式问题
    
    Args:
        response_text: 原始响应文本
        
    Returns:
        清理后的JSON字符串，如果无法提取有效部分则返回空字符串
    """
    # 保存原始文本用于调试
    original = response_text
    
    # --- MODIFIED SECTION 1: 更健壮的JSON内容提取 ---
    # 首先，尝试匹配被Markdown代码块包裹的JSON
    match = re.search(r'```(?:json)?\s*(\{[\s\S]*\})\s*```', response_text, re.MULTILINE)
    if match:
        response_text = match.group(1)
    else:
        # 如果没有找到Markdown块，则回退到查找第一个 '{' 和最后一个 '}'
        # 这种方法可以处理JSON前后有无关文本的情况
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            response_text = response_text[start_idx:end_idx+1]
        else:
            # 如果连基本的JSON结构都找不到，可能响应完全无效
            return "" # 返回空字符串以避免后续处理出错

    # 3. 修复常见的JSON格式问题
    
    # 3.1 移除行尾的逗号（在 } 或 ] 之前）
    response_text = re.sub(r',\s*([\}\]])', r'\1', response_text)
    
    # 3.2 修复缺失的逗号（在值后面跟着引号的情况）
    # 注意: 这组规则比较激进，如果遇到复杂结构可能误判，但对修复LLM的常见错误有帮助
    response_text = re.sub(r'("\s*:\s*"[^"]*")\s*\n?\s*(")', r'\1,\2', response_text)
    response_text = re.sub(r'("\s*:\s*\d+)\s*\n?\s*(")', r'\1,\2', response_text)
    response_text = re.sub(r'("\s*:\s*true)\s*\n?\s*(")', r'\1,\2', response_text)
    response_text = re.sub(r'("\s*:\s*false)\s*\n?\s*(")', r'\1,\2', response_text)
    response_text = re.sub(r'("\s*:\s*null)\s*\n?\s*(")', r'\1,\2', response_text)
    response_text = re.sub(r'(})\s*\n?\s*(")', r'\1,\2', response_text)
    response_text = re.sub(r'(\])\s*\n?\s*(")', r'\1,\2', response_text)
    
    # 3.3 修复属性名没有引号的问题
    # 匹配形如 key: value 的模式，给key加上引号
    response_text = re.sub(r'([,\{\s])([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', response_text)
    
    # --- MODIFIED SECTION 2: 修复单引号问题 (解决了 re.error) ---
    # 移除了会导致 "look-behind requires fixed-width pattern" 错误的正则表达式
    # 采用更安全、不使用 look-behind 的方式进行替换

    # 3.4.1 将用单引号包裹的键替换为双引号
    response_text = re.sub(r"([\{,]\s*)'([^']*)'(\s*:)", r'\1"\2"\3', response_text)
    
    # 3.4.2 将用单引号包裹的值替换为双引号
    # 这个表达式匹配一个冒号，后面跟着可选的空格和单引号值
    # 这样做可以避免错误地替换字符串内部的撇号 (e.g., "it's a bug")
    response_text = re.sub(r"(:)(\s*)'([^']*)'", r'\1\2"\3"', response_text)

    # 3.5 处理 Python 风格的 True/False/None
    response_text = re.sub(r'\bTrue\b', 'true', response_text)
    response_text = re.sub(r'\bFalse\b', 'false', response_text)
    response_text = re.sub(r'\bNone\b', 'null', response_text)
    
    # 3.6 移除注释（JSON不支持注释）
    # 移除 // 风格的注释
    response_text = re.sub(r'//.*$', '', response_text, flags=re.MULTILINE)
    # 移除 /* */ 风格的注释
    response_text = re.sub(r'/\*.*?\*/', '', response_text, flags=re.DOTALL)
    
    # --- REMOVED SECTION: 移除了危险的空白字符处理 ---
    # 原有的 3.7 节会破坏字符串值内部的空格，已被移除。
    # JSON解析器本身可以处理合法的多余空白。
    
    return response_text.strip()

def parse_json_with_fallback(response_text: str, debug: bool = False) -> Tuple[Dict, bool]:
    """
    尝试解析JSON，如果失败则使用多种策略修复
    
    Args:
        response_text: 响应文本
        debug: 是否打印调试信息
        
    Returns:
        (解析结果, 是否成功)
    """
    last_exception = None
    # 策略1：直接解析
    try:
        # 首先尝试直接从原始文本中提取 markdown json, 因为有些原始文本可能本身就是合法的json
        match = re.search(r'```(?:json)?\s*(\{[\s\S]*\})\s*```', response_text, re.MULTILINE)
        if match:
            json_str = match.group(1)
        else:
            json_str = response_text
            
        result = json.loads(json_str)
        if debug:
            print("✅ 策略1：直接解析成功")
        return result, True
    except json.JSONDecodeError as e:
        if debug:
            print(f"❌ 策略1失败: {e}")
        last_exception = e

    # 策略2：使用增强清理
    try:
        cleaned = clean_json_response_enhanced(response_text)
        if not cleaned: # 如果清理函数返回空，说明没找到可解析内容
             raise json.JSONDecodeError("无法从响应中提取有效的JSON内容", response_text, 0)
        result = json.loads(cleaned)
        if debug:
            print("✅ 策略2：清理后解析成功")
            print("🔧 清理后的JSON内容:\n", cleaned)
        return result, True
    except json.JSONDecodeError as e:
        if debug:
            print(f"❌ 策略2失败: {e}")
            # print("🔧 清理后失败的内容:\n", cleaned) # 取消注释以进行深度调试
        last_exception = e

    # 策略3：尝试修复具体的错误 (基于最后一次的异常)
    # ... (此部分逻辑可以根据需要进一步实现)
    
    # 策略4：使用正则表达式提取关键信息构建JSON
    try:
        result = extract_json_structure(response_text)
        if result:
            if debug:
                print("✅ 策略4：正则提取成功")
            return result, True
    except Exception as e:
        if debug:
            print(f"❌ 策略4失败: {e}")
    
    # 策略5：返回一个基础结构，包含原始响应
    if debug:
        print("⚠️ 所有策略失败，返回基础结构")
    
    return {
        "error": "JSON parsing failed",
        "last_known_error": str(last_exception),
        "raw_response": response_text[:500],
        "task_analysis": {
            "intent": "unknown",
            "entities": [],
            "complexity": "unknown",
            "estimated_duration": "unknown"
        },
        "execution_plan": [],
        "contingency_plans": [],
        "human_feedback": "Unable to parse response"
    }, False

# 以下函数 (extract_json_structure, validate_robot_response) 保持不变
def extract_json_structure(text: str) -> Dict[str, Any]:
    """
    从文本中提取JSON结构的关键信息
    
    Args:
        text: 输入文本
        
    Returns:
        提取的JSON结构
    """
    result = {
        "task_analysis": {},
        "execution_plan": [],
        "contingency_plans": [],
        "human_feedback": ""
    }
    
    # 提取 task_analysis
    intent_match = re.search(r'"intent"\s*:\s*"([^"]*)"', text)
    if intent_match:
        result["task_analysis"]["intent"] = intent_match.group(1)
    
    entities_match = re.search(r'"entities"\s*:\s*\[([^\]]*)\]', text)
    if entities_match:
        entities_str = entities_match.group(1)
        entities = re.findall(r'"([^"]*)"', entities_str)
        result["task_analysis"]["entities"] = entities
    
    complexity_match = re.search(r'"complexity"\s*:\s*"([^"]*)"', text)
    if complexity_match:
        result["task_analysis"]["complexity"] = complexity_match.group(1)
    
    duration_match = re.search(r'"estimated_duration"\s*:\s*"([^"]*)"', text)
    if duration_match:
        result["task_analysis"]["estimated_duration"] = duration_match.group(1)
    
    # 提取 execution_plan (简化版)
    step_matches = re.finditer(r'"step"\s*:\s*(\d+)', text)
    for match in step_matches:
        step_num = int(match.group(1))
        # 尝试找到相关的动作信息
        action_match = re.search(rf'"step"\s*:\s*{step_num}.*?"action"\s*:\s*"([^"]*)"', text, re.DOTALL)
        if action_match:
            result["execution_plan"].append({
                "step": step_num,
                "action": action_match.group(1),
                "agent": "humanoid_robot",
                "location": "unknown",
                "success_criteria": "unknown"
            })
    
    # 提取 human_feedback
    feedback_match = re.search(r'"human_feedback"\s*:\s*"([^"]*)"', text)
    if feedback_match:
        result["human_feedback"] = feedback_match.group(1)
    
    return result if result["task_analysis"] else None

def validate_robot_response(response: Dict) -> Tuple[bool, str]:
    """
    验证机器人响应的结构是否完整
    
    Args:
        response: 解析后的响应字典
        
    Returns:
        (是否有效, 错误信息)
    """
    required_fields = ["task_analysis", "execution_plan", "human_feedback"]
    missing_fields = []
    
    for field in required_fields:
        if field not in response:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    # 验证 task_analysis 结构
    task_fields = ["intent", "entities", "complexity", "estimated_duration"]
    if "task_analysis" in response:
        missing_task_fields = []
        for field in task_fields:
            if field not in response["task_analysis"]:
                missing_task_fields.append(field)
        if missing_task_fields:
            return False, f"Missing task_analysis fields: {', '.join(missing_task_fields)}"
    
    # 验证 execution_plan 是列表
    if not isinstance(response.get("execution_plan"), list):
        return False, "execution_plan must be a list"
    
    return True, "Valid response structure"