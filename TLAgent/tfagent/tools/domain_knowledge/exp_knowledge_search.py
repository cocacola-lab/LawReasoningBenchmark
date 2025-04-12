from typing import Type, Optional
from pathlib import Path

from tfagent.resource_manager.file_manager import FileManager
from tfagent.tools.base_tool import BaseTool

from pydantic import BaseModel, Field


class ExpKnowledgeSchema(BaseModel):
    pass
    """Input for FinalKnowledgeTool."""
    # query: str = Field(..., description="The query for retrieving the relevant provision ")


class ExpKnowledgeTool(BaseTool):
    """
    search the relevant evid knowledge

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "Human Experience Knowledge"
    agent_id: int = None
    agent_execution_id: int = None
    args_schema: Type[BaseModel] = ExpKnowledgeSchema
    description: str = "Retrieve knowledge about human experience knowledge"
    resource_manager: Optional[FileManager] = None

    def _execute(self, query: str):
        """
        Execute the tool.

        Args:
            query : The query for retrieving the relevant provision .

        Returns:
            The relevant provision.
        """

        file_path = str(Path(__file__).resolve().parent) + "/knowledge/exp.txt"
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return content