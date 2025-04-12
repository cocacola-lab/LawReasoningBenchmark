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

class LawMultiRoleCheckToolSchema(BaseModel):
    text: str = Field(
        ...,
        description="The content about discussion topic",
    )

    # text: str = Field(
    #     ...,
    #     description="The text that needs to be discussed",
    # )

    # issue: str = Field(
    #     ...,
    #     description="The topic about discussion",
    # )



class LawMultiRoleCheckTool(BaseTool, ABC):
    """
    MultiRole Check Tool for Law

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
        llm: LLM used to determine whether there is a relation between evidence and fact
    """
    llm: Optional[BaseLlm] = None
    name = "LawMultiRoleCheckTool"
    description = (
        "Intelligent multirole check assistant that can understand the meaning of the legal issue, handle the issue of the task result,"
        "and get the professional legal comment after reasonable analysis and judgment from different character perspective,"
        "such as police, person and judge."
    )
    args_schema: Type[LawMultiRoleCheckToolSchema] = LawMultiRoleCheckToolSchema
    goals: List[str] = []
    agent_execution_id: int = None
    agent_id: int = None
    permission_required: bool = False
    tool_response_manager: Optional[ToolResponseQueryManager] = None

    class Config:
        arbitrary_types_allowed = True

    def chat_response(self, text: str, issue: str,  prompt_file: str):
        try:
            prompt = PromptReader.read_tools_prompt(__file__, prompt_file)
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            prompt = prompt.replace("{issue}", issue)
            prompt = prompt.replace("{legal_text}", text)

            # if roles_check != None:
            #     prompt = prompt.replace("{police_text}", roles_check["police"])
            #     prompt = prompt.replace("{lawyer_text}", roles_check["lawyer"])
            #     prompt = prompt.replace("{people_text}", roles_check["people"])


            messages = [{"role": "system", "content": prompt}]
            result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)

            if 'error' in result and result['message'] is not None:
                ErrorHandler.handle_openai_errors(self.toolkit_config.session, self.agent_id, self.agent_execution_id,
                                                  result['message'])
            return result["content"]
        except Exception as e:
            logger.error(e)
            return f"Error generating text: {e}"

    def _execute(self, text: str, ):
        """
        Execute the MultiRole Check Tool.

        Args:
            input_text : The content that needs to be discussed.
            issue : The topic of discussion.

        Returns:
            the final analysis result.
        """
        issue = text
        last_tool_response = self.tool_response_manager.get_last_response("UniversalReflectionTool")
        if last_tool_response != None and last_tool_response != "":
            input_text = last_tool_response
        else:
            input_text = self.tool_response_manager.get_first_response()

        result_police = self.chat_response(issue, input_text, "policecheck.txt",)
        result_lawyer = self.chat_response(issue, input_text, "lawyercheck.txt",)
        result_people = self.chat_response(issue, input_text, "peoplecheck.txt",)

        result = (f"From the perspective of view of the police:\n{result_police}\n"
                  f"From the perspective of lawyer:\n{result_lawyer}\n"
                  f"From the perspective of people:\n{result_people}\n")

        # roles_check = {}
        # roles_check["police"] = result_police
        # roles_check["lawyer"] = result_lawyer
        # roles_check["people"] = result_people
        #
        # # final decision from judge
        # final_decision = self.chat_response(issue, text, "lawfinalcheck.txt", roles_check=roles_check)

        return result