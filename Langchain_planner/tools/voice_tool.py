# tools/voice_tool.py
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import tempfile

class VoiceInput(BaseModel):
    """语音工具的输入schema"""
    message: str = Field(description="要通过语音说出的消息内容")
    listen: bool = Field(
        default=False, 
        description="是否需要等待用户语音输入。True表示需要听用户说话，False表示只播放消息"
    )

class VoiceInteractionTool(BaseTool):
    name = "voice_interaction"
    description = """
    用于与用户进行语音交互的工具。可以：
    1. 将文字转换为语音播放给用户
    2. 接收用户的语音输入并转换为文字
    
    输入参数：
    - message: 要说给用户听的内容
    - listen: 是否需要等待用户的语音回复 (True/False)
    
    使用场景：当需要语音播报信息或获取用户语音输入时使用。
    """
    args_schema: Type[BaseModel] = VoiceInput
    
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        pygame.mixer.init()
    
    def _text_to_speech(self, text: str, lang: str = 'zh-CN'):
        """文字转语音并播放"""
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
            
            # 生成语音
            tts = gTTS(text=text, lang=lang)
            tts.save(temp_file)
            
            # 播放语音
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # 等待播放完成
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # 清理临时文件
            os.unlink(temp_file)
            
            return True
        except Exception as e:
            return f"语音播放失败: {str(e)}"
    
    def _speech_to_text(self, timeout: int = 5) -> str:
        """语音转文字"""
        try:
            with sr.Microphone() as source:
                print("🎤 正在听取用户输入...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout)
                
                # 使用Google语音识别（支持中文）
                text = self.recognizer.recognize_google(audio, language='zh-CN')
                print(f"📝 识别结果: {text}")
                return text
        except sr.WaitTimeoutError:
            return "未检测到语音输入"
        except sr.UnknownValueError:
            return "无法识别语音内容"
        except Exception as e:
            return f"语音识别失败: {str(e)}"
    
    def _run(self, message: str, listen: bool = False) -> str:
        """执行语音交互"""
        result = []
        
        # 1. 播放消息给用户
        if message:
            tts_result = self._text_to_speech(message)
            if tts_result is True:
                result.append(f"✅ 已语音播放: {message}")
            else:
                result.append(f"❌ {tts_result}")
        
        # 2. 如果需要，监听用户输入
        if listen:
            user_input = self._speech_to_text()
            result.append(f"用户语音输入: {user_input}")
            return "\n".join(result) + f"\n用户说: {user_input}"
        
        return "\n".join(result)
    
    async def _arun(self, message: str, listen: bool = False) -> str:
        """异步执行"""
        raise NotImplementedError("暂不支持异步")