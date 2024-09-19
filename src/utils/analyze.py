from typing import Dict, List

def invert_dict(d: Dict[str, str]) -> Dict[str, str]:
    """
    将`Dict[str, str]`类型的变量，进行键值互换。
    """
    return {v: k for k, v in d.items()}

def sort_dict_list(dict_list: List[dict], key_name: str):
    """
    将`List[dict]`类型的变量，按`dict`的`key`值进行排序。
    """
    sorted_list = sorted(dict_list, key=lambda x: x[key_name])
    return sorted_list

def merge_dict_lists(list1: List[dict], list2: List[dict]):
    """
    将两个所有包含的`dict`的`key`均相同的`List[dict]`进行合并。

    Note: `list2`优先级高于`list1`.
    """
    name_to_dict = {d["name"]: d for d in list1}
    for d in list2:
        if d["name"] in name_to_dict:
            name_to_dict[d["name"]]["time"] = d["time"]
        else:
            list1.append(d)
    return list1