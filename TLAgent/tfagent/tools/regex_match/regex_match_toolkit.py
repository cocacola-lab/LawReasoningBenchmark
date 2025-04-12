from abc import ABC
from typing import List
from tfagent.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from tfagent.tools.regex_match.fact_finding import FactFinding
from tfagent.tools.regex_match.evid_finding import EvidFinding
from tfagent.types.key_type import ToolConfigKeyType


class ThinkingToolkit(BaseToolkit, ABC):
    name: str = "Regex Match Toolkit"
    description: str = "Extract evidence or facts from the text through regex matching."

    def get_tools(self) -> List[BaseTool]:
        return [
            FactFinding(), EvidFinding()
        ]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return []
