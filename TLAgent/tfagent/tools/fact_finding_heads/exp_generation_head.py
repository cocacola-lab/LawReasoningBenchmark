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


class ExpGenerationHeadSchema(BaseModel):
    pass
    # fact: str = Field(
    #     ...,
    #     description="The content of criminal fact",
    # )
    #
    # evidence: str = Field(
    #     ...,
    #     description="The content of criminal evidence",
    # )


class ExpGenerationHeadTool(BaseTool, ABC):
    """
    Human Experience Generation Head Tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
        llm: LLM used to generate experience between evidence and fact
    """
    llm: Optional[BaseLlm] = None
    name = "ExpGenerationHeadTool"
    description = (
        "Intelligent criminal experience generator that can generate the human experience from evidence reasoning to facts."
    )
    args_schema: Type[ExpGenerationHeadSchema] = ExpGenerationHeadSchema
    goals: List[str] = []
    agent_execution_id: int = None
    agent_id: int = None
    permission_required: bool = False
    tool_response_manager: Optional[ToolResponseQueryManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, ):
        """
        Execute the Experience Generation Head Tool.

        Args:
            fact : The content of criminal fact
            evidence : The content of crimminal evidence

        Returns:
            the experience between evidence and fact.
        """
        try:
            prompt = PromptReader.read_tools_prompt(__file__, "exp_generation_head.txt")
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            # prompt = prompt.replace("{criminal_fact}", fact)
            # prompt = prompt.replace("{criminal_evidence}", evidence)
            last_tool_response = self.tool_response_manager.get_last_response()
            prompt = prompt.replace("{last_tool_response}", last_tool_response)
            metadata = {"agent_execution_id": self.agent_execution_id}

            # query_txt = fact + evidence
            # relevant_tool_response = self.tool_response_manager.get_relevant_response(query=query_txt,
            #                                                                           metadata=metadata)
            # prompt = prompt.replace("{relevant_tool_response}", relevant_tool_response)
            messages = [{"role": "system", "content": prompt}]
            result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)

            if 'error' in result and result['message'] is not None:
                ErrorHandler.handle_openai_errors(self.toolkit_config.session, self.agent_id, self.agent_execution_id,
                                                  result['message'])
            return result["content"]
        except Exception as e:
            logger.error(e)
            return f"Error generating text: {e}"