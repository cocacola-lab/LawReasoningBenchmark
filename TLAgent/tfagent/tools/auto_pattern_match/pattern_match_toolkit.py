from abc import ABC
from typing import List
from tfagent.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from tfagent.tools.auto_pattern_match.pattern_match_llm import PatternMatchLLMTool

from tfagent.types.key_type import ToolConfigKeyType

class EmotionToolkit(BaseToolkit, ABC):
    name: str = "Pattern Match Toolkit"
    description: str = "Toolkit containing tools for intelligent auto pattern match"

    def get_tools(self) -> List[BaseTool]:
        return [
            PatternMatchLLMTool(),
        ]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return []
