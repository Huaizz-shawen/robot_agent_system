# agents/main_agent.py
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from tools.rag_tool import RAGTool
from tools.voice_tool import VoiceInteractionTool

class MultiModalAgent:
    def __init__(self, documents_path: str, model_name: str = "gpt-4"):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.7
        )
        
        # 初始化工具
        self.rag_tool = RAGTool(documents_path, self.llm)
        self.voice_tool = VoiceInteractionTool()
        
        self.tools = [self.rag_tool, self.voice_tool]
        
        # 设置智能体
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    def _create_agent(self):
        """创建ReAct智能体"""
        template = """你是一个智能助手，可以查询知识库并进行语音交互。

你有以下工具可用：
{tools}

工具名称: {tool_names}

请按照以下格式回答：

Question: 用户的输入问题
Thought: 你应该思考需要做什么
Action: 要使用的工具名称，必须是 [{tool_names}] 中的一个
Action Input: 工具的输入参数
Observation: 工具执行的结果
... (这个 Thought/Action/Action Input/Observation 可以重复N次)
Thought: 我现在知道最终答案了
Final Answer: 对用户问题的最终回答

重要提示：
1. 当用户询问知识库相关问题时，使用 knowledge_base_search 工具
2. 当需要语音交互时，使用 voice_interaction 工具
3. 可以组合使用多个工具来完成复杂任务

开始！

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools]),
                "tool_names": ", ".join([tool.name for tool in self.tools])
            }
        )
        
        return create_react_agent(self.llm, self.tools, prompt)
    
    def run(self, query: str) -> str:
        """运行智能体"""
        result = self.agent_executor.invoke({"input": query})
        return result['output']