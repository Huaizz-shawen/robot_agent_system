# tools/rag_tool.py
from langchain.tools import BaseTool
from langchain.vectorstores import Chroma  # 或 FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from typing import Optional, Type
from pydantic import BaseModel, Field

class RAGInput(BaseModel):
    """RAG工具的输入schema"""
    query: str = Field(description="用户想要查询的问题")

class RAGTool(BaseTool):
    name = "knowledge_base_search"
    description = """
    当用户询问关于特定文档或知识库的问题时使用此工具。
    输入应该是一个完整的问题。
    这个工具会在知识库中搜索相关信息并返回答案。
    """
    args_schema: Type[BaseModel] = RAGInput
    
    def __init__(self, documents_path: str, llm):
        super().__init__()
        self.llm = llm
        self.vectorstore = self._setup_vectorstore(documents_path)
        self.qa_chain = self._setup_qa_chain()
    
    def _setup_vectorstore(self, documents_path: str):
        """设置向量存储"""
        # 加载文档
        from langchain.document_loaders import TextLoader
        loader = TextLoader(documents_path, encoding='utf-8')
        documents = loader.load()
        
        # 分割文档
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?"]
        )
        splits = text_splitter.split_documents(documents)
        
        # 创建向量存储
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory="./chroma_db"
        )
        return vectorstore
    
    def _setup_qa_chain(self):
        """设置问答链"""
        retriever = self.vectorstore.as_retriever(
            search_type="mmr",  # 最大边际相关性
            search_kwargs={"k": 3}
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",  # 或 "map_reduce", "refine"
            retriever=retriever,
            return_source_documents=True
        )
        return qa_chain
    
    def _run(self, query: str) -> str:
        """执行RAG查询"""
        result = self.qa_chain({"query": query})
        answer = result['result']
        sources = result.get('source_documents', [])
        
        # 可选：添加来源信息
        if sources:
            answer += f"\n\n参考来源: {len(sources)}个文档片段"
        
        return answer
    
    async def _arun(self, query: str) -> str:
        """异步执行（如需要）"""
        raise NotImplementedError("暂不支持异步")