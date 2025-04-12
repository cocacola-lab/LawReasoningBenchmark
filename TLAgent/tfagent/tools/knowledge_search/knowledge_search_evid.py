import json

from tfagent.models.agent_config import AgentConfiguration

from tfagent.models.knowledges import Knowledges
from tfagent.llms.base_llm import BaseLlm
from tfagent.models.vector_db_indices import VectordbIndices
from tfagent.models.vector_dbs import Vectordbs
from tfagent.models.vector_db_configs import VectordbConfigs
from tfagent.vector_store.vector_factory import VectorFactory
from tfagent.models.configuration import Configuration
from tfagent.jobs.agent_executor import AgentExecutor
from tfagent.helper.json_cleaner import JsonCleaner
from tfagent.helper.error_handler import ErrorHandler

from typing import Any, Type, List, Union, Optional
from pydantic import BaseModel, Field

from tfagent.tools.base_tool import BaseTool
from tfagent.tools.tool_response_query_manager import ToolResponseQueryManager


class EvidKnowledgeSearchSchema(BaseModel):
    query: Union[str, List[str]] = Field(..., description="The query for evidence search ")


class EvidKnowledgeSearchTool(BaseTool):
    name: str = "Knowledge Search (Criminal Evidence)"
    args_schema: Type[BaseModel] = EvidKnowledgeSearchSchema
    agent_id: int = None
    agent_execution_id: int = None
    llm: Optional[BaseLlm] = None
    description = ("This tool can be called to find criminal evidence texts similar to the query and further verify"
        " whether the input query belongs to criminal evidence, use this tool first before using other tools is recommended."
        "Input should be a search query for the predicted criminal evidence or list of query.")

    tool_response_manager: Optional[ToolResponseQueryManager] = None


    def handle_search_res(self, search_result):
        temp_res = ""
        for i, doc in enumerate(search_result['documents']):
            temp_res += f"相似文本{i + 1}:\n {doc.text_content}\n"
            if doc.metadata["type"] == "evidence":
                if doc.metadata["is_type"]:
                    temp_res += "该段相似文本属于犯罪证据。\n\n"
                else:
                    temp_res += "该段相似文本不属于犯罪证据。\n\n"
            else:
                temp_res = "数据库调用错误，该向量库与犯罪证据无关。\n"
                break
        return temp_res

    def check_evidence(self, q, simres: str):
        prompt = "请根据得到的相似文本，判断输入文本是否属于犯罪证据。如果相似文本中一半以上不属于犯罪证据，那么输入文本则不属于犯罪证据。最后如果输入文本属于犯罪证据请返回\"该文本属于犯罪证据。\"，如果不属于犯罪证据请返回\"该文本不属于犯罪证据。\"\n"
        prompt += f"输入文本：\n{q}\n\n"
        prompt += f"相似文本检索结果：\n{simres}\n\n"

        messages = [{"role": "system", "content": prompt}]
        result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)

        if 'error' in result and result['message'] is not None:
            ErrorHandler.handle_openai_errors(self.toolkit_config.session, self.agent_id, self.agent_execution_id,
                                              result['message'])

        if "该文本属于犯罪证据" in result["content"]:
            return q
        else:
            return "该文本不属于犯罪证据。"


    def _execute(self, query: Union[str, List[str]]):
        session = self.toolkit_config.session
        knowledge_id = session.query(AgentConfiguration).filter(AgentConfiguration.agent_id == self.agent_id,
                                                                AgentConfiguration.key == "knowledge").first().value
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
            model_source = db_creds['embedding_type']
        else:
            model_source = 'OpenAI'

        embedding_model = AgentExecutor.get_embedding(model_source, model_api_key, model_name)

        if vector_db_index.state == "Custom":
            filters = None
        if vector_db_index.state == "Marketplace":
            filters = {"knowledge_name": knowledge.name}
        vector_db_storage = VectorFactory.build_vector_storage(vector_db.db_type, vector_db_index.name,
                                                               embedding_model, **db_creds)

        try:
            evid_results =  {"evidence": []}
            final_evid_count = 0
            # 找到最后的思考结果，然后通过相似文本验证是否为犯罪证据
            last_tool_response = self.tool_response_manager.get_last_response("UniversalReflectionTool")
            if last_tool_response != None and last_tool_response != "":
                evids = JsonCleaner.extract_json_section(last_tool_response)
                evids = json.loads(evids)
                new_query = []
                for evid in evids["evidence"]:
                    new_query.append(evid["text"])
                query = new_query
            else:
                query = []

            if isinstance(query, list):
                for i, q in enumerate(query):
                    search_result = vector_db_storage.get_matching_text(q, 3, metadata=filters)
                    temp_res = self.handle_search_res(search_result)
                    if temp_res != "":
                        res = self.check_evidence(q, temp_res)
                    else:
                        res = ""

                    if res != "该文本不属于犯罪证据。":
                        evid_results["evidence"].append(
                            {"id": final_evid_count, "text": res}
                        )
                        final_evid_count += 1

            # elif isinstance(query, str):
            #     search_result = vector_db_storage.get_matching_text(query, 3, metadata=filters)
            #     temp_res = self.handle_search_res(search_result)
            #     if temp_res != "":
            #         res = self.check_evidence(query, temp_res)
            #     else:
            #         res = ""
            #
            #     if res != "该文本不属于犯罪证据。":
            #         evid_results["evidence"].append(
            #             {"id": final_evid_count, "text": res}
            #         )
            #         final_evid_count += 1
            # else:
            #     evid_results = {"Error": "No Results"}

            evid_results = json.dumps(evid_results, ensure_ascii=False)
        except Exception as err:
            return f"Error fetching text: {err}"

        return f"Result: \n{evid_results}"
