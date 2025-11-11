# deepseek_config.py

"""
DeepSeek API Configuration for Humanoid Robot Planner
"""

# DeepSeek API 端点配置
DEEPSEEK_API_CONFIG = {
    # 主要端点
    "primary": {
        "base_url": "http://dsv3.sii.edu.cn/v1/chat/completions",
        "model": "deepseek-v3-ep",
        "timeout": 300
    }
}

# DeepSeek 模型参数预设
DEEPSEEK_PRESETS = {
    # 精确模式 - 用于需要高准确性的任务
    "precise": {
        "temperature": 0.1,
        "top_p": 0.1,
        "max_tokens": 30000,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0
    },
    
    # 平衡模式 - 默认设置
    "balanced": {
        "temperature": 0.5,
        "top_p": 0.95,
        "max_tokens": 30000,
        "presence_penalty": 1.03,
        "frequency_penalty": 1.0
    },
    
    # 创造模式 - 用于需要创造性的任务
    "creative": {
        "temperature": 0.8,
        "top_p": 0.95,
        "max_tokens": 30000,
        "presence_penalty": 1.1,
        "frequency_penalty": 1.2
    },
    
    # 快速模式 - 用于简单任务，减少token使用
    "fast": {
        "temperature": 0.3,
        "top_p": 0.5,
        "max_tokens": 5000,
        "presence_penalty": 0.5,
        "frequency_penalty": 0.5
    }
}

def get_deepseek_config(preset_name="balanced", endpoint="primary"):
    """
    获取DeepSeek配置
    
    Args:
        preset_name: 预设名称 ('precise', 'balanced', 'creative', 'fast')
        endpoint: 端点选择 ('primary', 'backup')
    
    Returns:
        dict: 完整的配置字典
    """
    config = {}
    
    # 获取API端点配置
    if endpoint in DEEPSEEK_API_CONFIG:
        config.update(DEEPSEEK_API_CONFIG[endpoint])
    else:
        config.update(DEEPSEEK_API_CONFIG["primary"])
    
    # 获取参数预设
    if preset_name in DEEPSEEK_PRESETS:
        config.update(DEEPSEEK_PRESETS[preset_name])
    else:
        config.update(DEEPSEEK_PRESETS["precise"])
    
    return config

def list_available_presets():
    """列出所有可用的预设配置"""
    print("\n📋 Available DeepSeek Presets:")
    print("-" * 50)
    
    for name, settings in DEEPSEEK_PRESETS.items():
        print(f"\n🔧 {name.upper()}:")
        print(f"   Temperature: {settings['temperature']}")
        print(f"   Top-p: {settings['top_p']}")
        print(f"   Max Tokens: {settings['max_tokens']}")
        print(f"   Presence Penalty: {settings['presence_penalty']}")
        print(f"   Frequency Penalty: {settings['frequency_penalty']}")
    
    print("\n📡 Available Endpoints:")
    for name, settings in DEEPSEEK_API_CONFIG.items():
        print(f"   {name}: {settings['base_url']}")