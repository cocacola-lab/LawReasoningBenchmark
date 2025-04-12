from abc import ABC
from typing import List
from tfagent.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from tfagent.tools.knowledge_search.knowledge_search import KnowledgeSearchTool
from tfagent.tools.knowledge_search.knowledge_search_fact import FactKnowledgeSearchTool
from tfagent.tools.knowledge_search.knowledge_search_evid import EvidKnowledgeSearchTool
from tfagent.types.key_type import ToolConfigKeyType

class KnowledgeSearchToolkit(BaseToolkit, ABC):
    name: str = "Knowledge Search Toolkit"
    description: str = "Toolkit containing tools for performing search on the knowledge base."

    def get_tools(self) -> List[BaseTool]:
        return [KnowledgeSearchTool(), FactKnowledgeSearchTool(), EvidKnowledgeSearchTool()]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return [
            ToolConfiguration(key="OPENAI_API_KEY", key_type=ToolConfigKeyType.STRING, is_required=False, is_secret=True)
        ]