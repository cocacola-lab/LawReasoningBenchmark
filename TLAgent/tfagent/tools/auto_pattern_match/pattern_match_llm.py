import re
from abc import ABC
from typing import Type, Optional, List, Union

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


def is_list_string(s):
    """
    Check if the input string is a list of strings.

    Args:
        s: The input string.

    Returns:
        True if the input string is a list of strings, False otherwise.
    """
    return re.match(r"^\[.*\]$", s)


class PatternMatchLLMSchema(BaseModel):
    input_list: str = Field(
        ...,
        description="A list of strings from which the task target features and rules need to be extracted.",
    )


class PatternMatchLLMTool(BaseTool, ABC):
    """
    Pattern Match LLM tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
        llm: LLM used for emotion recognition.
    """
    llm: Optional[BaseLlm] = None
    name = "PatternMatchLLMTool"
    description = (
        "Intelligent Auto Pattern Match Tool that can automatically pre-analyze the required knowledge, rules "
        "and the text features that meet the goal according to the legal task goal."
    )
    args_schema: Type[PatternMatchLLMSchema] = PatternMatchLLMSchema
    goals: List[str] = []
    agent_execution_id: int = None
    agent_id: int = None
    permission_required: bool = False
    tool_response_manager: Optional[ToolResponseQueryManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, input_list:str):
        """
        Execute the pattern match tool.

        Args:
            input_txt : A list of strings that require pattern match.

        Returns:
            the match result.
        """
        try:
            last_tool_response = self.tool_response_manager.get_last_response()

            if last_tool_response != None and last_tool_response != "":
                input_list_str = last_tool_response.replace("Tool Response :", "")
            else:
                input_list_str = ""

            prompt = PromptReader.read_tools_prompt(__file__, "pattern_match.txt")
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            prompt = prompt.replace("{input_text}", input_list_str)

            messages = [{"role": "system", "content": prompt}]
            result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)

            if 'error' in result and result['message'] is not None:
                ErrorHandler.handle_openai_errors(self.toolkit_config.session, self.agent_id, self.agent_execution_id,
                                                  result['message'])
            # convert str to json
            return result["content"]
        except Exception as e:
            logger.error(e)
            return f"Error generating the pattern match result: {e}"