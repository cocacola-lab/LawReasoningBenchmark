from abc import ABC
from typing import List

from tfagent.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from tfagent.tools.domain_knowledge.fact_knowledge_search import FactKnowledgeTool
from tfagent.tools.domain_knowledge.final_knowledge_search import FinalKnowledgeTool
from tfagent.tools.domain_knowledge.evid_knowledge_search import EvidKnowledgeTool


class LegalKnowledgeToolkit(BaseToolkit, ABC):
    name: str = "Legal Knowledge Toolkit"
    description: str = "Legal Knowledge Toolkit contains all tools related to Legal Knowledge DB"

    def get_tools(self) -> List[BaseTool]:
        return [FactKnowledgeTool(), FinalKnowledgeTool(), EvidKnowledgeTool()]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return []
