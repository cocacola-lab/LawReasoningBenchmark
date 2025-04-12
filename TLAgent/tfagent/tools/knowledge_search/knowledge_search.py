from tfagent.models.agent_config import AgentConfiguration

from tfagent.models.knowledges import Knowledges
from tfagent.models.vector_db_indices import VectordbIndices
from tfagent.models.vector_dbs import Vectordbs
from tfagent.models.vector_db_configs import VectordbConfigs
from tfagent.models.toolkit import Toolkit
from tfagent.vector_store.vector_factory import VectorFactory
from tfagent.models.configuration import Configuration
from tfagent.jobs.agent_executor import AgentExecutor

from typing import Any, Type, List
from pydantic import BaseModel, Field

from tfagent.tools.base_tool import BaseTool

# from tfagent.tools.file.read_file import ReadFileTool


class KnowledgeSearchSchema(BaseModel):
    query: str = Field(..., description="The query to search required from knowledge search")


class KnowledgeSearchTool(BaseTool):
    name: str = "Knowledge Search"
    args_schema: Type[BaseModel] = KnowledgeSearchSchema
    agent_id: int = None
    description = (
        "A tool for performing a Knowledge search on knowledge base which might have knowledge of the task you are pursuing."
        "To find relevant info, use this tool first before using other tools."
        "If you don't find sufficient info using Knowledge tool, you may use other tools."
        "If a question is being asked, responding with context from info returned by knowledge tool is prefered."
        "Input should be a search query."
    )

    def _execute(self, query: str):
        session = self.toolkit_config.session
        knowledge_id = session.query(AgentConfiguration).filter(AgentConfiguration.agent_id == self.agent_id, AgentConfiguration.key == "knowledge").first().value
        knowledge = Knowledges.get_knowledge_from_id(session, knowledge_id)
        if knowledge is None:
            return "Selected Knowledge not found"
        vector_db_index = VectordbIndices.get_vector_index_from_id(session, knowledge.vector_db_index_id)
        vector_db = Vectordbs.get_vector_db_from_id(session, vector_db_index.vector_db_id)
        db_creds = VectordbConfigs.get_vector_db_config_from_db_id(session, vector_db.id)

        # TODO 修改下面三行代码使其通用 将apikey以及embeddingmodel添加到vectordb configs中。
        model_api_key = self.get_tool_config('OPENAI_API_KEY')

        if "embedding_name" in db_creds:
            model_name = db_creds['embedding_name']
        else:
            model_name = None

        if "embedding_type" in db_creds:
            model_source = db_creds['embedding_name']
        else:
            model_source = 'OpenAI'

        embedding_model = AgentExecutor.get_embedding(model_source, model_api_key)

        try:
            if vector_db_index.state == "Custom":
                filters = None
            if vector_db_index.state == "Marketplace":
                filters = {"knowledge_name": knowledge.name}
            vector_db_storage = VectorFactory.build_vector_storage(vector_db.db_type, vector_db_index.name, embedding_model, **db_creds)
            search_result = vector_db_storage.get_matching_text(query, metadata=filters)
            return f"Result: \n{search_result['search_res']}"
        except Exception as err:
            return f"Error fetching text: {err}"
        