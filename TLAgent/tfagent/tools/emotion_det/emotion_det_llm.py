import json
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
    # 正则表达式匹配类似列表的字符串，其中元素是字符串
    list_pattern = r'^\[\s*("[^"]*"(\s*,\s*"[^"]*")*)?\s*\]$'
    return bool(re.match(list_pattern, s))

class EmotionDetectionLLMSchema(BaseModel):
    input_list: Union[str, list] = Field(
        ...,
        description="A list of strings that require emotional recognition",
    )


class EmotionDetLLMTool(BaseTool, ABC):
    """
    Emotion Recognition tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
        llm: LLM used for emotion recognition.
    """
    llm: Optional[BaseLlm] = None
    name = "EmotionDetLLMTool"
    description = (
        "Intelligent Emotion Recognition that can call llm to identify the emotional tone of each string in the above list."
    )
    args_schema: Type[EmotionDetectionLLMSchema] = EmotionDetectionLLMSchema
    goals: List[str] = []
    agent_execution_id: int = None
    agent_id: int = None
    permission_required: bool = False
    tool_response_manager: Optional[ToolResponseQueryManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, input_list: Union[str, list]):
        """
        Execute the Emotion Recognition tool.

        Args:
            input_txt : A list of strings that require emotional recognition.

        Returns:
            the recognition result.
        """
        try:
            last_tool_response = self.tool_response_manager.get_last_response("UniversalReflectionTool")

            if last_tool_response != None and last_tool_response != "":
                input_list_str = last_tool_response.replace("Tool Response :", "")
            else:
                if isinstance(input_list, str):
                    if is_list_string(input_list):
                        input_list = eval(input_list)
                    else:
                        input_list = [input_list]

                input_list_str = str(input_list)

            prompt = PromptReader.read_tools_prompt(__file__, "emotion_det.txt")
            prompt = prompt.replace("{text_list}", input_list_str)

            messages = [{"role": "system", "content": prompt}]

            result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)

            if 'error' in result and result['message'] is not None:
                ErrorHandler.handle_openai_errors(self.toolkit_config.session, self.agent_id, self.agent_execution_id,
                                                  result['message'])
            # convert str to json
            result = json.loads(result["content"])
            response = ""
            for item in result["emotions"]:
                response += item["text"] + "\n" + "The emotion is " + item["type"] + "\n"
            return response
        except Exception as e:
            logger.error(e)
            return f"the emotion detection failed: {e}"