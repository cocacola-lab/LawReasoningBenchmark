import json
from typing import Type, Optional

from pydantic import BaseModel, Field

# from tfagent.helper.s3_helper import upload_to_s3
from tfagent.resource_manager.file_manager import FileManager
from tfagent.tools.base_tool import BaseTool


# from tfagent.helper.s3_helper import upload_to_s3


class ReadValFromJsonItemSchema(BaseModel):
    json_content: str = Field(..., description="json content")
    seleted_key: str = Field(..., description="The key to get")


class ReadValFromJsonItem(BaseTool):
    """
    The tool of read value from json item

    Attributes:
        name : The name.
        description : The description.
        agent_id: The agent id.
        args_schema : The args schema.
        resource_manager: File resource manager.
    """
    name: str = "Read Value From Json Item"
    args_schema: Type[BaseModel] = ReadValFromJsonItemSchema
    description: str = " The tool of read value from json item"
    agent_id: int = None
    resource_manager: Optional[FileManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, selected_key: str, json_content: str):
        """
        Execute the tool of read value from json item.

        Args:
            selected_key: The selected key.
            json_content: The content of the json item.

        Returns:
            The value from json item.
        """

        try:
            json_item = json.loads(json_content)
        except json.JSONDecodeError as e:
            raise ValueError("The input string is not valid JSON") from e

        if not isinstance(json_item, dict):
            raise ValueError("The input string is not json item")

        content = json_item.get(selected_key, "None")

        return content
