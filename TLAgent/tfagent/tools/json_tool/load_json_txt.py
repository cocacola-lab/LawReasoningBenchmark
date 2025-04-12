import os
import json
from typing import Type, Optional


from tfagent.helper.resource_helper import ResourceHelper
from tfagent.models.agent import Agent
from tfagent.models.agent_execution import AgentExecution
from tfagent.resource_manager.file_manager import FileManager
from tfagent.tools.base_tool import BaseTool

from pydantic import BaseModel, Field



class LoadJsonTxtSchema(BaseModel):
    """Input for LoadJsonTxtTool."""
    file_name: str = Field(..., description="The name of the json file")


class LoadJsonTxtTool(BaseTool):
    """
    Load json content from files

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "Load Json Txt"
    agent_id: int = None
    agent_execution_id: int = None
    args_schema: Type[BaseModel] = LoadJsonTxtSchema
    description: str = "Load json content from file"
    resource_manager: Optional[FileManager] = None

    def _execute(self, file_name: str):
        """
        Execute the loadjson text tool.

        Args:
            file_name : The name of the file to read.

        Returns:
            The json object (list or dict)
        """

        final_path = ResourceHelper.get_agent_read_resource_path(file_name, agent=Agent.get_agent_from_id(
            session=self.toolkit_config.session, agent_id=self.agent_id), agent_execution=AgentExecution
                                                                 .get_agent_execution_from_id(session=self
                                                                                              .toolkit_config.session,
                                                                                              agent_execution_id=self
                                                                                              .agent_execution_id))

        if final_path is None or not os.path.exists(final_path):
            raise FileNotFoundError(f"File '{file_name}' not found.")

        if not final_path.split('/')[-1].lower().endswith('.json'):
            raise FileNotFoundError(f"File '{file_name}' suffix is not of type JSON.")

        with open(final_path,  'r', encoding="utf-8") as f:
            json_txt = f.read()

        try:
            json_obj = json.loads(json_txt)
            return json_obj
        except json.JSONDecodeError as e:
            raise ValueError("The input string is not valid JSON") from e
