from abc import ABC
from typing import List
from tfagent.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from tfagent.tools.multirolescheck.law_multirole_check import LawMultiRoleCheckTool

from tfagent.types.key_type import ToolConfigKeyType

class RoleCheckToolkit(BaseToolkit, ABC):
    name: str = "Role Check Toolkit"
    description: str = "Toolkit containing tools for intelligent multirole check"

    def get_tools(self) -> List[BaseTool]:
        return [
            LawMultiRoleCheckTool(),
        ]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return []
