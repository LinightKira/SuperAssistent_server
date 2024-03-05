import json

from flask import stream_with_context, Response

from app_server.tools.dify.dify_request import Make_dify_request

response_mode = 'blocking'  # streaming / blocking
# payload = {
#     'inputs': {'query': "多啦a梦为什么喜欢帮助其他人呢？"},
#     "response_mode": response_mode,
#     "user": "123456"
# }
# key="app-Ve0Hvzc0IaKJ8XOa1HMYV5l6"
key = 'app-hp8hKD1ni8Dnw9eKU7YzcZP2'
payload = {
    'inputs': {'query': '飞驰人生2',
               'tools': 'Calculator:Useful for when you need to answer questions about math.\nWikipedia:A wrapper around Wikipedia. Useful for when you need to answer general questions about people, places, companies, facts, historical events, or other subjects. Input should be a search query.\n',
               'tools_list': 'Calculator,Wikipedia,'},
    'response_mode': response_mode,
    'user': '123456'}

response = Make_dify_request(key, payload)
if response_mode == 'streaming':
    content = ''
    incomplete_chunk = b''  # 保存上一个不完整的数据块
    for chunk in response.iter_content(chunk_size=1024):
        # 合并上一个不完整的数据块和当前数据块
        print(chunk)
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
else:
    print(response.status_code)
    print(response.json())
