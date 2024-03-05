import json


def read_json_from_file(file_path):
    if not file_path:
        return
    with open(file_path, 'r') as file:
        # 从文件中加载JSON数据
        data = json.load(file)
    return data
