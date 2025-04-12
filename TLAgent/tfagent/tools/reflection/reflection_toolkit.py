from abc import ABC
from typing import List
from tfagent.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from tfagent.tools.reflection.universal_reflection import UniversalReflectionTool

from tfagent.types.key_type import ToolConfigKeyType

class FFheadsToolkit(BaseToolkit, ABC):
    name: str = "Reflection Toolkit"
    description: str = "Toolkit containing tools for intelligent reflection"

    def get_tools(self) -> List[BaseTool]:
        return [
            UniversalReflectionTool(),
        ]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return []
