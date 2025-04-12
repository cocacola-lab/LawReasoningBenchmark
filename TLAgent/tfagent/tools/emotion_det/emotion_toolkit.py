from abc import ABC
from typing import List
from tfagent.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from tfagent.tools.emotion_det.emotion_det_llm import EmotionDetLLMTool

from tfagent.types.key_type import ToolConfigKeyType

class EmotionToolkit(BaseToolkit, ABC):
    name: str = "Emotion Toolkit"
    description: str = "Toolkit containing tools for intelligent emotion recognition"

    def get_tools(self) -> List[BaseTool]:
        return [
            EmotionDetLLMTool(),
        ]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return []
