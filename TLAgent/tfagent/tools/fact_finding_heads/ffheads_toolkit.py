from abc import ABC
from typing import List
from tfagent.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from tfagent.tools.fact_finding_heads.fact_finding_head import FactFindingHeadTool
from tfagent.tools.fact_finding_heads.evid_finding_head import EvidFindingHeadTool
from tfagent.tools.fact_finding_heads.criminal_relation_head import CriminalRelationHeadTool
from tfagent.tools.fact_finding_heads.exp_generation_head import ExpGenerationHeadTool
from tfagent.tools.fact_finding_heads.final_decision_head import FinalDecisionHeadTool
from tfagent.types.key_type import ToolConfigKeyType

class FFheadsToolkit(BaseToolkit, ABC):
    name: str = "Fact Finding Heads Toolkit"
    description: str = "Toolkit containing tools for intelligent judicial analysis"

    def get_tools(self) -> List[BaseTool]:
        return [
            FactFindingHeadTool(),
            EvidFindingHeadTool(),
            CriminalRelationHeadTool(),
            ExpGenerationHeadTool(),
            FinalDecisionHeadTool(),
        ]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return []
