from abc import ABC
from typing import Type, Optional, List

from pydantic import BaseModel, Field

from tfagent.agent.agent_prompt_builder import AgentPromptBuilder
from tfagent.helper.error_handler import ErrorHandler
from tfagent.helper.prompt_reader import PromptReader
from tfagent.lib.logger import logger
from tfagent.llms.base_llm import BaseLlm
from tfagent.models.agent_execution import AgentExecution
from tfagent.models.agent_execution_feed import AgentExecutionFeed
from tfagent.tools.base_tool import BaseTool
from tfagent.tools.tool_response_query_manager import ToolResponseQueryManager


class EvidFindingHeadSchema(BaseModel):
    pass
    # legal_text: str = Field(
    #     ...,
    #     description="The content of legal documents",
    # )


class EvidFindingHeadTool(BaseTool, ABC):
    """
    Evidence finding head tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
        llm: LLM used for thinking.
    """
    llm: Optional[BaseLlm] = None
    name = "EvidFindingHeadTool"
    description = (
        "Intelligent evidence finding assistant that comprehends the contents of the document, find out criminal evidence from given data only."
    )
    args_schema: Type[EvidFindingHeadSchema] = EvidFindingHeadSchema
    goals: List[str] = []
    agent_execution_id: int = None
    agent_id: int = None
    permission_required: bool = False
    tool_response_manager: Optional[ToolResponseQueryManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self,):
        """
        Execute the Evidence Finding Head tool.

        Args:
            legal_text : The content of legal documents

        Returns:
            A list of evidences found in legal document.
        """
        try:
            goals = AgentPromptBuilder.add_list_items_to_string(self.goals)
            prompt = PromptReader.read_tools_prompt(__file__, "evid_finding_head.txt")
            prompt = prompt.replace("{goals}", goals)
            #prompt = prompt.replace("{legal_text}", legal_text)
            last_tool_response = self.tool_response_manager.get_last_response()
            prompt = prompt.replace("{last_tool_response}", last_tool_response)
            metadata = {"agent_execution_id": self.agent_execution_id}
            relevant_tool_response = self.tool_response_manager.get_relevant_response(query=goals,
                                                                                      metadata=metadata)
            prompt = prompt.replace("{relevant_tool_response}", relevant_tool_response)
            messages = [{"role": "system", "content": prompt}]
            result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)

            if 'error' in result and result['message'] is not None:
                ErrorHandler.handle_openai_errors(self.toolkit_config.session, self.agent_id, self.agent_execution_id,
                                                  result['message'])
            return result["content"]
        except Exception as e:
            logger.error(e)
            return f"Error generating text: {e}"