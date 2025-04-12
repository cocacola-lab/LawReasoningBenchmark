from abc import ABC
from typing import List

from tfagent.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from tfagent.tools.json_tool.load_json_txt import LoadJsonTxtTool
from tfagent.tools.json_tool.read_value_from_item import ReadValFromJsonItem

class JsonToolkit(BaseToolkit, ABC):
    name: str = "Json Toolkit"
    description: str = "Json Toolkit contains all tools related to json operations"

    def get_tools(self) -> List[BaseTool]:
        return [LoadJsonTxtTool(), ReadValFromJsonItem()]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return []
