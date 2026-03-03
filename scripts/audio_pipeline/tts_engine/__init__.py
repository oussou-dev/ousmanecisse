from .gtts_engine import GTTSEngine
from .qwen_engine import QwenEngine

def get_engine(name, config):
    if name == "gtts":
        return GTTSEngine(config)
    elif name == "qwen":
        return QwenEngine(config)
    else:
        raise ValueError(f"Unknown TTS engine: {name}")
