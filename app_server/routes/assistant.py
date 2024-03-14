import json
import re
import threading
import time
from http import HTTPStatus

from flask import request, jsonify, Blueprint

from app_server.models.agent import DifyAgent
from app_server.tools.dify.dify_request import Make_dify_request
from app_server.tools.file_tools import read_json_from_file
from feishu_utils.feishu_reply_message import reply_msg_text

assistant_bp = Blueprint('assistant', __name__)


@assistant_bp.route('/assistant/main', methods=['POST'])
def assistant_main():
    try:
        data = request.get_json()
        input_data = data.get('content')
        if not input_data:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "input is empty."})
        msg_id = data.get('message_id')
        if not msg_id:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "msg_id is empty."})

        # 开一个线程 处理消息
        t = threading.Thread(target=assistant_input_process, args=(input_data, msg_id,))  # 传入参数 一定要带着逗号，不然会报错
        t.start()
        # assistant_input_process(input_data)
        return jsonify({"code": HTTPStatus.OK, "msg": "success"})

    except Exception as e:
        print('start agent error:', str(e))
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


# 处理用户输入
def assistant_input_process(input_data, msg_id):
    # 使用read_json函数读取JSON文件
    config_json_data = read_json_from_file("./agents_config.json")
    api_key = config_json_data['main_api_key']
    default_api_key = config_json_data['default_api_key']
    tools, tools_list = generate_parameters(config_json_data)
    print('tools:', tools)
    print('tools_list:', tools_list)

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
        return
    # print('response:', response.text)
    json_data = response.json()
    action, action_input = extract_action_info(json_data.get('answer'))
    # 获取分类
    print('action:', action)
    print('action_input:', action_input)

    response_mode = 'blocking'
    mode = 'chat'
    api_key = default_api_key

    agents_list = get_all_agents(config_json_data)
    payload = {}
    # 根据分类进行处理
    for agent in agents_list:
        if action == agent.name:
            # 找到匹配的 agent
            print(f'start agent: {agent.name}')
            response_mode = agent.response_mode
            mode = agent.mode
            api_key = agent.api_key
            payload = {
                "inputs": {},
                "query": action_input,
                "response_mode": response_mode,
                "user": "123456"
            }
            break
    if payload == {}:
        # 如果没有找到匹配的 agent,可以执行默认操作或输出错误信息
        # print(f"No matching agent found for action: {action}")
        print('start default agent')
        payload = {
            "inputs": {},
            "query": input_data,
            "response_mode": response_mode,
            "user": "123456"
        }

    response = Make_dify_request(api_key, payload, mode=mode)
    # 这里需要根据response_mode来判断处理方式
    if response_mode == 'streaming':
        print('response_mode:', response_mode)
        final_answer = response_streaming(response)
    else:
        if response.status_code != HTTPStatus.OK:
            print('response status_code:', response.status_code)
            print('response:', response.text)
        json_data = response.json()
        final_answer = json_data.get('answer')
    print('response answer:', final_answer)
    reply_msg_text(msg_id, final_answer)


def response_streaming(response):
    content = ''
    incomplete_chunk = b''  # 保存上一个不完整的数据块
    for chunk in response.iter_content(chunk_size=1024):
        # 合并上一个不完整的数据块和当前数据块
        # print(chunk)
        data = incomplete_chunk + chunk
        try:
            # 将字节字符串解码为普通字符串
            decoded_data = chunk.decode('utf-8')

            # 从字符串中提取 JSON 部分
            json_data_start = decoded_data.find('{')
            json_data_end = decoded_data.rfind('}') + 1
            json_data = decoded_data[json_data_start:json_data_end]

            # 解析 JSON 数据
            parsed_data = json.loads(json_data)

            # 获取 answer
            answer = parsed_data.get('answer', '')
            if answer:
                content += answer
        except json.decoder.JSONDecodeError:
            # 如果解码失败，说明数据块不完整，保存当前数据块以备下一次使用
            incomplete_chunk = data
        else:
            # 如果解码成功，说明数据块完整，清空不完整的数据块
            incomplete_chunk = b''
    print('content:', content)
    return content


# 获取全部工具详情
def get_all_agents(json_data):
    agents_list = []

    for agent in json_data.get("dify_agents", []):
        # print('agent:', agent)
        name = agent.get("name", "")
        introduction = agent.get("introduction", "")
        api_key = agent.get("api_key", "")
        response_mode = agent.get("response_mode", "")
        mode = agent.get("mode", "")

        dify_agent = DifyAgent(name, introduction, api_key, response_mode, mode)
        agents_list.append(dify_agent)

    return agents_list


# 生成tools参数
def generate_parameters(json_data):
    tools = ""
    tools_list = ""

    for agent in json_data.get("dify_agents", []):
        name = agent.get("name")
        introduction = agent.get("introduction")

        tools += f"{name}:{introduction}\n"
        tools_list += f"{name},"
    return tools, str(tools_list)


# 从JSON文件中读取action数据
def extract_action_info(text):
    print('action info')
    print(text)
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
