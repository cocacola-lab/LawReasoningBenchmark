
def segdata(data, max_input_words):
    case_split = {}
    case_split['id'] = data['id']
    case_segments = []
    start = 0
    end = 0
    seg_cnt = 0
    item = ""

    for sent in data["Case_info"].split("。"):
        if len(item) > max_input_words:
            case_segments.append({
                "seg": seg_cnt,
                "start": start,
                "end": end,
                "case_info": item,
                 })

            seg_cnt += 1
            start = end + 1
            item = ""

        item += sent
        item += "。"
        end += 1

    if item != "":
        case_segments.append({
            "seg": seg_cnt,
            "start": start,
            "end": end,
            "case_info": item,
            }
        )

    case_split["case_segments"] = case_segments
    # print(case_split)
    return case_split