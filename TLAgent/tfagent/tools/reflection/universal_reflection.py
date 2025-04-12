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


class UniversalReflectionSchema(BaseModel):
    pass
    # input_txt: str = Field(
    #     ...,
    #     description="Text that needs to be reflection by llm",
    # )


class  UniversalReflectionTool(BaseTool, ABC):
    """
    Final decision head tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
        llm: LLM used for thinking.
    """
    llm: Optional[BaseLlm] = None
    name = "UniversalReflectionTool"
    description = (
        "Intelligent Reflection assistant that reflect on the accuracy of the responses from the LLM "
        "based on relevant knowledge. If the responses are inaccurate, they need to be revised and"
        "accurate response should be returned."
    )
    args_schema: Type[UniversalReflectionSchema] = UniversalReflectionSchema
    goals: List[str] = []
    agent_execution_id: int = None
    agent_id: int = None
    permission_required: bool = False
    tool_response_manager: Optional[ToolResponseQueryManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, ):
        """
        Execute the Fact Finding Head tool.

        Args:
            input_txt : Text that needs to be reflection by llm.

        Returns:
            the reflection result.
        """
        try:
            last_reflection_response = self.tool_response_manager.get_last_response("UniversalReflectionTool")
            # input_txt = self.tool_response_manager.get_last_response()
            input_txt = ""
            last_tool_response = self.tool_response_manager.get_last_response()
            if last_reflection_response and last_reflection_response != "":
                input_txt = last_reflection_response
            elif last_tool_response and last_tool_response != "":
                input_txt = last_tool_response
                last_tool_response = ""

            # 更鲁邦，当中间的工具出现错误时，直接返回第一个工具response
            if "error" in input_txt or "Error" in input_txt:
                first_tool_response = self.tool_response_manager.get_first_response()
                input_txt = first_tool_response

            prompt = PromptReader.read_tools_prompt(__file__, "reflection.txt")
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            prompt = prompt.replace("{input_text}", input_txt)
            prompt = prompt.replace("{last_tool_response}", last_tool_response)

            # metadata = {"agent_execution_id": self.agent_execution_id}
            # relevant_tool_response = self.tool_response_manager.get_relevant_response(query=legal_text,
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
            return f"Error generating the reflection text: {e}"