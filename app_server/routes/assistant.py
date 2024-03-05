import json
import re
import threading
import time
from http import HTTPStatus

from flask import request, jsonify, Blueprint

from app_server.tools.dify.dify_request import Make_dify_request
from app_server.tools.file_tools import read_json_from_file

assistant_bp = Blueprint('assistant', __name__)


@assistant_bp.route('/assistant/main', methods=['POST'])
def assistant_main():
    try:
        data = request.get_json()
        input_data = data.get('input')
        if not input_data:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "input is empty."})

        # 开一个线程 处理消息
        t = threading.Thread(target=assistant_input_process, args=(input_data,))  # 传入参数
        t.start()

        # assistant_input_process(input_data)
        return jsonify({"code": HTTPStatus.OK, "msg": "success"})

    except Exception as e:
        print('start agent error:', str(e))
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


# 处理用户输入
def assistant_input_process(input_data):
    # 使用read_json函数读取JSON文件
    json_data = read_json_from_file("./agents_config.json")
    api_key = json_data['main_api_key']
    default_api_key = json_data['default_api_key']
    tools, tools_list = generate_parameters(json_data)

    # 构造请求参数
    payload = {
        "inputs": {"query": input_data, "tools": tools, "tools_list": tools_list},
        "response_mode": "blocking",
        "user": "123456"
    }
    # 请求参数分类
    response = Make_dify_request(api_key, payload)
    if response.status_code != HTTPStatus.OK:
        print('response status_code:', response.status_code)
        print('response:', response.text)
        return jsonify({"code": response.status_code, "msg": response.text})
    print('response:', response.text)
    json_data = response.json()
    action, action_input = extract_action_info(json_data.get('answer'))
    # 获取分类
    print('action:', action)
    print('action_input:', action_input)

    # 根据分类进行处理
    if action == 'default':
        print('start default')
        payload = {
            "inputs": {},
            "query": input_data,
            "response_mode": "blocking",
            "user": "123456"
        }

        response = Make_dify_request(default_api_key, payload, mode='chat')
        if response.status_code != HTTPStatus.OK:
            print('response status_code:', response.status_code)
            print('response:', response.text)
            return jsonify({"code": response.status_code, "msg": response.text})
        json_data = response.json()
        print('response answer:', json_data.get('answer'))


def generate_parameters(json_data):
    tools = ""
    tools_list = ""

    for agent in json_data.get("dify_agents", []):
        name = agent.get("name")
        introduction = agent.get("introduction")

        tools += f"{name}:{introduction}\n"
        tools_list += f"{name},"
    return tools, str(tools_list)


def extract_action_info(text):
    try:
        # Use regular expressions to find the action and action_input values
        match = re.search(r'"action": "(.*?)",\s*"action_input": "(.*?)"', text)

        if match:
            action = match.group(1)
            action_input = match.group(2)
            return action, action_input
        else:
            print("No match found.")
            return None, None

    except Exception as e:
        print(f"Error: {e}")
        return None, None


# test threading 测试多线程
@assistant_bp.route('/assistant/main', methods=['GET'])
def assistant_main_test():
    try:
        t = threading.Thread(target=funB)
        t.start()
        return jsonify({"code": HTTPStatus.OK, "msg": "success"})

    except Exception as e:
        print('start agent error:', str(e))
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


def funB():
    print("funB started")
    time.sleep(10)
    print("funB completed")
