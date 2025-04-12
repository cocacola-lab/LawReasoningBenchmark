import os
import json
from typing import Type, Optional
from pathlib import Path

from tfagent.helper.resource_helper import ResourceHelper
from tfagent.models.agent import Agent
from tfagent.models.agent_execution import AgentExecution
from tfagent.resource_manager.file_manager import FileManager
from tfagent.tools.base_tool import BaseTool

from pydantic import BaseModel, Field



class EvidKnowledgeSchema(BaseModel):
    """Input for EvidKnowledgeTool."""
    query: str = Field(..., description="The query for retrieving the relevant provision ")


class EvidKnowledgeTool(BaseTool):
    """
    search the relevant evidence knowledge

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "Criminal Evidence Knowledge"
    agent_id: int = None
    agent_execution_id: int = None
    args_schema: Type[BaseModel] = EvidKnowledgeSchema
    description: str = "Retrieve knowledge about criminal evidence"
    resource_manager: Optional[FileManager] = None

    def _execute(self, query: str):
        """
        Execute the tool.

        Args:
            query : The query for retrieving the relevant provision .

        Returns:
            The relevant provision.
        """

        file_path = str(Path(__file__).resolve().parent) + "/knowledge/evid.txt"
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return content
