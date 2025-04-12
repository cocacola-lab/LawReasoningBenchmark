from typing import Type, Optional, List, Union

from pydantic import BaseModel, Field

from tfagent.tools.base_tool import BaseTool
from tfagent.tools.tool_response_query_manager import ToolResponseQueryManager

from tfagent.lib.logger import logger

class FactFindingSchema(BaseModel):
    """Input for FactFindingTool."""
    text: str = Field(..., description="legal document text")


class FactFinding(BaseTool):
    """
    Fact Finding tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name = "FactFindingTool"
    description = (
        "Intelligent problem-solving assistant that extracting fact from legal documents through regex matching."
    )
    args_schema: Type[FactFindingSchema] = FactFindingSchema
    goals: List[str] = []
    agent_execution_id: int = None
    agent_id: int = None
    permission_required: bool = False
    tool_response_manager: Optional[ToolResponseQueryManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, text: str) -> Union[List[str], str]:
        """
        Execute the FactFinding tool.

        Args:
            text : legal document text

        Returns:
            fact list or fact id list
        """
        KEYS = ["审理查明","经查","经鉴定","另查明","具体事实","确认如下事实","公诉机关认为"]
        KEYS2 = ["检察院指控","检察院起诉","公诉机关指控：","经查","经鉴定","另查明","具体事实","确认如下事实"]
        KEYS3 = ["审理查明","经鉴定","另查明","具体事实","确认如下事实"]
        KEYS4 = ["检察院指控","经鉴定","经查","另查明","具体事实","确认如下事实","公诉机关认为"]
        EV_START1 = ["上述事实", "上述犯罪事实", "上述指控", "下列证据"]
        try:
            # TODO huiqi
            # [CODE]
            text = text.replace(" ","")
            sents = text.split("。")
            inters = set()
            shenlichaming = False
            for i_t, sent in enumerate(sents):
                if ("本案经合议庭评议认为" in sent):
                    inters.add(i_t)
                for k in KEYS3:
                    if (k in sent):
                        if (k == "审理查明" and "审理查明的" not in sent):
                            for m in range(i_t, i_t + 14):
                                if (m >= len(sents)):
                                    break
                                bk = False
                                if (m >= i_t + 2):
                                    for key in EV_START1:
                                        if (key in sents[m]):
                                            bk = True
                                if (bk):
                                    break
                                if ("内容已隐藏，请自行生成最终认定事实" in sents[m]):
                                    break
                                inters.add(m)

                            shenlichaming = True
                        elif (shenlichaming and "事实" in k):
                            for m in range(i_t, i_t + 4):
                                if (m >= len(sents)):
                                    break
                                bk = False
                                for key in EV_START1:
                                    if (key in sents[m]):
                                        bk = True
                                if (bk):
                                    break
                                inters.add(m)
                        elif (shenlichaming):
                            for m in range(i_t, i_t + 1):
                                if (m >= len(sents)):
                                    break
                                bk = False
                                for key in EV_START1:
                                    if (key in sents[m]):
                                        bk = True
                                if (bk):
                                    break
                                inters.add(m)

            true_inters = list(inters)

            text = ""
            inters_list = sorted(list(inters))
            for i in inters_list:
                if (i > len(sents) - 1):
                    continue
                if ("内容已隐藏，请自行生成最终认定事实" in sents[i]):
                    continue
                text += sents[i] + "。"

            if (len(text) < 700):
                for i_t, sent in enumerate(sents):
                    if ("现已审理终结" in sent):
                        for m in range(i_t + 1, i_t + 20):
                            if (m >= len(sents)):
                                break
                            inters.add(m)
                    for k in KEYS4:
                        if (k in sent):
                            if ("事实" in k):
                                for m in range(i_t, i_t + 4):
                                    if (m >= len(sents)):
                                        break
                                    inters.add(m)
                            else:
                                for m in range(i_t, i_t + 1):
                                    if (m >= len(sents)):
                                        break
                                    inters.add(m)

            dif = sorted(list(inters.difference(set(inters_list))))

            temp_text = ""
            choose = []
            for i in dif:
                if (i > len(sents) - 1):
                    continue
                if ("内容已隐藏，请自行生成最终认定事实" in sents[i]):
                    continue
                temp_text += sents[i] + "。"
                choose.append(i)

            inters_list.extend(choose)
            inters_list = sorted(list(set(inters_list)))

            text = ""
            for i in inters_list:
                if (i > len(sents) - 1):
                    continue
                if ("内容已隐藏，请自行生成最终认定事实" in sents[i]):
                    continue
                text += sents[i] + "。"
                if (len(text) > 2048):
                    break

            if (len(true_inters) < 1):
                true_inters = inters_list

            return true_inters  # inter fact id list

        except Exception as e:
            logger.error(e)
            return f"Error find fact from text: {e}"
