# humanoid_planner_deepseek.py

import os
import json
import sys
import requests
from typing import Dict, List, Optional, Any

# 添加父目录到路径（如果需要从子目录导入）
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from humanoid_prompt_template import (
    get_humanoid_system_prompt,
    get_humanoid_test_cases
)
from json_tool.json_parser_enhanced import (
    clean_json_response_enhanced,
    parse_json_with_fallback,
    validate_robot_response
)

class HumanoidRobotPlannerDeepSeek:
    """
    Unitree-G1 Humanoid Robot Planner - DeepSeek API Version
    Specialized for home environment control and item retrieval coordination
    """

    def __init__(self, base_url: str = None, model_name: str = None):
        """
        初始化人形机器人规划器（DeepSeek版本）

        Args:
            base_url: DeepSeek API的基础URL
            model_name: 指定使用的DeepSeek模型名称
        """
        # 设置API配置
        self.base_url = base_url or "http://dsv3.sii.edu.cn/v1/chat/completions"
        self.model = model_name or "deepseek-v3-ep"
        
        # DeepSeek API配置参数
        self.config = {
            "model": self.model,
            "max_tokens": 2000,
            "temperature": 0.7,
            "top_p": 0.95,
            "presence_penalty": 1.03,
            "frequency_penalty": 1.0,
            "stream": False
        }
        
        # 设置请求头
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        self.system_prompt = get_humanoid_system_prompt()
        print(f"✅ Initialized HumanoidRobotPlanner with DeepSeek model: {self.model}")
        print(f"   API endpoint: {self.base_url}")

    def _make_api_request(self, messages: List[Dict], stream: bool = False) -> Dict:
        """
        发送API请求到DeepSeek服务

        Args:
            messages: 消息列表
            stream: 是否使用流式输出

        Returns:
            API响应
        """
        request_data = {
            "model": self.config["model"],
            "messages": messages,
            "max_tokens": self.config["max_tokens"],
            "temperature": self.config["temperature"],
            "top_p": self.config["top_p"],
            "presence_penalty": self.config["presence_penalty"],
            "frequency_penalty": self.config["frequency_penalty"],
            "stream": stream
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=request_data,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def plan_task(self, human_request: str, return_raw: bool = False, 
                  stream: bool = False, debug: bool = False) -> Dict:
        """
        根据人类请求生成人形机器人任务执行计划

        Args:
            human_request: 人类的自然语言请求
            return_raw: 是否返回原始响应文本
            stream: 是否使用流式输出（DeepSeek版本暂不支持流式）
            debug: 是否显示调试信息

        Returns:
            dict: 解析后的任务计划，或原始响应文本
        """
        try:
            # 构建消息
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": human_request}
            ]
            
            if debug:
                print(f"Sending request to DeepSeek API...")
                print(f"Model: {self.config['model']}")
                print(f"Temperature: {self.config['temperature']}")
            
            # 调用DeepSeek API
            if stream:
                print("⚠️ Stream mode is not fully implemented for DeepSeek API yet")
                # 降级为非流式处理
                response = self._make_api_request(messages, stream=False)
            else:
                response = self._make_api_request(messages, stream=False)
            
            # 提取响应内容
            if 'choices' in response and len(response['choices']) > 0:
                response_text = response['choices'][0]['message']['content']
            else:
                raise Exception("Invalid API response format")
            
            if debug:
                print(f"Raw API response:\n{response_text}\n{'='*50}")
            
            if return_raw:
                return response_text
            
            # 验证和解析响应
            return self._parse_response(response_text, debug=debug)
            
        except Exception as e:
            return {"error": f"API call failed: {str(e)}"}

    def _parse_response(self, response_text: str, debug: bool = False) -> Dict:
        """解析响应文本"""
        # 使用增强的JSON解析
        result, success = parse_json_with_fallback(response_text, debug=debug)
        
        if success:
            # 验证响应结构
            is_valid, message = validate_robot_response(result)
            if not is_valid:
                print(f"Warning: Response structure issue - {message}")
                # 即使结构不完整，也尝试返回部分结果
                if "task_analysis" in result:
                    return result
                else:
                    return {"error": message, "raw_response": response_text[:500]}
            return result
        else:
            return result  # 返回带错误信息的结果

    def execute_plan(self, plan: Dict):
        """
        执行生成的任务计划（模拟实现）

        Args:
            plan: plan_task()返回的任务计划
        """
        if "error" in plan:
            print(f"❌ Cannot execute plan due to error: {plan['error']}")
            if "raw_response" in plan:
                print(f"Raw response: {plan['raw_response'][:200]}...")
            return

        print("\n" + "="*60)
        print("🤖 HUMANOID ROBOT (Unitree-G1) - TASK EXECUTION")
        print("="*60)

        # 任务分析
        task_analysis = plan['task_analysis']
        print(f"📋 Task Intent: {task_analysis['intent']}")
        print(f"🏷️  Entities: {', '.join(task_analysis['entities'])}")
        print(f"⚡ Complexity: {task_analysis['complexity']}")
        print(f"⏱️  Estimated Duration: {task_analysis['estimated_duration']}")

        # 执行步骤
        print(f"\n📝 EXECUTION PLAN ({len(plan['execution_plan'])} steps):")
        for step in plan['execution_plan']:
            print(f"\n  Step {step['step']}: 🤖 {step['agent']}")
            print(f"    📍 Location: {step['location']}")
            print(f"    🎯 Action: {step['action']}")
            if step.get('parameters'):
                print(f"    ⚙️  Parameters: {step['parameters']}")
            if step.get('dependencies'):
                print(f"    🔗 Dependencies: Step {', '.join(map(str, step['dependencies']))}")
            print(f"    ✅ Success Criteria: {step['success_criteria']}")

        # 应急预案
        if plan.get('contingency_plans'):
            print(f"\n🚨 CONTINGENCY PLANS:")
            for i, contingency in enumerate(plan['contingency_plans'], 1):
                print(f"  {i}. If {contingency['failure_scenario']}")
                print(f"     → {contingency['alternative_action']}")

        # 人机反馈
        print(f"\n💬 HUMANOID ROBOT FEEDBACK: {plan['human_feedback']}")
        print("="*60)

    def run_tests(self):
        """运行人形机器人专用测试用例"""
        test_cases = get_humanoid_test_cases()
        print(f"\n🧪 Running {len(test_cases)} humanoid robot test cases")
        print(f"Model: {self.config['model']}")
        print(f"API: {self.base_url}")
        print("="*60)

        results = {"passed": 0, "failed": 0, "errors": 0}

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[Test {i}/{len(test_cases)}] {test_case['id']}")
            print(f"Request: {test_case['request']}")

            plan = self.plan_task(test_case['request'])

            if "error" not in plan:
                complexity = plan['task_analysis']['complexity']
                expected = test_case['expected_complexity']

                if complexity == expected:
                    print(f"✅ PASSED - Complexity: {complexity}")
                    results["passed"] += 1
                else:
                    print(f"⚠️  COMPLEXITY MISMATCH - Got: {complexity}, Expected: {expected}")
                    results["failed"] += 1
            else:
                print(f"❌ ERROR: {plan['error']}")
                results["errors"] += 1

        # 测试结果总结
        print(f"\n📊 HUMANOID ROBOT TEST SUMMARY:")
        print(f"✅ Passed: {results['passed']}")
        print(f"⚠️  Failed: {results['failed']}")
        print(f"❌ Errors: {results['errors']}")
        total = sum(results.values())
        success_rate = (results['passed'] / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")

    def update_config(self, **kwargs):
        """
        更新配置参数
        
        Args:
            **kwargs: 要更新的配置参数
        """
        valid_params = ['temperature', 'max_tokens', 'top_p', 
                       'presence_penalty', 'frequency_penalty']
        
        for key, value in kwargs.items():
            if key in valid_params:
                self.config[key] = value
                print(f"Updated {key} to {value}")
            else:
                print(f"Warning: {key} is not a valid configuration parameter")

    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            print(f"Testing connection to {self.base_url}...")
            response = self._make_api_request([
                {"role": "user", "content": "Hello"}
            ])
            if 'choices' in response:
                print("✅ Connection successful!")
                return True
            else:
                print("❌ Connection failed: Invalid response format")
                return False
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False

def main():
    """主函数示例"""
    print("🤖 Humanoid Robot (Unitree-G1) Task Planner - DeepSeek Edition")
    print("="*60)

    try:
        # 初始化规划器
        planner = HumanoidRobotPlannerDeepSeek()
        
        # 测试连接
        if not planner.test_connection():
            print("⚠️  Warning: Could not connect to DeepSeek API")
            print("Please check your network connection and API endpoint")
            return

        # 显示可用命令
        print(f"\n📋 Available Commands:")
        print("  - Type your request in natural language")
        print("  - 'test' or 't': Run test cases")
        print("  - 'debug <request>': Run with debug output")
        print("  - 'config': Show current configuration")
        print("  - 'set <param> <value>': Update configuration parameter")
        print("  - 'quit' or 'q': Exit")

        # 交互式模式
        while True:
            user_input = input(f"\n🤖 Humanoid [DeepSeek {planner.model}] > ").strip()

            if user_input.lower() in ['quit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() in ['test', 't']:
                planner.run_tests()
            elif user_input.lower() == 'config':
                print("Current configuration:")
                for key, value in planner.config.items():
                    print(f"  {key}: {value}")
            elif user_input.lower().startswith('set '):
                parts = user_input.split()
                if len(parts) >= 3:
                    param = parts[1]
                    value = parts[2]
                    # 尝试转换为数字
                    try:
                        value = float(value) if '.' in value else int(value)
                    except ValueError:
                        pass
                    planner.update_config(**{param: value})
                else:
                    print("Usage: set <param> <value>")
            elif user_input.lower().startswith('debug '):
                request = user_input[6:].strip()
                plan = planner.plan_task(request, debug=True)
                planner.execute_plan(plan)
            elif user_input:
                plan = planner.plan_task(user_input)
                planner.execute_plan(plan)

    except Exception as e:
        print(f"❌ Initialization failed: {str(e)}")

if __name__ == "__main__":
    main()