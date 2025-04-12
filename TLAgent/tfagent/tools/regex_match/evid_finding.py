import re


from typing import Type, Optional, List, Union

from pydantic import BaseModel, Field

from tfagent.tools.base_tool import BaseTool
from tfagent.tools.tool_response_query_manager import ToolResponseQueryManager

from tfagent.lib.logger import logger

class EvidFindingSchema(BaseModel):
    """Input for FactFindingTool."""
    text: str = Field(..., description="legal document text")


class EvidFinding(BaseTool):
    """
    Thinking tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name = "EvidFindingTool"
    description = (
        "Intelligent problem-solving assistant that extracting fact from legal documents through regex matching."
    )
    args_schema: Type[EvidFindingSchema] = EvidFindingSchema
    goals: List[str] = []
    agent_execution_id: int = None
    agent_id: int = None
    permission_required: bool = False
    tool_response_manager: Optional[ToolResponseQueryManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, text: str) -> Union[List[str], str]:
        """
            Execute the EvidFinding tool.

            Args:
                task_description : The task description.

            Returns:
                evidence location pair  list
            """
        EV_START1 = ["上述事实", "上述犯罪事实", "上述指控", "下列证据"]
        EV_START2 = ["证据有", "证言证明"]
        EV_START = [EV_START1, EV_START2]

        EV_END1 = ["以上证据", "上述证据"]
        EV_END2 = ["本院认为"]
        EV_END = [EV_END1, EV_END2]

        EV_KEYS = ["　一、", "　二、", "　三、", "　四、", "　五、", "　六、", "　七、", "　八、", "　九、", "　十、", \
                   "　十一、", "　十二、", "　十三、", "　十四、", "　十五、", "　十六、", "　十七、", "　十八、", "　十九、", "　二十、" \
                                                                                                             "（一）",
                   "（二）", "（三）", "（四）", "（五）", "（六）", "（七）", "（八）", "（九）", "（十）", "（十一）" \
                                                                                           "（十二）", "（十三）", "（十四）",
                   "（十五）", "（十六）", "（十七）", "（十八）", "（十九）", "（二十）"
                   ]
        try:
            text = text.replace(" ", "")
            sents = text.split("。")
            # 证据开始
            start = -1
            end = -1

            less_range_start = 0
            less_range_end = 0

            for i_e, ev_s in enumerate(EV_START):
                for i_t, sent in enumerate(sents):
                    for key in ev_s:
                        if (key in sent):
                            start = i_t
                            break
                    if (start != -1):
                        break
                if (start != -1):
                    break

                less_range_start = -1  # 没有找到准确的开始

            for ev_e in EV_END:
                for i_t, sent in enumerate(sents):
                    for key in ev_e:
                        if (key in sent):
                            end = i_t
                            break
                    if (end != -1):
                        break
                if (end != -1):
                    break

                less_range_end = -1  # 没有找到准确的结尾

            if (start != 0 and end == -1):
                end = start + 100
            if (end != 0 and start == -1):
                start = end - 100

            if (less_range_start == -1 and less_range_end != -1):
                less_range_start, less_range_end = end - 50, end
            elif (less_range_start != -1 and less_range_end == -1):
                less_range_start, less_range_end = start, start + 50
            elif (less_range_start != -1 and less_range_end != -1):
                less_range_start, less_range_end = start, end

            end -= 1

            if (start < 0):
                start = 0
            if (end < 0):
                end = len(sents) - 1

            #     start = 0
            #     end = len(sents)-1
            is_first = True
            evs_loc = []
            ev_start = start
            for i_s, sent in enumerate(sents[start:end + 1]):
                now = start + i_s
                has_key = False
                for key in EV_KEYS:
                    if (key in sent):
                        has_key = True
                if (re.search(r'\d+\.(?!\d)', sent) or re.search(r'\d+．(?!\d)', sent) or re.search(r'（\d+）',
                                                                                                   sent) or re.search(
                        r'　\d+、(?!\d)', sent)
                        or re.search(r'\s+[一二三四五六七八九十零壹贰叁肆伍陆柒捌玖拾]+、', sent) \
                        or re.search(r'（[一二三四五六七八九十零壹贰叁肆伍陆柒捌玖拾]+）', sent)):
                    if (is_first):
                        ev_start = now
                        is_first = False
                        continue
                    evs_loc.append([ev_start, now - 1])
                    ev_start = now

            is_first = True
            if (len(evs_loc) == 0):
                start = 0
                ev_start = start
                for i_s, sent in enumerate(sents):
                    now = start + i_s
                    if (re.match(r'^\s*\d+\.(?!\d)', sent) or re.match(r'^\s*\d+．(?!\d)', sent) \
                            or re.match(r'^\s*（\d+）', sent) or re.match(r'^\s*\d+、', sent) \
                            or re.match(r'^\s*\(\d+\)', sent) or re.search(
                                r'\s+[一二三四五六七八九十零壹贰叁肆伍陆柒捌玖拾]+、',
                                sent) \
                            or re.search(r'\s*（[一二三四五六七八九十零壹贰叁肆伍陆柒捌玖拾]+）', sent)):
                        if (is_first):
                            ev_start = now
                            is_first = False
                            continue
                        evs_loc.append([ev_start, now - 1])
                        ev_start = now

            return evs_loc


        except Exception as e:
            logger.error(e)
            return f"Error find fact from text: {e}"
