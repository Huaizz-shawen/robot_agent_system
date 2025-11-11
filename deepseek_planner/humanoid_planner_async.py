# humanoid_planner_deepseek_async.py

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, AsyncGenerator
from humanoid_prompt_template import (
    get_humanoid_system_prompt,
    get_humanoid_test_cases,
    validate_response,
    clean_json_response
)
from deepseek_config import get_deepseek_config, list_available_presets

class HumanoidRobotPlannerDeepSeekAsync:
    """
    Unitree-G1 Humanoid Robot Planner - DeepSeek API Async Version
    支持异步调用和流式输出
    """

    def __init__(self, preset: str = "balanced", endpoint: str = "primary"):
        """
        初始化人形机器人规划器（DeepSeek异步版本）

        Args:
            preset: 参数预设 ('precise', 'balanced', 'creative', 'fast')
            endpoint: API端点选择 ('primary', 'backup')
        """
        # 获取配置
        self.config = get_deepseek_config(preset, endpoint)
        self.base_url = self.config["base_url"]
        self.model = self.config["model"]
        self.preset = preset
        
        # 设置请求头
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # 初始化session（将在async context中创建）
        self.session = None
        
        self.system_prompt = get_humanoid_system_prompt()
        print(f"✅ Initialized Async HumanoidRobotPlanner")
        print(f"   Model: {self.model}")
        print(f"   Preset: {preset}")
        print(f"   Endpoint: {self.base_url}")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()

    async def _make_api_request(self, messages: List[Dict], stream: bool = False) -> Dict:
        """
        异步发送API请求到DeepSeek服务

        Args:
            messages: 消息列表
            stream: 是否使用流式输出

        Returns:
            API响应
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        request_data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.config["max_tokens"],
            "temperature": self.config["temperature"],
            "top_p": self.config["top_p"],
            "presence_penalty": self.config["presence_penalty"],
            "frequency_penalty": self.config["frequency_penalty"],
            "stream": stream
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.config.get("timeout", 60))
            
            async with self.session.post(
                self.base_url,
                headers=self.headers,
                json=request_data,
                timeout=timeout
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API returned status {response.status}: {error_text}")
                
                if stream:
                    return response  # 返回响应对象用于流式处理
                else:
                    return await response.json()
                    
        except asyncio.TimeoutError:
            raise Exception("API request timeout")
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")

    async def _handle_stream_response(self, messages: List[Dict]) -> str:
        """
        处理流式响应
        
        Args:
            messages: 消息列表
            
        Returns:
            完整的响应文本
        """
        print("Streaming response:")
        full_response = ""
        
        try:
            response = await self._make_api_request(messages, stream=True)
            
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str == '[DONE]':
                        break
                    
                    try:
                        data = json.loads(data_str)
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                print(content, end='', flush=True)
                                full_response += content
                    except json.JSONDecodeError:
                        continue
            
            print("\n")
            return full_response
            
        except Exception as e:
            print(f"\n❌ Stream processing error: {str(e)}")
            return full_response if full_response else ""

    async def plan_task(self, human_request: str, return_raw: bool = False, 
                       stream: bool = False, debug: bool = False) -> Dict:
        """
        异步生成人形机器人任务执行计划

        Args:
            human_request: 人类的自然语言请求
            return_raw: 是否返回原始响应文本
            stream: 是否使用流式输出
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
                print(f"Sending async request to DeepSeek API...")
                print(f"Model: {self.model}")
                print(f"Preset: {self.preset}")
                print(f"Temperature: {self.config['temperature']}")
            
            # 调用DeepSeek API
            if stream:
                response_text = await self._handle_stream_response(messages)
            else:
                response = await self._make_api_request(messages, stream=False)
                
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
            return self._parse_response(response_text)
            
        except Exception as e:
            return {"error": f"API call failed: {str(e)}"}

    def _parse_response(self, response_text: str) -> Dict:
        """解析响应文本"""
        cleaned_text = clean_json_response(response_text)
        
        is_valid, message = validate_response(response_text)
        if not is_valid:
            print(f"Warning: {message}")
            try:
                return json.loads(cleaned_text)
            except json.JSONDecodeError:
                return {"error": message, "raw_response": response_text}
        
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {str(e)}")
            return {"error": f"JSON parsing failed: {str(e)}", "raw_response": response_text}

    async def batch_plan_tasks(self, requests: List[str], max_concurrent: int = 3) -> List[Dict]:
        """
        批量异步处理多个任务请求
        
        Args:
            requests: 任务请求列表
            max_concurrent: 最大并发数
            
        Returns:
            任务计划列表
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_limit(request: str, index: int) -> Dict:
            async with semaphore:
                print(f"Processing request {index + 1}/{len(requests)}: {request[:50]}...")
                result = await self.plan_task(request)
                return {"index": index, "request": request, "result": result}
        
        tasks = [process_with_limit(req, i) for i, req in enumerate(requests)]
        results = await asyncio.gather(*tasks)
        
        # 按原始顺序排序
        results.sort(key=lambda x: x['index'])
        return [r['result'] for r in results]

    async def run_tests_async(self, stream: bool = False):
        """异步运行测试用例"""
        test_cases = get_humanoid_test_cases()
        print(f"\n🧪 Running {len(test_cases)} test cases asynchronously")
        print(f"Model: {self.model}")
        print(f"Preset: {self.preset}")
        print("="*60)

        results = {"passed": 0, "failed": 0, "errors": 0}
        
        # 准备所有测试请求
        test_requests = [test['request'] for test in test_cases]
        
        # 批量处理
        if not stream:
            print("Running tests in batch mode...")
            plans = await self.batch_plan_tasks(test_requests, max_concurrent=3)
            
            for i, (test_case, plan) in enumerate(zip(test_cases, plans), 1):
                print(f"\n[Test {i}/{len(test_cases)}] {test_case['id']}")
                
                if "error" not in plan:
                    complexity = plan['task_analysis']['complexity']
                    expected = test_case['expected_complexity']
                    
                    if complexity == expected:
                        print(f"✅ PASSED - Complexity: {complexity}")
                        results["passed"] += 1
                    else:
                        print(f"⚠️  MISMATCH - Got: {complexity}, Expected: {expected}")
                        results["failed"] += 1
                else:
                    print(f"❌ ERROR: {plan['error']}")
                    results["errors"] += 1
        else:
            # 流式模式下逐个处理
            for i, test_case in enumerate(test_cases, 1):
                print(f"\n[Test {i}/{len(test_cases)}] {test_case['id']}")
                print(f"Request: {test_case['request']}")
                
                plan = await self.plan_task(test_case['request'], stream=True)
                
                if "error" not in plan:
                    complexity = plan['task_analysis']['complexity']
                    expected = test_case['expected_complexity']
                    
                    if complexity == expected:
                        print(f"✅ PASSED - Complexity: {complexity}")
                        results["passed"] += 1
                    else:
                        print(f"⚠️  MISMATCH - Got: {complexity}, Expected: {expected}")
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

    def execute_plan(self, plan: Dict):
        """执行计划（与同步版本相同）"""
        if "error" in plan:
            print(f"❌ Cannot execute plan due to error: {plan['error']}")
            if "raw_response" in plan:
                print(f"Raw response: {plan['raw_response'][:200]}...")
            return

        print("\n" + "="*60)
        print("🤖 HUMANOID ROBOT (Unitree-G1) - TASK EXECUTION")
        print("="*60)

        task_analysis = plan['task_analysis']
        print(f"📋 Task Intent: {task_analysis['intent']}")
        print(f"🏷️  Entities: {', '.join(task_analysis['entities'])}")
        print(f"⚡ Complexity: {task_analysis['complexity']}")
        print(f"⏱️  Estimated Duration: {task_analysis['estimated_duration']}")

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

        if plan.get('contingency_plans'):
            print(f"\n🚨 CONTINGENCY PLANS:")
            for i, contingency in enumerate(plan['contingency_plans'], 1):
                print(f"  {i}. If {contingency['failure_scenario']}")
                print(f"     → {contingency['alternative_action']}")

        print(f"\n💬 HUMANOID ROBOT FEEDBACK: {plan['human_feedback']}")
        print("="*60)

async def main():
    """异步主函数"""
    print("🤖 Humanoid Robot Planner - DeepSeek Async Edition")
    print("="*60)

    # 显示可用预设
    list_available_presets()
    
    # 让用户选择预设
    print("\nSelect a preset (or press Enter for 'balanced'):")
    preset_choice = input("Preset: ").strip().lower() or "balanced"
    
    async with HumanoidRobotPlannerDeepSeekAsync(preset=preset_choice) as planner:
        print(f"\n📋 Available Commands:")
        print("  - Type your request in natural language")
        print("  - 'test': Run test cases")
        print("  - 'test stream': Run tests with streaming")
        print("  - 'batch': Test batch processing")
        print("  - 'debug <request>': Run with debug output")
        print("  - 'presets': Show available presets")
        print("  - 'quit' or 'q': Exit")

        while True:
            user_input = input(f"\n🤖 DeepSeek [{preset_choice}] > ").strip()

            if user_input.lower() in ['quit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'test':
                await planner.run_tests_async()
            elif user_input.lower() == 'test stream':
                await planner.run_tests_async(stream=True)
            elif user_input.lower() == 'batch':
                test_requests = [
                    "帮我拿杯水",
                    "打扫客厅",
                    "找到我的手机"
                ]
                print(f"Testing batch processing with {len(test_requests)} requests...")
                results = await planner.batch_plan_tasks(test_requests)
                for i, result in enumerate(results, 1):
                    print(f"\nResult {i}:")
                    if "error" not in result:
                        print(f"  ✅ Success: {result['task_analysis']['intent']}")
                    else:
                        print(f"  ❌ Error: {result['error']}")
            elif user_input.lower() == 'presets':
                list_available_presets()
            elif user_input.lower().startswith('debug '):
                request = user_input[6:].strip()
                plan = await planner.plan_task(request, debug=True)
                planner.execute_plan(plan)
            elif user_input:
                use_stream = input("Use streaming? (y/N): ").lower().startswith('y')
                plan = await planner.plan_task(user_input, stream=use_stream)
                planner.execute_plan(plan)

if __name__ == "__main__":
    asyncio.run(main())