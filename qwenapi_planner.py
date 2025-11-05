# main.py

import os
import json
import re
from openai import OpenAI
from system_prompt_template import (
    SYSTEM_PROMPT, 
    get_qwen_config, 
    get_test_cases, 
    validate_response,
    clean_json_response,
    list_available_models
)

class QwenMultiAgentPlanner:
    def __init__(self, api_key=None, model_name=None):  # 确保参数正确
        """
        初始化基于Qwen的多智能体规划器
        
        Args:
            api_key: DASHSCOPE API密钥，如果不提供则从环境变量读取
            model_name: 指定使用的Qwen模型名称
        """
        # 获取API密钥
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not found. Please provide api_key parameter or set DASHSCOPE_API_KEY environment variable."
            )
        
        # 获取配置
        self.config = get_qwen_config(model_name)
        
        # 初始化OpenAI客户端（兼容Qwen API）
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.config["base_url"]
        )
        
        self.system_prompt = SYSTEM_PROMPT
        print(f"Initialized QwenMultiAgentPlanner with model: {self.config['model']}")
    
    def plan_task(self, human_request, return_raw=False, stream=False, debug=False):
        """
        根据人类请求生成任务执行计划
        
        Args:
            human_request: 人类的自然语言请求
            return_raw: 是否返回原始响应文本
            stream: 是否使用流式输出
            debug: 是否显示调试信息
            
        Returns:
            dict: 解析后的任务计划，或原始响应文本
        """
        try:
            # 构建请求参数
            request_params = {
                "model": self.config["model"],
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": human_request}
                ],
                "max_tokens": self.config["max_tokens"],
                "temperature": self.config["temperature"]
            }
            
            # 添加Qwen特有参数
            if not stream and "extra_body" in self.config:
                request_params["extra_body"] = self.config["extra_body"]
            
            # 调用API
            if stream:
                return self._handle_stream_response(request_params)
            else:
                response = self.client.chat.completions.create(**request_params)
                response_text = response.choices[0].message.content
            
            if debug:
                print(f"Raw API response:\n{response_text}\n{'='*50}")
            
            if return_raw:
                return response_text
            
            # 验证和解析响应
            return self._parse_response(response_text)
            
        except Exception as e:
            return {"error": f"API call failed: {str(e)}"}
    
    def _handle_stream_response(self, request_params):
        """处理流式响应"""
        request_params["stream"] = True
        response_text = ""
        
        try:
            stream = self.client.chat.completions.create(**request_params)
            print("Streaming response:")
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    response_text += content
            
            print("\n")  # 换行
            return self._parse_response(response_text)
            
        except Exception as e:
            return {"error": f"Stream processing failed: {str(e)}"}
    
    def _parse_response(self, response_text):
        """解析响应文本"""
        # 清理响应文本
        cleaned_text = clean_json_response(response_text)
        
        # 验证响应格式
        is_valid, message = validate_response(response_text)
        if not is_valid:
            print(f"Warning: {message}")
            print(f"Original response: {response_text[:200]}...")
            print(f"Cleaned response: {cleaned_text[:200]}...")
            
            # 尝试解析清理后的文本
            try:
                return json.loads(cleaned_text)
            except json.JSONDecodeError:
                return {"error": message, "raw_response": response_text}
        
        # 解析JSON响应
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed even after cleaning: {str(e)}")
            print(f"Cleaned text: {cleaned_text}")
            return {"error": f"JSON parsing failed: {str(e)}", "raw_response": response_text}
    
    def execute_plan(self, plan):
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
        
        print("\n" + "="*50)
        print("🤖 TASK EXECUTION SIMULATION")
        print("="*50)
        
        # 任务分析
        task_analysis = plan['task_analysis']
        print(f"📋 Task: {task_analysis['intent']}")
        print(f"🏷️  Entities: {', '.join(task_analysis['entities'])}")
        print(f"⚡ Complexity: {task_analysis['complexity']}")
        print(f"⏱️  Estimated Duration: {task_analysis['estimated_duration']}")
        
        # 执行步骤
        print(f"\n📝 EXECUTION PLAN ({len(plan['execution_plan'])} steps):")
        for i, step in enumerate(plan['execution_plan'], 1):
            print(f"\n  Step {step['step']}: 🤖 {step['agent']} @ 📍 {step['location']}")
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
        print(f"\n💬 FEEDBACK: {plan['human_feedback']}")
        print("="*50)
    
    def run_tests(self, stream=False):
        """运行测试用例"""
        test_cases = get_test_cases()
        print(f"\n🧪 Running {len(test_cases)} test cases with model: {self.config['model']}")
        print("="*60)
        
        results = {"passed": 0, "failed": 0, "errors": 0}
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[Test {i}/{len(test_cases)}] {test_case['id']}")
            print(f"Request: {test_case['request']}")
            
            plan = self.plan_task(test_case['request'], stream=stream)
            
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
        print(f"\n📊 TEST SUMMARY:")
        print(f"✅ Passed: {results['passed']}")
        print(f"⚠️  Failed: {results['failed']}")
        print(f"❌ Errors: {results['errors']}")
        total = sum(results.values())
        success_rate = (results['passed'] / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    def switch_model(self, model_name):
        """切换使用的模型"""
        old_model = self.config['model']
        self.config = get_qwen_config(model_name)
        print(f"Switched model from {old_model} to {self.config['model']}")

def main():
    """主函数示例"""
    print("🚀 Qwen Multi-Agent System Planner")
    print("="*50)
    
    # 检查API密钥
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("⚠️  Warning: DASHSCOPE_API_KEY environment variable not set.")
        print("Please set it using: export DASHSCOPE_API_KEY='your-api-key'")
        return
    
    try:
        # 初始化规划器
        planner = QwenMultiAgentPlanner()
        
        # 显示可用命令
        print(f"\n📋 Available Commands:")
        print("  - Type your request in natural language")
        print("  - 'test' or 't': Run test cases")
        print("  - 'test stream' or 'ts': Run test cases with streaming")
        print("  - 'debug <request>': Run with debug output")
        print("  - 'models' or 'm': List available models")
        print("  - 'switch <model_name>': Switch to different model")
        print("  - 'quit' or 'q': Exit")
        
        # 交互式模式
        while True:
            user_input = input(f"\n🤖 [{planner.config['model']}] > ").strip()
            
            if user_input.lower() in ['quit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() in ['test', 't']:
                planner.run_tests()
            elif user_input.lower() in ['test stream', 'ts']:
                planner.run_tests(stream=True)
            elif user_input.lower() in ['models', 'm']:
                list_available_models()
            elif user_input.lower().startswith('switch '):
                model_name = user_input[7:].strip()
                planner.switch_model(model_name)
            elif user_input.lower().startswith('debug '):
                request = user_input[6:].strip()
                plan = planner.plan_task(request, debug=True)
                planner.execute_plan(plan)
            elif user_input:
                # 询问是否使用流式输出
                use_stream = input("Use streaming output? (y/N): ").lower().startswith('y')
                plan = planner.plan_task(user_input, stream=use_stream)
                planner.execute_plan(plan)
            
    except Exception as e:
        print(f"❌ Initialization failed: {str(e)}")

if __name__ == "__main__":
    main()